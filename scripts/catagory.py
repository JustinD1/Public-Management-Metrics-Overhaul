from OPR2.models import OPRSave, WeekSales
from home.models import FileDate

def catagory_set(name,dept,sub,com,fam):
    current_object = OPRSave.objects.get(name=name.name, data_level=name.data_level)
    if current_object.catagory_tree != '':
        return 'Object is apart of an existing tree'

    while True:
        catagory_exists = OPRSave.objects.filter(catagory_tree=','.join(str(x) for x in [dept,sub,com,fam])).exists()
        print(catagory_exists)
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


dates = FileDate.objects.all()
for a in dates:
    dept = 0
    sub = 0
    com = 0
    fam = 0
    for item in WeekSales.objects.filter(date=a).order_by("pk"):
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
        print("%s" %(text))
