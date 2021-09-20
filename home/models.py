from django.db import models

class StoreSave(models.Model):
    def __str__(self):
        return '-'.join([str(self.store),self.store_town])

    class Meta:
        verbose_name = 'Store'

    store_town = models.CharField(max_length=50)
    store = models.PositiveSmallIntegerField(blank=True, primary_key=True)
    region = models.IntegerField(default=0)
    year_opr_start = models.PositiveSmallIntegerField(blank=True)

class FileDate(models.Model):
    def __str__(self):
        return ' '.join([self.file_type,str(self.date)])

    class Meta:
        ordering = ['store','-date']
        unique_together = ('store','date','file_type')
        verbose_name = 'File dated'

    store = models.ForeignKey(StoreSave, on_delete=models.CASCADE)
    data_exists = models.BooleanField(default=False)
    date = models.DateField()
    file_type = models.CharField(max_length=20)
    financial_year = models.PositiveIntegerField()
    week_number = models.PositiveIntegerField()

class UserURLS(models.Model):
    url_code = models.URLField()
