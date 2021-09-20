from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models import Q

from home.models import StoreSave,FileDate
from OPR2.models import *
from sales_comp.models import Comparisons, totalWeekTurnover

from xlrd.sheet import ctype_text
import xlrd, os, glob
import datetime
import operator
from functools import reduce

# [#0001] Check folder for new upload.
# [#0002] OPR read in; OPR2.models
# [#0003] Fill/create catagory trees;
# [#0004] Fill in the comparison database; sales_comp.models
# [#0005] Fill in the weektotal database;

#############################################################
######################## [#0001] ############################
#############################################################
# Check folder if opr has been upload to the server
# This will then prep the file to be broken down into the database.

def HandleOPRFile(errorReport,noteReport):
    OPR_list = []
    # print("\nTime: %s"%timezone.now())
    previous_path = os.getcwd()
    directory_prefix = settings.MEDIA_ROOT+"/TEMP/opr/"
    os.chdir(directory_prefix)
    data_check = False

    #This section will read in the OPR excel sheets to the database.
    #It will retain the pk of all new opr under OPR_list.
    #It then deletes the uploaded file from the computer.
    for file in glob.glob("*.xls"):
        # print("Reading in file %s" % directory_prefix+file)
        updateDB(directory_prefix+file,OPR_list)

        # print("Checking the OPR catagories and adding new ones.")
        # print(OPR_list)
        if OPR_list:
            data_check = True
            CreateCatagory(OPR_list[-1])

        # print("Current list of files that have been uploaded to database:\n %s \n\n"%OPR_list)
        # print("File was read into the database now deleting the document from server.\n")
        os.remove(directory_prefix+file)
        os.chdir(previous_path)

    data_check = True
    if data_check:
        query_list = []
        for store in StoreSave.objects.all():
            oldest_date = FileDate.objects.filter(store=store, data_exists=True, pk__in=OPR_list).order_by("date")
            # print(store)
            # print(oldest_date.count())
            if oldest_date.count() > 0:
                oldest_date = oldest_date[0]
                query_list.append(Q(store=store, date__gte=oldest_date.date, data_exists=True))

        files_to_update = FileDate.objects.filter(reduce(operator.or_,query_list)).exclude(date__gt=timezone.now()).order_by("date")
        # print("\n\nFilling in the following OPRs:")
        # print(*files_to_update, sep="\n")

        for file in files_to_update:
            # print("\n\n %s"%file)
            # print("Populating the comparison database.")
            PopulateComparison(file)
            # print("Populating the weekly total database.\n")
            weeklyTotal(file)


    return

#############################################################
######################## [#0002] ############################
#############################################################
# OPR read in
# This section is for populating the OPR's into the database
def mkSaterdayList(year):
    year=int(year)
    #Build a list of all saterdays in the year.
    firstSat = datetime.date(int(year),1,1)
    firstSat += datetime.timedelta(days = (5 - firstSat.weekday() + 7)% 7)
    firstSat_nextYear = datetime.date(int(year)+1,1,1)
    firstSat_nextYear = datetime.timedelta(days = (5 - firstSat_nextYear.weekday() + 7)% 7)

    saterdaydict = {}
    count = 0
    while firstSat.year == year:
        count += 1
        saterdaydict[firstSat] = count
        firstSat += datetime.timedelta(days = 7)
        if firstSat == firstSat_nextYear:
            break
    return saterdaydict

def check_row(row):
    for item in row:
        cell_type_str = ctype_text.get(item.ctype,'unknown type')
        if cell_type_str != 'empty':
            return False

def updateDB(filepath,OPR_list):
    print("Starting updateDB function")
    #Loading the opr data into a workable format.
    x1_workbook = xlrd.open_workbook(filepath)
    x1_sheet = x1_workbook.sheet_by_index(0)

    ##~This will work out the maximum number of rows that have data in them.
    count = 0
    while count < 10:
        x1_col = x1_sheet.col(count)
        if count == 0:
            maxColCell = len(x1_col) - 1
        elif maxColCell < len(x1_col) - 1:
            maxColCell = len(x1_col) - 1

        count += 1

    ##~This section will make sure that the xl sheet is an opr and will read in
    #the store name and the date of the opr to be used later
    count = 0

    #toggles for skipping information once an item is found
    dayToggle = False
    weekToggle = False
    yearToggle = False
    dateToggle = False
    storeToggle = False

    #creating lists that need to be created and a switch that will exit loop
    #once all preamble work is done.
    count = 0
    rowSelect = -10
    colIdx = []
    # keyList = []

    #This loop basicly reads in the "header" of the OPR and extracts the date
    #store name and creates all the class names to be used when pulling out
    #the values.
    print("starting header readin")
    while count < maxColCell:
        x1_row = x1_sheet.row(count)
        #check if the row is all empty and skip to the next row
        if check_row(row=x1_row):
            count += 1
            continue
        for idx,cell_obj in enumerate(x1_row):
            cell_type_str = ctype_text.get(cell_obj.ctype,'unknown type')
            strTemp = cell_obj.value

            #The excel doc is riddled with gaps in the columns so we want to
            #skip them
            if cell_type_str == "empty":
                continue

            #Once the store and date tag have been reached we save the values.
            if str(strTemp).lower() == "date":
                print("Found the date of the OPR")
                dateToggle = True
            elif dateToggle:
                date_split = cell_obj.value.split("/")
                file_date = datetime.date(int(date_split[2]),int(date_split[1]),int(date_split[0]))
                saterdaydict = mkSaterdayList(int(date_split[2]))
                print(file_date)
                if file_date not in saterdaydict:
                    print("OPR isn't a Saterday opr")
                    return
                dateToggle = False
                break
            if str(strTemp).lower() == "store":
                print("Found the Store name")
                storeToggle = True
            elif storeToggle:
                oprStore = cell_obj.value.replace(" ","")
                print(oprStore)
                # print(str(filepath))
                storeToggle = False
                break

            #once the row holding all the column titles is reached we toggle
            #rowselect. This save the departments and adds in sections depending
            #if the OPR has day week year columns. We also want to save the
            #column index number so any blank values under a title is entered
            #as a blank value rather than skipping it.
            if 'oprStore' in locals() and 'file_date' in locals():
                if str(strTemp).lower() == "dept":
                    rowSelect = count

                if rowSelect == count:
                    if str(strTemp).lower().startswith('day'):
                        dayToggle = True
                        continue
                    elif str(strTemp).lower().startswith('week'):
                        weekToggle = True
                        continue
                    elif str(strTemp).lower().startswith('year'):
                        yearToggle = True
                        continue
                    else:
                        # keyList.append(str(strTemp).lower().replace(' ','_'))
                        colIdx.append(idx)
                elif rowSelect + 1 == count:
                    #rowselect + 1 is a second line for column titles
                    colIdx.append(idx)
                elif rowSelect + 2 == count:
                    #rowselect + 2 is the start of the data readin and needs an
                    #other loop
                    break
        if rowSelect + 2 == count:
            break

        count += 1

    ##~Check if the store exists and creates/appends the opr
    #
    print("Get or creating a store object.")
    store_name = oprStore.split('-')
    storeDB,created = StoreSave.objects.get_or_create(
        store_town=store_name[1].strip(),
        store=store_name[0].strip()
    )
    #if a new store is created set the first recorded opr year
    if created:
        print("New store was created. Adding in a opr start date for the store.")
        storeDB.year_opr_start=date_split[2]
        storeDB.save()

    print("Creating the opr header object.")
    try:
        dateDB = FileDate.objects.get(data_exists=True,store=storeDB,date=file_date)
        print("This opr exists, skipping.")
        return
    except:
        dateDB,created = FileDate.objects.get_or_create(
            store=storeDB,
            date=file_date,
            file_type="OPR",
            financial_year=date_split[2],
            week_number=saterdaydict[file_date]
            )
        dateDB.data_exists=True
        dateDB.save()


    #save the id of the created opr for later database functions
    print("Appending the newly added opr to completed list.")
    OPR_list.append(dateDB.pk)

    breakToggle = False
    count -= 1

    while count < maxColCell:
        count += 1
        skip_row = True
        # print(count)
        values = []
        blankNumberToggle = 0
        unmatched_count = 0
        unmatched_suffixs = ["d","c","s","f"]
        for idx in colIdx:
            cellVal = x1_sheet.cell_value(count,idx)
            # print("Row: %s, Col: %s Val: %s" % (count, idx, cellVal))
            if str(cellVal).lower().startswith('totals ('):
                breakToggle = True
                break
            elif str(cellVal).lower().startswith('d'):
                skip_row = False
                name = str(cellVal)
                data_level = 1
            elif str(cellVal).lower().startswith('s'):
                skip_row = False
                name = str(cellVal)
                data_level = 2
            elif str(cellVal).lower().startswith('c'):
                skip_row = False
                name = str(cellVal)
                data_level = 3
            elif str(cellVal).lower().startswith('f'):
                skip_row = False
                name = str(cellVal)
                data_level = 4
            elif str(cellVal).lower().startswith('unmatched'):
                skip_row = False
                name = "-".join([unmatched_suffixs[unmatched_count],str(cellVal)])
                unmatched_count += 1
                data_level = unmatched_count


            # print(name)
            if blankNumberToggle > 3:
                if cellVal == '':
                    cellVal = 0
                values.append(cellVal)
            blankNumberToggle += 1

        if breakToggle:
            break
        if skip_row:
            continue
        # print("Name: %s, Data level: %d" %(name,data_level))
        OPR,created = OPRSave.objects.get_or_create(
            name = name,
            data_level = data_level
        )
        WeekSale,created = WeekSales.objects.get_or_create(
            date = dateDB,
            section_name = OPR,
            sale = values[5],
            vat = values[6],
            part = values[7],
            margin = values[8]
        )
        YearSale,created = YearSales.objects.get_or_create(
            date = dateDB,
            section_name = OPR,
            sale = values[10],
            vat = values[11],
            part = values[12],
            margin = values[13]
        )

    print("File read in")
    return

##############################################################
######################## [#0003] #############################
##############################################################
# This section creates the catagory trees for the departments and create links.

def CreateCatagory(opr):
    dept = 0
    sub = 0
    com = 0
    fam = 0
    for item in WeekSales.objects.filter(date=opr).order_by("pk"):
        if item.section_name.data_level == 1:
            dept+=1
            sub = 0
            com = 0
            fam = 0
        if item.section_name.data_level == 2:
            sub+=1
            com = 0
            fam = 0
        if item.section_name.data_level == 3:
            com+=1
            fam = 0
        if item.section_name.data_level == 4:
            fam+=1
        text = catagory_set(name=item.section_name,dept=dept,sub=sub,com=com,fam=fam)
        # print("%s" %(text))
    return

def catagory_set(name,dept,sub,com,fam):
    current_object = OPRSave.objects.get(name=name.name, data_level=name.data_level)
    if current_object.catagory_tree != '':
        return 'Object is apart of an existing tree'

    while True:
        catagory_exists = OPRSave.objects.filter(catagory_tree=','.join(str(x) for x in [dept,sub,com,fam])).exists()
        # print(catagory_exists)
        if (current_object.catagory_tree == '') & (not catagory_exists):
            current_object.catagory_tree=','.join(str(x) for x in [dept,sub,com,fam])
            current_object.save()
            return 'updating: %s -> %s' %(current_object.catagory_tree,','.join(str(x) for x in [dept,sub,com,fam]))

        if name.data_level== 1:
            dept+=1
        elif name.data_level== 2:
            sub+=1
        elif name.data_level== 3:
            com+=1
        elif name.data_level== 4:
            fam+=1
    return


##############################################################
######################## [#0004] #############################
##############################################################
# This section is for populating the comparison database.
def PopulateComparison(opr):
    previous_year = str(int(opr.date.strftime("%Y")) - 1)
    if FileDate.objects.filter(date__year=previous_year,week_number=opr.week_number).exists():
        populate(date_object=opr)
    else:
        print("--------------------------------------------")
        print("OPR year: %s, week: %s; does not exsit."%(previous_year,opr.week_number))
        print("--------------------------------------------\n")
    return

def populate(date_object):
    week_sale = WeekSales.objects.filter(date=date_object)
    for week_item in week_sale:
        # print(" ")
        # print(week_item.date)
        # print(week_item.section_name)
        last_week = date_object.date - datetime.timedelta(weeks=1)
        previous_year = str(int(date_object.date.strftime("%Y")) - 1)

        if not(FileDate.objects.filter(store=date_object.store, date=last_week, file_type="OPR").exists()):
            print("Object last week does not exists.")
            continue
        else:
            date_last_week = FileDate.objects.get(store=date_object.store,  date=last_week, file_type="OPR")

        if not(FileDate.objects.filter(store=date_object.store, date__year=previous_year, file_type="OPR", week_number=date_object.week_number).exists()):
            print("Object last year does not exists.")
            continue
        else:
            date_last_year = FileDate.objects.get(store=date_object.store, date__year=previous_year, file_type="OPR", week_number=date_object.week_number)


        values = Calc_values(date_object=date_object,week_item=week_item,date_last_year=date_last_year,date_last_week=date_last_week)
        # print(date_object)
        # print(week_item)
        # print(YearSales.objects.get(date=date_object,section_name=week_item.section_name))
        try:
            comparison = Comparisons.objects.get(date = date_object,week_sale = week_item,year_sale = values['year2_sale'][0])
            comparison.percentage_sale_last_week = values['percentage_sale_last_week']
            comparison.percentage_sale_last_year = values['percentage_sale_last_year']
            comparison.sum_last_4_weeks_sale = values['sum_last_4_weeks_sale']
            comparison.percentage_sale_last_year_4_weeks = values['percentage_sale_last_year_4_weeks']
            comparison.percentage_sale_year2date = values['percentage_sale_year2date']
            comparison.entery_exists = True
            comparison.save()
            print("updated")
        except:
            comparison = Comparisons.objects.create(
                    date = date_object,
                    week_sale = week_item,
                    year_sale = values['year2_sale'][0],
                    percentage_sale_last_week = values['percentage_sale_last_week'],
                    percentage_sale_last_year = values['percentage_sale_last_year'],
                    sum_last_4_weeks_sale = values['sum_last_4_weeks_sale'],
                    percentage_sale_last_year_4_weeks = values['percentage_sale_last_year_4_weeks'],
                    percentage_sale_year2date = values['percentage_sale_year2date'],
                    entery_exists = True
                    )
            comparison.save()

            print("created")

    return

def Calc_values(date_object,week_item,date_last_year,date_last_week):
    dict_value = {}
    year_item = YearSales.objects.get(
                                date=week_item.date,
                                section_name=week_item.section_name
    )
    dict_value['week_sale'] = float(week_item.sale)
    dict_value['year2_sale'] = [year_item,float(year_item.sale)]


    ###~ This week to last week
    if WeekSales.objects.filter(date=date_last_week, section_name=week_item.section_name).exists():
        sale_last_week = float(WeekSales.objects.get(date=date_last_week, section_name=week_item.section_name).sale)
    else:
        # print("sale_last_week has no value.")
        sale_last_week = 0.0

    if dict_value['week_sale'] == 0.0:
        # print('percentage_sale_last_week: -100%')
        dict_value['percentage_sale_last_week'] = -1.0
    elif sale_last_week == 0.0:
        # print('percentage_sale_last_week: 100%')
        dict_value['percentage_sale_last_week'] = 1.0
    else:
        dict_value['percentage_sale_last_week'] = (dict_value['week_sale'] / sale_last_week) - 1.0


    ###~ This week to last year
    if WeekSales.objects.filter(date=date_last_year, section_name=week_item.section_name).exists():
        sale_last_year = float(WeekSales.objects.get(date=date_last_year, section_name=week_item.section_name).sale)
    else:
        # print("sale_last_year has no value.")
        sale_last_year = 0.0

    if dict_value['week_sale'] == 0.0:
        # print('percentage_sale_last_year: -100%')
        dict_value['percentage_sale_last_year'] = -1.0
    elif sale_last_year == 0.0:
        # print('percentage_sale_last_year: 100%')
        dict_value['percentage_sale_last_year'] = 1.0
    else:
        dict_value['percentage_sale_last_year'] = (dict_value['week_sale'] / sale_last_year) - 1.0



    ##~~ 4 week sum calulations ~~#
    last_4_weeks = FileDate.objects.exclude(store=date_object.store,date__lt=(date_object.date - datetime.timedelta(weeks=3))).filter(date__lte=date_object.date,store=date_object.store)
    last_4_weeks_last_year = FileDate.objects.exclude(store=date_object.store,date__lt=(date_last_year.date - datetime.timedelta(weeks=3))).filter(store=date_object.store,date__lte=date_last_year.date)

    if WeekSales.objects.filter(date__in=last_4_weeks, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'] is None:
        dict_value['sum_last_4_weeks_sale'] = 0.0
    else:
        dict_value['sum_last_4_weeks_sale'] = float(WeekSales.objects.filter(date__in=last_4_weeks, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])

    # if last_4_weeks_last_year.count() != 4:
    #     print(last_4_weeks)
    #     print(WeekSales.objects.filter(date__in=last_4_weeks, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])
    #     print(last_4_weeks_last_year)
    #     print(last_4_weeks_last_year.count())
    #     print(WeekSales.objects.filter(date__in=last_4_weeks_last_year, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])
    #     print(dict_value['sum_last_4_weeks_sale'])

    if last_4_weeks_last_year.count() == 4:
        if WeekSales.objects.filter(date__in=last_4_weeks_last_year, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'] is None:
            sum_last_year = 0.0
        else:
            sum_last_year =  float(WeekSales.objects.filter(date__in=last_4_weeks_last_year, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])
    else:
        # print("sum_last_year doesn't have 4 dates to it")
        # print(last_4_weeks_last_year,last_4_weeks_last_year.count())
        sum_last_year = 0.0
    if dict_value['sum_last_4_weeks_sale'] == 0:
        # print('sum_last_4_weeks_sale: -100%')
        dict_value['percentage_sale_last_year_4_weeks'] = -1.0
    elif sum_last_year == 0.0:
        # print('sum_last_4_weeks_sale: 100%')
        dict_value['percentage_sale_last_year_4_weeks'] = 1.0
    else:
        dict_value['percentage_sale_last_year_4_weeks'] = (dict_value['sum_last_4_weeks_sale'] / sum_last_year) - 1.0

    if YearSales.objects.filter(date=date_last_week, section_name=week_item.section_name).exists():
        sale_last_year2date = float(YearSales.objects.get(date=date_last_week, section_name=week_item.section_name).sale)
    else:
        # print("sale_last_year2date has no value.")
        sale_last_year2date = 0.0

    if dict_value['year2_sale'][1] == 0.0:
        # print('percentage_sale_year2date: -100%')
        dict_value['percentage_sale_year2date'] = -1.0
    elif sale_last_year2date == 0.0:
        # print('percentage_sale_year2date: 100%')
        dict_value['percentage_sale_year2date'] = 1.0
    else:
        dict_value['percentage_sale_year2date'] = (dict_value['year2_sale'][1] / sale_last_year2date) - 1.0

    return dict_value

##############################################################
######################## [#0005] #############################
##############################################################
# This section creates the total for the weeks for the uploaded OPR
def weeklyTotal(opr):
    departments = OPRSave.objects.filter(data_level=1)
    total_turnover = WeekSales.objects.filter(section_name__in=departments,date=opr).aggregate(Sum('sale'))['sale__sum']
    total_vat = WeekSales.objects.filter(section_name__in=departments,date=opr).aggregate(Sum('vat'))['vat__sum']
    # print(opr.store,opr)
    # print(*departments,sep="\n")
    # print("Turnover: %s + %s vat \n\n"%(total_turnover,total_vat))

    try:
        current_totalWeekTurnover = totalWeekTurnover.objects.get(date=opr)
        current_totalWeekTurnover.turnover = total_turnover
        current_totalWeekTurnover.turnover_vat = total_vat
        current_totalWeekTurnover.save()
    except:
        current_totalWeekTurnover = totalWeekTurnover.objects.create(date=opr, turnover=total_turnover, turnover_vat=total_vat)
    return
