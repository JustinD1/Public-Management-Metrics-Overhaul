from django.conf import settings

from home.models import StoreSave,FileDate
from OPR2.models import Document

from xlrd.sheet import ctype_text
import xlrd, os
import datetime

from scripts.BackendHandleOPR import mkSaterdayList, check_row

# [#0001] File upload to database and check.

#############################################################
######################## [#0001] ############################
#############################################################
# This is to handle the uploaded file and checks to make sure that i is an OPR file

def uploadFile(filepath,noteReport,errorReport):
    #A simple check to make sure that the uploaded file is infact a excel document and not something else.
    if filepath.content_type != "application/vnd.ms-excel":
        errorReport.append("%s: \n Uploaded file is not an excel document"%(str(filepath).split("/")[-1]))
        return

    #An other check in the form of a try expression. If xlrd can't access the
    #file in question then it returns a cannot access error to the sender.
    try:
        x1_workbook = xlrd.open_workbook(filepath.temporary_file_path())
        x1_sheet = x1_workbook.sheet_by_index(0)
    except:
        errorReport.append("%s: \n Uploaded file can't be opened."%(str(filepath).split("/")[-1]))
        return

    ##~This will work out the maximum number of row that have data.
    count = 0
    print("Entering row max length check")
    while count < 10:
        x1_col = x1_sheet.col(count)
        if count == 0:
            maxColCell = len(x1_col) - 1
        elif maxColCell < len(x1_col) - 1:
            maxColCell = len(x1_col) - 1

        count += 1

    #This will read the custom header of the opr and pull from it the store name,date
    count=0
    dateToggle = False
    storeToggle = False
    print("Entering header cycle loop")
    while count < maxColCell:
        x1_row = x1_sheet.row(count)
        #check if the row is all empty and skip to the next row if it is.
        if check_row(row=x1_row):
            count += 1
            continue

        #Once a row has data it will read each column and save needed data.
        for idx,cell_obj in enumerate(x1_row):
            cell_type_str = ctype_text.get(cell_obj.ctype,'unknown type')
            strTemp = cell_obj.value

            #The excel doc is riddled with gaps in the columns so we want to
            #skip them.
            if cell_type_str == "empty":
                continue

            #Once the store and date tag have been reached we save the values.
            if str(strTemp).lower() == "date":
                print("Found the date of the opr:")
                dateToggle = True
            #The next value in this row will be the date of the opr
            elif dateToggle:
                date_split = cell_obj.value.split("/")
                file_date = datetime.date(int(date_split[2]),int(date_split[1]),int(date_split[0]))
                print(file_date)
                print(" ")
                saterdaydict = mkSaterdayList(int(date_split[2]))
                if file_date not in saterdaydict:
                    errorReport.append("%s: This is not a Saterday OPR. You can only upload Saterday"%(str(filepath).split("/")[-1]))
                    return
                dateToggle = False
                break
            if str(strTemp).lower() == "store":
                print("Found the store name and code:")
                storeToggle = True
            #The next value in this row will be the name of the store
            elif storeToggle:
                oprStore = cell_obj.value.replace(" ","")
                print(oprStore)
                print(" ")
                storeToggle = False
                break

        if 'oprStore' in locals() and 'file_date' in locals():
            print("Both naming objects found. Creating and exiting")
            description = '_'.join([oprStore,file_date.strftime("%Y-%m-%d")])
            if Document.objects.filter(description=description).exists():
                errorReport.append("%s: This OPR is in the database skipping this opr."%(str(filepath).split("/")[-1]))
                return
            else:
                post = Document.objects.create(description=description,document=filepath)
                post.save()
                return
        count+=1
    errorReport.append("%s: This OPR doesn't have the expected header information and was not saved."%(str(filepath).split("/")[-1]))
    return
