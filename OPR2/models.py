from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from home.models import StoreSave, FileDate


class Document(models.Model):
    def __str__(self):
        return self.description

    description = models.CharField(max_length=255)
    document = models.FileField(upload_to='TEMP/opr/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class OPRSave(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Section'

    name = models.CharField(max_length=100, primary_key=True)
    data_level = models.PositiveIntegerField(blank=True, null=True)
    catagory_tree = models.CharField(validators=[validate_comma_separated_integer_list],max_length=11,default='')

class WeekSales(models.Model):
    class Meta:
        unique_together = ('date','section_name')

    date = models.ForeignKey(FileDate, on_delete=models.CASCADE)
    section_name = models.ForeignKey(OPRSave, on_delete=models.CASCADE)
    sale = models.DecimalField(max_digits=11,decimal_places=4)
    vat = models.DecimalField(max_digits=11,decimal_places=4)
    part = models.DecimalField(max_digits=8,decimal_places=5)
    margin = models.DecimalField(max_digits=11,decimal_places=4)

class YearSales(models.Model):
    class Meta:
        unique_together = ('date','section_name')

    date = models.ForeignKey(FileDate, on_delete=models.CASCADE)
    section_name = models.ForeignKey(OPRSave, on_delete=models.CASCADE)
    sale = models.DecimalField(max_digits=11,decimal_places=4)
    vat = models.DecimalField(max_digits=11,decimal_places=4)
    part = models.DecimalField(max_digits=8,decimal_places=5)
    margin = models.DecimalField(max_digits=11,decimal_places=4)
