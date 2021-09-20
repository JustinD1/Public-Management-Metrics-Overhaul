from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.forms import modelformset_factory
from django.utils import timezone

from OPR2.models import WeekSales, YearSales, OPRSave
from home.models import FileDate, StoreSave
from sales_comp.models import Comparisons, totalWeekTurnover
from sls.models import Profile
from .forms import ChangeBudget
from .functions import SetTableContentYear2Week
from scripts.BackendHandleOPR import mkSaterdayList, weeklyTotal

import datetime
import math

#Page to view how a department compares to this time last year: last 4 weeks and current week. And preveious week.
@login_required
def department_comparison(request,storeID):
    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)
    #Hard coded list that client wants to show by default
    showList = [
        "s0075",
        "s0078",
        "s0155",
        "s0156",
        "s0157",
        "s0228",
        "s0229",
        "s0230",
        "s0231",
        "s0232",
        "s0136",
        "c0637",
        "c0639",
        "c0640",
        "f3181",
        "f3182",
        "c0641",
        "c0642"
    ]
    compare2 = {}
    errorReport = []
    #pull from the database any other stores.
    store = StoreSave.objects.get(store=storeID)
    stores = StoreSave.objects.exclude(store=storeID)

    #pull from the database the latest date opr that was uploaded.
    latest_opr_date = FileDate.objects.filter(store=store, data_exists=True, file_type="OPR").latest('date')
    #Just check if the previous year has a corrosponding week if you go over 52 weeks. If not default back a week
    if latest_opr_date.week_number > 52 and not(FileDate.objects.get(
        store=store,
        file_type="OPR",
        financial_year=(latest_opr_date.financial_year - 1), week_number=latest_opr_date.week_number).exists()):
        errorReport.append("Current year has %s, weeks. No previous year data to compare too." % str(latest_opr_date.week_number))
        latest_opr_date = FileDate.objects.get( store=store, file_type="OPR", financial_year=(latest_opr_date.financial_year), week_number=52
        )

    # print(latest_opr_date)
    # print((latest_opr_date.date - datetime.timedelta(weeks=1)))
    compare2["lastYear"] = FileDate.objects.get(store=store, file_type="OPR", date__year=str(int(latest_opr_date.date.strftime("%Y")) - 1), week_number = latest_opr_date.week_number).date
    # print(compare2["lastYear"])
    compare2["lastWeek"] = FileDate.objects.get(store=store, file_type="OPR", date=(latest_opr_date.date + datetime.timedelta(weeks=-1))).date
    data_list = Comparisons.objects.filter(date=latest_opr_date).order_by("-pk")


    tableContent = []
    # print(latest_opr_date.pk)
    # print(data_list.count)
    for item in data_list:
        temp_dictionary = {}
        item_visable = False
        # print(" ")
        # print(item.week_sale.section_name.name.lower())
        # print(item.week_sale.section_name.name.lower().startswith("d"))
        # print(item.week_sale.section_name.name[:5])
        # print(item.week_sale.section_name.name[:5].lower() in showList)
        if item.week_sale.section_name.name.lower().startswith("d") or item.week_sale.section_name.name[:5].lower() in showList:
            item_visable = True


        temp_dictionary["name"] = item.week_sale.section_name.name
        # print(temp_dictionary["name"])
        temp_dictionary["data_level"] = item.week_sale.section_name.data_level
        # print(temp_dictionary["data_level"])
        temp_dictionary["visable"] = item_visable
        # print("Data Level: %d, show line: %s."%(temp_dictionary["data_level"],temp_dictionary["visable"]))
        temp_dictionary["current_sales"] = '{0:,.0f}'.format(item.week_sale.sale)
        temp_dictionary["current_ytdsales"] = '{0:,.0f}'.format(item.year_sale.sale)

        if (float(item.week_sale.sale) == 0. or float(item.percentage_sale_last_week) == 0.):
            temp_dictionary["lastYear_ytdsales_diff"] = "-"
            temp_dictionary["lastYear_ytdsales_diffPrec"] = "-"
        else:
            temp_dictionary["lastYear_ytdsales_diff"] = '{0:,.0f}'.format(float(item.percentage_sale_last_week)*(float(item.week_sale.sale)/(float(item.percentage_sale_last_week) + 1.)))
            temp_dictionary["lastYear_ytdsales_diffPrec"] = '{0:.2f}'.format((float(item.percentage_sale_last_week))*100.)

        if (float(item.week_sale.sale) == 0. or float(item.percentage_sale_last_year) == 0.):
            temp_dictionary["lastYear_ytdsales"] = "-"
            temp_dictionary["this_week_last_year_ytdsale_diff"] = "-"
            temp_dictionary["this_week_last_year_ytdsale_diffPrec"] = "-"
        else:
            temp_dictionary["lastYear_ytdsales"] = '{0:,.0f}'.format(float(item.year_sale.sale) / (float(item.percentage_sale_year2date) + 1.) )
            temp_dictionary["this_week_last_year_ytdsale_diffPrec"] = '{0:.2f}'.format(float(item.percentage_sale_year2date)*100.)
            temp_dictionary["this_week_last_year_ytdsale_diff"] = '{0:,.0f}'.format(float(item.percentage_sale_year2date)*(float(item.year_sale.sale)/(float(item.percentage_sale_year2date) + 1.)))

        if (float(item.week_sale.sale) == 0. or float(item.percentage_sale_last_year) == 0.):
            temp_dictionary["lastYear_sales"] = "-"
            temp_dictionary["this_week_last_year_sale_diff"] = "-"
            temp_dictionary["this_week_last_year_sale_diffPrec"] = "-"
        else:
            temp_dictionary["lastYear_sales"] = '{0:,.0f}'.format(float(item.week_sale.sale) / (float(item.percentage_sale_last_year) + 1.) )
            temp_dictionary["this_week_last_year_sale_diffPrec"] = '{0:.2f}%'.format(float(item.percentage_sale_last_year)*100.)
            temp_dictionary["this_week_last_year_sale_diff"] = '{0:,.0f}'.format(float(item.percentage_sale_last_year)*(float(item.week_sale.sale)/(float(item.percentage_sale_last_year) + 1.)))

        temp_dictionary["sale_last_4_weeks"] = '{0:,.0f}'.format(item.sum_last_4_weeks_sale)

        if (float(item.sum_last_4_weeks_sale) == 0. or float(item.percentage_sale_last_year_4_weeks) == 0.0):
            temp_dictionary["corrosponding_4_weeks_last_year_diff"] = "-"
            temp_dictionary["corrosponding_4_weeks_last_year_diffPrec"] = "-"
        else:
            temp_dictionary["corrosponding_4_weeks_last_year_diffPrec"] = '{0:.2f}'.format(float(item.percentage_sale_last_year_4_weeks)*100.)
            temp_dictionary["corrosponding_4_weeks_last_year_diff"] = '{0:,.0f}'.format(float(item.percentage_sale_last_year_4_weeks)*(float(item.sum_last_4_weeks_sale)/(float(item.percentage_sale_last_year_4_weeks) + 1.)))


        tableContent.append(temp_dictionary)
    contents = {'store':store, 'stores':stores, 'errorReport':errorReport, 'last_file':latest_opr_date, 'compare2':compare2, 'tableContent':tableContent, 'showLongList':showList,}
    print(errorReport)
    return render(request,"sales_comp/week_breakdown.html",contents)

@login_required
def departmant_sales_weekly_breakdown(request,storeID,year):
    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)

    # create redirects for selecting a new store or year.
    if 'storeName' in request.GET:
        return redirect('sales:department_breakdown', storeID=request.GET['storeName'], year=year)
    if 'selectYear' in request.GET:
        return redirect('sales:department_breakdown', storeID=storeID, year=request.GET['selectYear'])


    #need to work out the previous year for the compairsons
    yearPre = (datetime.date(int(year),1,1) + datetime.timedelta(weeks=-1)).strftime("%Y")

    #pull the selected store from the database
    selectedStore = StoreSave.objects.get(store=storeID)
    #make a list for user to switch between stores and years.
    storeList = StoreSave.objects.exclude(store=storeID)
    yearList = list(range(selectedStore.year_opr_start+1,int(timezone.localtime().strftime("%Y"))+1))
    print(yearList)
    yearList.remove(int(year))
    print(yearList)
    yearList.insert(0,int(year))
    print(yearList)

    #get the list of dated oprs that are in the years needed
    current_files = FileDate.objects.filter(store=selectedStore, date__year=year,data_exists=True).order_by("date")
    previous_files = FileDate.objects.filter(store=selectedStore, date__year=yearPre).order_by("date")

    #count how may ops are in that year.
    date_count = current_files.count()

    #Create a list of objects that the user can switch between departments
    #This is aultered for a custom list for user
    deptList = []

    for item in OPRSave.objects.filter(data_level=1):
        if not (WeekSales.objects.filter(date__in=current_files,section_name=item.name).count() > 0):
            print("%s does not exsit in this OPR set skipping" % item.name)
            continue
        if item.data_level == 1:
            nameDept = item.name.split("-")[-1].strip()
            if nameDept not in deptList:
                if nameDept.lower() == "meat, poultry & fish":
                    deptList.append("MEAT & POULTRY")
                    deptList.append("FISH")
                elif nameDept.lower() == "bread and cakes":
                    deptList.append("BREAD")
                    deptList.append("CAKES")
                    deptList.append("BAKERY")
                elif nameDept.lower() == "instore services":
                    deptList.append("E TOP UP")
                    deptList.append("LOTTO")
                else:
                    deptList.append(nameDept)

    deptList = sorted(deptList)
    #select which department to look at. by default just pick the first one in the list.
    if 'Department' in request.GET:
        print(request.GET['Department'])
        dept = request.GET['Department']
    else:
        dept = deptList[0]

    print(dept)
    deptSalesDict = []
    count = -1
    for date,previousDate in zip(current_files,previous_files):
        count += 1
        custom_name_toggle = False
        if dept == "MEAT & POULTRY":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="MEAT, POULTRY & FISH")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=2, catagory_tree__startswith=','.join(catagory_tree[0:1])).exclude(name__icontains="fish")

        elif dept == "FISH":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="MEAT, POULTRY & FISH")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=2,name__icontains="fish", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        elif dept == "BREAD":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="BREAD AND CAKES")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=2,name__icontains="BREAD", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        elif dept == "CAKES":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="BREAD AND CAKES")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=2,name__icontains="cake", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        elif dept == "BAKERY":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="BREAD AND CAKES")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=2,name__icontains="BAKERY", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        elif dept =="LOTTO":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="instore services")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=3,name__icontains="lottery", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        elif dept =="E TOP UP":
            department_filter = OPRSave.objects.get(data_level=1,name__icontains="instore services")
            catagory_tree = department_filter.catagory_tree.split(',')
            tempItem = OPRSave.objects.filter(data_level=3,name__icontains="e top up", catagory_tree__startswith=','.join(catagory_tree[0:1]))

        else:
            department_filter = OPRSave.objects.get(data_level=1,name__icontains=dept)
            custom_name_toggle = True

        if custom_name_toggle:
            wkTurnover = WeekSales.objects.get(section_name=department_filter,date=date).sale
            previous_wkTurnover = WeekSales.objects.get(section_name=department_filter,date=previousDate).sale
        else:
            wkTurnover = WeekSales.objects.filter(date=date,section_name__in=tempItem).aggregate(Sum('sale'))['sale__sum']
            previous_wkTurnover = WeekSales.objects.filter(date=previousDate,section_name__in=tempItem).aggregate(Sum('sale'))['sale__sum']


        wkTurnover = float(wkTurnover)
        previous_wkTurnover = float(previous_wkTurnover)
        if count == 0:
            cumulative_wkTurnover = wkTurnover
            cumulative_previous_wkTurnover = previous_wkTurnover
        else:
            cumulative_wkTurnover += wkTurnover
            cumulative_previous_wkTurnover += previous_wkTurnover

        diff =  float(wkTurnover - previous_wkTurnover)
        diffPrec = 100. * diff / previous_wkTurnover

        cumulative_diff = float(cumulative_wkTurnover - cumulative_previous_wkTurnover)
        cumulative_diffPrec = 100. * cumulative_diff / cumulative_previous_wkTurnover

        deptSalesDict.append({
            "date":date.date.strftime("%d-%b"),
            "preYear_wkTurnover":"{:,.0f}".format(previous_wkTurnover),
            "wkTurnover":"{:,.0f}".format(wkTurnover),
            "cumulative_wkTurnover":"{:,.0f}".format(cumulative_wkTurnover),
            "diff":"{:,.0f}".format(diff),
            "diffPrec":"{0:.2f}".format(diffPrec),
            "cumulative_diff":"{:,.0f}".format(cumulative_diff),
            "cumulative_diffPrec":"{0:.2f}".format(cumulative_diffPrec),
            })

    contents = {'selectedStore':selectedStore,'storeList':storeList,'dept':dept,'deptList':deptList, 'deptSalesDict':deptSalesDict,'yearList':yearList}
    return render(request,'sales_comp/dept_breakdown.html', contents)

@login_required
def total_year_sale_to_previous_year(request,storeID,year):
    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)
    #set the previous year.
    yearPre = str(int(year) - 1)

    #make a list for user to switch between stores
    selectedStore = StoreSave.objects.get(store=storeID)
    storeList = StoreSave.objects.exclude(store=storeID)

    #Build up a blank filedates to cycle through starting at the new year,
    saterdayList = mkSaterdayList(year=year)
    if FileDate.objects.filter(file_type="OPR",financial_year=year,store=selectedStore).count() < 50:
        for date in saterdayList:
            temp_date,created = FileDate.objects.get_or_create(file_type="OPR",date=date,financial_year=year,week_number=saterdayList[date],store=selectedStore)
            if created:
                totalWeekTurnover.objects.create(date=temp_date,turnover=0.0)

    dates = FileDate.objects.filter(financial_year=year,store=selectedStore).order_by("date")
    #Handles the change budget POST
    budgetFilter = totalWeekTurnover.objects.filter(date__in=dates).order_by("date")
    if request.method == 'POST':
        for key,value in request.POST.items():
            print("forms update: %s = %s" %(key, value))

        if "default_set_budget" in request.POST:
            print("Updating all budgets with:",request.POST["default_set_budget"])
            budgets = [[dated.date,ChangeBudget(prefix=str(idx),instance=dated)] for idx,dated in enumerate(budgetFilter)]
            for dated,item in budgets:
                update_budget = item.save(commit=False)
                update_budget.budget_percent = request.POST["default_set_budget"]
                update_budget.save()

            #Set the updated values
            budgets = [[dated.date,ChangeBudget(prefix=str(idx),instance=dated)] for idx,dated in enumerate(budgetFilter)]
        else:
            budgets = [[dated.date,ChangeBudget(request.POST, prefix=str(idx),instance=dated)] for idx,dated in enumerate(budgetFilter)]
            if all([item.is_valid() for dated,item in budgets]):
                print("All items are valid!")
                for dated,item in budgets:
                    update_budget = item.save()

    else:
        budgets = [[dated.date,ChangeBudget(prefix=str(idx),instance=dated.date)] for idx,dated in enumerate(budgetFilter)]
    #need to work out possible years the user can select from saved data
    alldates = FileDate.objects.filter(week_number=1,file_type="OPR",store=selectedStore).order_by("date")[1::]
    yearList = []
    for date in alldates:
        if date.date.strftime('%Y') not in yearList:
            yearList.append(date.date.strftime('%Y'))
    #~
    #This section is for working out the html tables
    #~
    postRow = []
    dateList = []

    #Selecting the first opr of the year.
    date = FileDate.objects.filter(file_type="OPR",store=selectedStore,date__year=year).order_by("date")[0].date

    #Need to make sure that the first opr is from the first week.
    start_year_check = True
    deltaTime = 0
    while start_year_check:
        deltaTime -= 1
        if date.strftime("%Y") != (date+datetime.timedelta(weeks=deltaTime)).strftime("%Y"):
            deltaTime += 1
            date = date + datetime.timedelta(weeks=deltaTime)
            start_year_check = False

    # Start building the table from the first week of selected year
    # Setting cumulative turnover to 0 for new cycle
    c_wkTurnover = 0.
    c_bugt = 0.
    c_preTurn = 0.
    next_week_exists = True
    leap_year_toggle = False

    for item in dates:
        weeks_dictionary = {}
        # getting the corrsponding date from last year
        last_year_date_object = FileDate.objects.filter(file_type="OPR",store=selectedStore,financial_year=item.financial_year-1,week_number=item.week_number)
        if last_year_date_object.exists():
            last_year_date_object = last_year_date_object[0]
        else:
            leap_year_toggle = True


        # print(" ")
        # print(item)
        # print(item.pk)
        # print(totalWeekTurnover.objects.filter(date=item))
        # print(" ")
        this_weeks_total = totalWeekTurnover.objects.get(date=item)
        if this_weeks_total.turnover == 0 and item.data_exists:
            weeklyTotal(item)
            this_weeks_total = totalWeekTurnover.objects.get(date=item)

        weeks_dictionary["date"] = this_weeks_total.date.date.strftime("%d-%b")

        if not leap_year_toggle:
            last_year_total =  totalWeekTurnover.objects.get(date=last_year_date_object)
            bugtTurnover = float(last_year_total.turnover + last_year_total.turnover_vat) * (1.0 + float(this_weeks_total.budget_percent)/100.0)

        weeks_dictionary["bugtTurnover"] = "{0:,.0f}".format(bugtTurnover)
        c_bugt+=bugtTurnover

        weeks_dictionary["c_bugt"] = math.floor(c_bugt)
        c_wkTurnover+=float(this_weeks_total.turnover)
        if this_weeks_total.date.data_exists:

            # print(" ")
            # print(item)
            # print(item.pk)
            # print(this_weeks_total.turnover)
            # print(" ")
            if not leap_year_toggle:
                c_preTurn+=float(last_year_total.turnover)

            weeks_dictionary["wkTurnover"] = "{0:,.0f}".format(this_weeks_total.turnover + this_weeks_total.turnover_vat)
            # print("This weeks turnover: %s"%weeks_dictionary["wkTurnover"])
            if not leap_year_toggle:
                weeks_dictionary["pre_turnover"] = "{0:,.0f}".format(last_year_total.turnover + last_year_total.turnover_vat)
            else:
                weeks_dictionary["pre_turnover"] = "{0:,.0f}".format(0.0)
            weeks_dictionary["c_wkTurnover"] = "{0:,.0f}".format(c_wkTurnover)
            weeks_dictionary["c_preTurn"] = "{0:,.0f}".format(c_preTurn)

            diff = float(this_weeks_total.turnover) - bugtTurnover
            c_diff = float(c_wkTurnover) - c_bugt
            if not leap_year_toggle:
                pre_diff = (this_weeks_total.turnover + this_weeks_total.turnover_vat) - (last_year_total.turnover + last_year_total.turnover_vat)
                if float(last_year_total.turnover) != 0:
                    pre_diffPrec = float(pre_diff)*100./float(last_year_total.turnover + last_year_total.turnover_vat)
                else:
                    pre_diffPrec = 0.0
            else:
                pre_diff = float(this_weeks_total.turnover + this_weeks_total.turnover_vat) - 0.0
                pre_diffPrec = 0.0
            c_pre_diff = c_wkTurnover - float(c_preTurn)

            weeks_dictionary["diff"] = "{0:,.0f}".format(diff)
            weeks_dictionary["pre_diff"] = "{0:,.0f}".format(pre_diff)
            weeks_dictionary["c_diff"] = "{0:,.0f}".format(c_diff)
            weeks_dictionary["c_pre_diff"] = "{0:,.0f}".format(c_pre_diff)

            if float(bugtTurnover) != 0:
                diffPrec = diff*100./float(bugtTurnover)
            else:
                diffPrec = 0.0
            if float(c_bugt) != 0:
                c_diffPrec = c_diff*100./c_bugt
            else:
                c_diffPrec = 0.0
            if float(c_preTurn) != 0:
                c_pre_diffPrec = c_pre_diff*100./float(c_preTurn)
            else:
                c_pre_diffPrec = 0.0

            weeks_dictionary["diffPrec"] = "{0:,.2f}".format(diffPrec)
            weeks_dictionary["pre_diffPrec"] = "{0:,.2f}".format(pre_diffPrec)
            weeks_dictionary["c_diffPrec"] = "{0:,.2f}".format(c_diffPrec)
            weeks_dictionary["c_pre_diffPrec"] = "{0:,.2f}".format(c_pre_diffPrec)
        else:
            weeks_dictionary["pre_turnover"] = ""
            weeks_dictionary["wkTurnover"] = ""

            weeks_dictionary["diff"] = ""
            weeks_dictionary["diffPrec"] = ""
            weeks_dictionary["c_diff"] = ""
            weeks_dictionary["c_diffPrec"] = ""

            weeks_dictionary["pre_diff"] = ""
            weeks_dictionary["pre_diffPrec"] = ""
            weeks_dictionary["c_pre_diff"] = ""
            weeks_dictionary["c_pre_diffPrec"] = ""

            weeks_dictionary["c_wkTurnover"] = ""
            weeks_dictionary["c_preTurn"] = ""

        postRow.append(weeks_dictionary)


        # # Check if there is a next week opr and exit if not.
        # try:
        #     date = date + datetime.timedelta(weeks=1)
        #     date_object = FileDate.objects.get(file_type="OPR",date=date.strftime("%Y%m%d"))
        # except:
        #     print("No more OPR's. Last one was: %s" %date.strftime("%Y%m%d"))
        #     next_week_exists = False



    contents = {'store':selectedStore,'storeList':storeList,'year':year,'yearList':yearList,'postRow':postRow,'budgets':budgets}
    return render(request,'sales_comp/comparison.html',contents)

@login_required
def missing_oprs(request):
    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)
    stores = StoreSave.objects.all()
    missingOPRS=[]
    yearList=[]
    for store in stores:
        dates = FileDate.objects.filter(store=store).order_by("date")
        yearListStore = []
        for date in dates:
            if date.date.strftime('%Y') not in yearList:
                yearList.append(date.date.strftime('%Y'))
            if date.date.strftime('%Y') not in yearListStore:
                yearListStore.append(date.date.strftime('%Y'))
        for year in yearListStore:
            print(" ")
            print(" ")
            print(year)
            tempDate = FileDate.objects.filter(store=store, data_exists=True, date__year=year).order_by('date')[0].date
            week = 0
            print(tempDate)
            print(timezone.localtime().strftime("%Y-%m-%d"))
            while week <= 50:
                if tempDate.strftime("%Y-%m-%d") > timezone.localtime().strftime("%Y-%m-%d"):
                    break
                try:
                    checkYear = FileDate.objects.get(store=store, date=tempDate+datetime.timedelta(days=7))
                except:
                    print(store, tempDate + datetime.timedelta(days=7),"Missing")
                    missingOPRS.append([store,tempDate+datetime.timedelta(days=7)])
                tempDate = tempDate+datetime.timedelta(days=7)
                week += 1
        return render(request,'sales_comp/missing_oprs.html', {'missingOPRS':missingOPRS, 'stores':stores, 'yearList':yearList})
