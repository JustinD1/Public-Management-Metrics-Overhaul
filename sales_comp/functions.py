from django.db.models import Sum

from OPR2.models import FileDate, WeekSales
import datetime

def SetTableContentDefault(current,previous):
    contents = {}

    sale = float(current.sale)
    preSale = float(previous.sale)
    diff = current.sale - previous.Sale

    contents["tag"] = current.catagory
    contents["name"] = current.name
    contents["currentSale"] = "{:,.2f}".format(current.sale)
    contents["previousSale"] = "{:,.2f}".format(previous.Sale)
    contents["diff"] = "{:,.2f}".format(diff)

    #Make sure that the precentage returens "-" if any of the values is a 0
    if sale == 0.0 or preSale == 0.0:
        contents["diffPrec"] = "-"
    else:
        contents["diffPrec"] = "{0:.2f}".format(diff/preSale)
    return contents

def SetTableContentYear2Week(tableContent,name,sendQuery):
    contents = {}

    store = sendQuery[0]
    curDate = sendQuery[1]
    preDate = sendQuery[2]
    current = sendQuery[3]
    previous = sendQuery[4]

    #Make filters for the year to date.
    currentYear2Date = FileDate.objects.exclude(store=store,date__gt=curDate.date).filter(date__gt=(curDate.date - datetime.timedelta(weeks=52)))
    preYear2Date = FileDate.objects.exclude(store=store,date__gt=preDate.date).filter(date__gt=(preDate.date - datetime.timedelta(weeks=52)))

    #Sum up the year to date for current year and comparison year
    year2week = WeekSales.objects.filter(name=current.name, date__in=currentYear2Date).aggregate(Sum('sale'))['sale__sum']
    preYear2week = WeekSales.objects.filter(name=current.name, date__in=preYear2Date).aggregate(Sum('sale'))['sale__sum']

    y2wDiff = year2week - preYear2week
    contents["y2w"] = "{:,.2f}".format(year2week)
    contents["preY2w"] = "{:,.2f}".format(preYear2week)
    contents["y2wdiff"] = "{:,.2f}".format(y2wDiff)
    if preYear2week == 0.0 or year2week == 0.0:
        contents["y2wdiffPrec"] = "-"
    else:
        contents["y2wdiffPrec"] = "{0:.2f}".format(y2wDiff/preYear2week)
    #set the base contents that are in most reports
    contents = SetTableContentDefault(current=current,previous=previous)

    tableContent.append(contents)
    return tableContent
