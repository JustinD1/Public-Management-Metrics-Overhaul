from django.db.models import Sum, Count

from home.models import FileDate
from OPR2.models import *
from sales_comp.models import Comparisons

import datetime

def populate(date_object,storeID):
    week_sale = WeekSales.objects.filter(date=date_object)
    for week_item in week_sale:
        print(" ")
        print(week_item.date)
        print(week_item.section_name)
        last_week = date_object.date - datetime.timedelta(weeks=1)
        previous_year = str(int(date_object.date.strftime("%Y")) - 1)

        if not(FileDate.objects.filter(store_id=storeID, date=last_week, file_type="OPR").exists()):
            print("Object last week does not exists.")
            continue
        else:
            date_last_week = FileDate.objects.get(store_id=storeID,date=last_week, file_type="OPR")

        if not(FileDate.objects.filter(store_id=storeID,date__year=previous_year, file_type="OPR", week_number=date_object.week_number).exists()):
            print("Object last year does not exists.")
            continue
        else:
            date_last_year = FileDate.objects.get(store_id=storeID,date__year=previous_year, file_type="OPR", week_number=date_object.week_number)


        values = Calc_values(date_object=date_object,week_item=week_item,date_last_year=date_last_year,date_last_week=date_last_week,storeID=storeID)
        # print(date_object)
        # print(week_item)
        # print(YearSales.objects.get(date=date_object,section_name=week_item.section_name))
        for item in values:
            print(item,values[item])
        compar,create = Comparisons.objects.get_or_create(
            date = date_object,
            week_sale = week_item,
            year_sale = YearSales.objects.get(date=date_object,section_name=week_item.section_name),
            percentage_sale_last_week = values['percentage_sale_last_week'],
            percentage_sale_last_year = values['percentage_sale_last_year'],
            sum_last_4_weeks_sale = values['sum_last_4_weeks_sale'],
            percentage_sale_last_year_4_weeks = values['percentage_sale_last_year_4_weeks'],
            percentage_sale_year2date = values['percentage_sale_year2date'],
            entery_exists = True
        )
        print(compar,create)

def Calc_values(date_object,week_item,date_last_year,date_last_week,storeID):
    dict_value = {}
    year_item = YearSales.objects.get(
                                date=week_item.date,
                                section_name=week_item.section_name
    )
    dict_value['week_sale'] = float(week_item.sale)
    dict_value['year2_sale'] = float(year_item.sale)
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

    #~~ 4 week sum calulations ~~#

    last_4_weeks = FileDate.objects.exclude(date__lt=(date_object.date - datetime.timedelta(weeks=4))).filter(store_id=storeID,date__lt=date_object.date)
    last_4_weeks_last_year = FileDate.objects.exclude(date__lt=(date_last_year.date - datetime.timedelta(weeks=4))).filter(store_id=storeID,date__lt=date_last_year.date)

    if WeekSales.objects.filter(date__in=last_4_weeks, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'] is None:
        dict_value['sum_last_4_weeks_sale'] = 0.0
    else:
        dict_value['sum_last_4_weeks_sale'] = float(WeekSales.objects.filter(date__in=last_4_weeks, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])

    if last_4_weeks_last_year.count() == 4:
        if WeekSales.objects.filter(date__in=last_4_weeks_last_year, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'] is None:
            sum_last_year = 0.0
        else:
            sum_last_year =  float(WeekSales.objects.filter(date__in=last_4_weeks_last_year, section_name=week_item.section_name).aggregate(Sum('sale'))['sale__sum'])
    else:
        # print("sum_last_year doesn't have 4 dates to it")
        print(last_4_weeks_last_year,last_4_weeks_last_year.count())
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

    if dict_value['year2_sale'] == 0.0:
        # print('percentage_sale_year2date: -100%')
        dict_value['percentage_sale_year2date'] = -1.0
    elif sale_last_year2date == 0.0:
        # print('percentage_sale_year2date: 100%')
        dict_value['percentage_sale_year2date'] = 1.0
    else:
        dict_value['percentage_sale_year2date'] = (dict_value['year2_sale'] / sale_last_year2date) - 1.0

    return dict_value

# makes a list of dates that will be excluded. This is built from enteries that
# are already in the Comparisions file.
file_list = []
ID=239
for item in FileDate.objects.filter(file_type="OPR",store_id=ID).exclude(date__year="2013"):
    temp_object = Comparisons.objects.filter(date=item)
    if not(temp_object.count() > 0):
        file_list.append(item)

# print(file_list)
for item in file_list:
    previous_year = str(int(item.date.strftime("%Y")) - 1)
    if FileDate.objects.filter(date__year=previous_year,week_number=item.week_number).exists():
        print(item)
        populate(date_object=item,storeID=ID)
    else:
        print("OPR year: %s, week: %s; does not exsit."%(previous_year,item.week_number))
