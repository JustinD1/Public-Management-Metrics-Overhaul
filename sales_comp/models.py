from django.db import models

from home.models import FileDate
from OPR2.models import WeekSales, YearSales

class totalWeekTurnover(models.Model):
    date = models.ForeignKey(FileDate, on_delete=models.CASCADE)
    turnover = models.DecimalField(max_digits=12,decimal_places=4,blank=True)
    turnover_vat = models.DecimalField(max_digits=12,decimal_places=4,blank=True)

    budget_percent = models.DecimalField(max_digits=6,decimal_places=2, default=3.00)

    class Meta:
        ordering = ['date']
    def __str__(self):
        return str(self.date)

# class AutoDisplaySections()
class Comparisons(models.Model):
    class Meta:
        unique_together = ('date','week_sale','year_sale')

    date = models.ForeignKey(FileDate, on_delete=models.CASCADE)
    week_sale = models.ForeignKey(WeekSales, on_delete=models.CASCADE)
    year_sale = models.ForeignKey(YearSales, on_delete= models.CASCADE)
    budget =  models.DecimalField(max_digits=6, decimal_places=2, default=3.00)
    percentage_sale_last_week = models.DecimalField(max_digits=9, decimal_places=4)
    percentage_sale_last_year = models.DecimalField(max_digits=9, decimal_places=4)
    sum_last_4_weeks_sale = models.DecimalField(max_digits=11, decimal_places=3)
    percentage_sale_last_year_4_weeks = models.DecimalField(max_digits=9, decimal_places=4,default=0.0)
    percentage_sale_year2date = models.DecimalField(max_digits=9, decimal_places=4,default=0.0)
    entery_exists = models.BooleanField(default=False)
