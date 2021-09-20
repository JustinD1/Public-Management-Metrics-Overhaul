from django.conf import settings

from home.models import *
from OPR2.models import *

import xlrd, os, glob
from xlrd.sheet import ctype_text
from os import listdir
import datetime

def mkSaterdayList(year):
    year=int(year)
    #Build a list of all saterdays in the year.
    firstSat = datetime.date(int(year),1,1)
    firstSat += datetime.timedelta(days = (5 - firstSat.weekday() + 7)% 7)
    saterdaydict = {}
    count = 0
    while firstSat.year == year:
        count += 1
        saterdaydict[firstSat] = count
        firstSat += datetime.timedelta(days = 7)
        if firstSat > datetime.date.today():
            break
    return saterdaydict

def check_row(row):
    for item in row:
        cell_type_str = ctype_text.get(item.ctype,'unknown type')
        if cell_type_str != 'empty':
            return False

def updateBD(filepath):
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
                dateToggle = True
            elif dateToggle:
                date_split = cell_obj.value.split("/")
                file_date = datetime.date(int(date_split[2]),int(date_split[1]),int(date_split[0]))
                saterdaydict = mkSaterdayList(int(date_split[2]))
                if file_date not in saterdaydict:
                    return "Uploaded OPR is not a Saterday OPR"
                dateToggle = False
                break
            if str(strTemp).lower() == "store":
                storeToggle = True
            elif storeToggle:
                oprStore = cell_obj.value.replace(" ","")
                # # print(settings.MEDIA_ROOT)
                # # print(str(filepath))
                # post = Document.objects.get(document=str(filepath))
                # post.description = oprStore
                # post.save()
                storeToggle = False
                break

            #once the row holding all the column titles is reach we toggle
            #rowselect. This save the departments and adds in sections depending
            #if the OPR has day week year columns. We also want to save the
            #column index number so any blank values under a title is entered
            #as a blank value rather than skipping it.
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

    #Depending on the type of opr we need to create different structure
    # if dayToggle:
    #     keyList = keyList + ['daySale','dayVat','dayPart','dayMargin','dayMarginPrec']
    # if weekToggle:
    #     keyList = keyList + ['weekSale','weekVat','weekPart','weekMargin','weekMarginPrec']
    # if yearToggle:
    #     keyList = keyList + ['yearSale','yearVat','yearPart','yearMargin','yearMarginPrec']

    ##~Check if the store exists and creates/appends the opr
    #
    store_name = oprStore.split('-')
    storeDB,created = StoreSave.objects.get_or_create(
        store_town=store_name[1].strip(),
        store=store_name[0].strip()
    )

    if FileDate.objects.filter(store=storeDB,date=file_date).exists():
        dateDB = FileDate.objects.get(store=storeDB,date=file_date)
        if dateDB.data_exists:
            created = False
        else:
            dateDB.data_exists = True
            dateDB.save()
            created = True
    else:
        dateDB,created = FileDate.objects.get_or_create(
            store=storeDB,
            date=file_date,
            data_exists = True,
            file_type="OPR",
            financial_year=date_split[2],
            week_number=saterdaydict[file_date]
            )

    if not created:
        print("Skipping to the next non-entered opr")
        print(" ")

        return

    breakToggle = False
    count -= 1
    while count < maxColCell:
        count += 1
        skip_row = True
        # print(count)
        values = []
        blankNumberToggle = 0
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
        print("Name: %s, Data level: %d" %(name,data_level))
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
    return "File has been uploaded."

os.chdir("OPR_Batch")
for file in glob.glob("*.xls"):

    print("Reading in file %s" % file)
    update = updateBD(filepath=file)
