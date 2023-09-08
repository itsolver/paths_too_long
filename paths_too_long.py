import os, csv
import pandas as pd
from datetime import datetime

def user_csv_choice():
    '''Prompts user for csv file and checks that the user string corresponds to a file in current directory'''
    aPrompt = "Enter csv filename including its extension." + os.linesep + "(The file must be in same directory as this script.)"
    userStr = input(aPrompt)
    try:
        os.path.isfile(os.path.join(os.getcwd(), userStr))
    except:
        print("error occured with that filename. Try again.")
        user_csv_choice()

    return userStr

def user_chooses_yes(promptText):
    '''asks yes or no question to user and returns 'True' for a yes answer and 'False' for a no answer'''
    yesNo = ['yes', 'y', 'Yes', 'Y', 'No', 'no', 'n', 'N']
    response = ''
    while response not in yesNo:
        response = input(promptText)
    if response in yesNo[4:]:
        return False
    else:
        return True

def establish_csv(defaultName, columnNamesList):
    csvPrompt = "Use %s?" % defaultName

    if user_chooses_yes(csvPrompt):
        csvFile = defaultName
    else:
        csvFile = user_csv_choice()
    csvPath = os.path.join(os.getcwd(), csvFile)

    if not os.path.isfile(csvPath):
        blankCSVdf = pd.DataFrame(columns=columnNamesList)
        blankCSVdf.to_csv(csvPath, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return csvPath

class longPathSearcher:
    def __init__(self, search_start, results_csv_name):
        self.starting_dir = search_start
        self.results_csv = results_csv_name
        self.resultsDF = None

    def collect_file_data(self, chosenDir = None, DF = None, ignoreThumbs=True):
        '''adapted version of build_file_dataframe used in other scripts'''
        def timestamp_to_date(timestamp):
            DT = datetime.fromtimestamp(timestamp)
            return DT.strftime("%m/%d/%Y, %H:%M:%S")

        def file_data_to_list(root, file):
            filePath = os.path.join(root, file)
            extension = file.split('.')[-1]
            extension = extension.lower()
            name = '.'.join(file.split('.')[:-1])
            now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            try:
                fileStats = os.stat(filePath)
                fileSize = str(fileStats.st_size)
                fileSize.zfill(15)
                fileCreationTime = timestamp_to_date(fileStats.st_ctime)
                fileModifiedTime = timestamp_to_date(fileStats.st_mtime)
                error = None
                retrieved = now
            except:
                fileSize = "123456789"
                fileSize.zfill(15)
                fileCreationTime = now
                fileModifiedTime = now
                error = "error getting file metadata"
                retrieved = now
            return [filePath, file, name, extension, fileSize, fileCreationTime, fileModifiedTime, retrieved, error]

        if chosenDir == None:
            chosenDir = self.starting_dir
        if DF == None:
            DF = self.resultsDF
        fileList = []
        for root, dirs, files in os.walk(chosenDir):
            if files:
                for file in files:
                    if ignoreThumbs:
                        if file.split('.')[0] != "Thumbs":
                            fileList.append(file_data_to_list(root, file))
                    else:
                        fileList.append(file_data_to_list(root, file))

        self.fileDF = pd.DataFrame(fileList,
                              columns=["Filepath", "File", "Name", "Extension", "Filesize", "Created", "Modified",
                                       "Retrieved", "Error"])
        if DF is not None:
            fileDF = DF.append(self.fileDF)
            self.fileDF.drop_duplicates(subset="Filepath", keep='first', inplace=True)
        return self


    def remove_acceptable_paths(self):
        if isinstance(self.fileDF, pd.DataFrame):
            self.fileDF["Path_Length"] = [len(ii) for ii in  self.fileDF["Filepath"]]
            self.fileDF = self.fileDF[self.fileDF["Path_Length"] >= 260]
        else:
            print("Error: no dataframe detected.")
        return self


if __name__ == '__main__':
    targetDir = ''
    csvFile = "st_2long.csv"

    while not os.path.isdir(targetDir):
        targetDir = input("Enter path to scan: ")

    results_csv = establish_csv(csvFile, ["Filepath", "File", "Name", "Extension", "Filesize", "Created", "Modified", "Retrieved", "Error", "Path_Length"])
    constdoc = longPathSearcher(targetDir, results_csv)
    constdoc.collect_file_data().remove_acceptable_paths()
    longpathDF = pd.read_csv(results_csv)
    longpathDF = pd.concat([longpathDF, constdoc.fileDF], ignore_index=True)
    longpathDF.drop_duplicates(subset=["Filepath", "Extension", "Modified"], keep='first', inplace=True)
    longpathDF.to_csv(results_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
