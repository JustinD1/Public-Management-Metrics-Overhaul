
from home.models import FileDate, StoreSave
from sales_comp.models import Comparisons, totalWeekTurnover
from OPR2.models import WeekSales

stores = StoreSave.objects.all()
for store in stores:
    # store=stores[1]
    print("\n %s" %store.store_town)
    list_1 = []
    dates = FileDate.objects.filter(store=store,date__year="2019").order_by("date")
    for date in dates:
        print(date.date)
        this_turnover = totalWeekTurnover.objects.filter(date=date)
        if this_turnover.exists():
            this_turnover=this_turnover[0]
            print("--Turnover has a value of %s and the data exists is set to: %s" %(this_turnover.turnover,date.data_exists))

        else:
            print("--Turnover doesn\'t exsit and the data_exists is set to: %s" %date.data_exists)
            this_turnover=totalWeekTurnover.objects.get_or_create(
                            date=date,
                            turnover=0.0
            )
