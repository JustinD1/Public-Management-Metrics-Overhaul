from django.db.models import Sum, Count

from home.models import FileDate
from OPR2.models import *
from sales_comp.models import Comparisons, totalWeekTurnover

import datetime

departments = OPRSave.objects.filter(data_level=1)

for store in StoreSave.objects.all():
    # Keep the first yesr of OPR's out of the starting calculation due to needing a starting year
    for item in FileDate.objects.filter(store=store.store,file_type="OPR").exclude(data_exists=False):
        total_turnover = WeekSales.objects.filter(section_name__in=departments,date=item).aggregate(Sum('sale'))['sale__sum']
        print(item)
        print("OPR %s has a total of %d" %(item.date,total_turnover))
        current_totalWeekTurnover,created = totalWeekTurnover.objects.update_or_create(date=item,turnover=total_turnover)
