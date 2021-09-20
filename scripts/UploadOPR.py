from scripts.BackendHandleOPR import *

def xls2database():
    errorReport = []
    noteReport = []
    HandleOPRFile(errorReport,noteReport)
    return

# databaseUpdated = updateBD(filepath=post.document)
# CreateCatagory(opr=databaseUpdated)
# PopulateComparison(opr=databaseUpdated)
# weeklyTotal(opr=databaseUpdated)
