import os, csv, glob, shutil
import pandas as pd
from datetime import datetime
import numpy as np
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

def splitall(path):
    '''splits a path into each piece that corresponds to a mount point, directory name, or file'''
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def where_lists_differ(list1, list2):
    '''Returns first instance of a difference between list1 and list2'''
    for index, (first, second) in enumerate(zip(list1, list2)):
        if first != second:
            return (index, first, second)

def clean_path(path):
    '''Process a path string such that it can be used regardless of the os and regardless of whether its length
    surpasses the limit in windows file systems'''
    path = path.replace('/',os.sep).replace('\\',os.sep)
    if os.sep == '\\' and '\\\\?\\' not in path:
        # fix for Windows 260 char limit
        relative_levels = len([directory for directory in path.split(os.sep) if directory == '..'])
        cwd = [directory for directory in os.getcwd().split(os.sep)] if ':' not in path else []
        path = '\\\\?\\' + os.sep.join(cwd[:len(cwd)-relative_levels]\
                         + [directory for directory in path.split(os.sep) if directory!=''][relative_levels:])
    return path

def change_path_dir(og_path, new_path):
    origin_dir = os.getcwd() #might be needed if moving files requires moving to directory

    og_list = splitall(og_path)
    new_list = splitall(new_path)
    changeindex = where_lists_differ(og_list, new_list)[0]
    og_path = os.path.join(*og_list[:changeindex + 1])
    new_path = os.path.join(*new_list[:changeindex + 1])
    clean_og = clean_path(og_path)
    clean_new = clean_path(new_path)
    clean_og_loc = clean_path(og_path)
    result_tuple = (True, None)
    if os.path.exists(new_path):
        emessage = f"The desired path, '{new_path}', already exists"
        print(emessage)
        result_tuple = (False, emessage)
    if not os.path.exists(clean_og_loc):
        emessage = f'{og_path} does not exist'
        print(emessage)
        result_tuple = (False, emessage)
    if os.path.exists(clean_og_loc) and not os.path.exists(new_path):
        try:
            #os.chdir(new_path_loc) #move to containing folder
            os.rename(clean_og_loc, new_path)
            #os.chdir(origin_dir)
        except Exception as e:
            emessage = e.message
            result_tuple = (False, emessage)
    return result_tuple

def unnest_dir(og_path, new_path):
    ''''''
    og_list = splitall(og_path)
    new_list = splitall(new_path)
    changeindex = where_lists_differ(og_list, new_list)[0] #index where change is to be made
    og_location = os.path.join(*og_list[:changeindex + 2])
    new_location = os.path.join(*og_list[:changeindex])
    result_tuple = (True, None)
    #ToDo: add try and except to return errors. What happens if new_location or og_location do not exist? Second try-except for clean path
    if os.path.exists(clean_path(new_location)):
        #files = glob.glob(og_location)
        try:
            shutil.move(og_location, new_location)
        except Exception as e:
            try:
                shutil.move(clean_path(og_location), new_location)
            except Exception as e2:
                emessage = str(e2)
                result_tuple = (False, emessage)
    else:
        emessage
        result_tuple = (False, emessage)
    return result_tuple

class pathfixer:
    def __init__(self, dataframe):
        self.pathsDF = dataframe
        dfcolumns2add = ['date_corrected', 'intermediary_paths', 'result_path', 'change_depth', 'errors']
        for label in dfcolumns2add:
            if label not in self.pathsDF.columns.tolist():
                self.pathsDF[label] = ''
        #self.pathsDF['path_fix'].replace('', np.nan, inplace=True)
        #self.pathsDF['path_fix'].replace(None, np.nan, inplace=True)
        self.pathsDF.path_fix.fillna(value=pd.NA, inplace=True)
        self.pathsDF.dropna(subset=['path_fix'], inplace=True)
        #handler dict contains {'long_path':<str>, 'path_correction': <str>}
        self.handlerdict = {}
        self.get_change_depths()
        self.max_change_depth = max(self.pathsDF.change_depth.values.tolist())

    def get_change_depths(self):
        def where_lists_differ(list1, list2):
            for index, (first, second) in enumerate(zip(list1, list2)):
                if first != second:
                    return (index,  first, second)

        for rowindex, row in self.pathsDF.iterrows():
            where2correct = where_lists_differ(splitall(row['Filepath']), splitall(row['path_fix']))
            self.pathsDF.at[rowindex, 'change_depth'] = where2correct[0]

    def correct_all(self):
        '''Starting with the deepest directory changes, this iterates through directory change depth (from deepest to shallowest). For each row with each depth, all other paths with same
        path to the change being made are changed.
        THe depth loop allows us to work back from deepest to shallowest change.
        The samedepth loop determines which fix will be implemented and implements all changes
        The sharedDF loop records the change in the appropriate self.pathsDF cells for all the files that were affected by the change'''

        self.correction_depth_row_index = {} #keeps track of which rows were fixed for each correction index. {depth: [list of row indices]}
        currentdt = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        for depth in range(self.max_change_depth, 0, -1):
            #starting with deepest changes we will move in to the mountpoint...
            same_depthDF = self.pathsDF[self.pathsDF['change_depth'] >= depth] #DF with only those paths that have changes at the same path depth
            samedepthindex = same_depthDF.index.values.tolist()
            if depth not in self.correction_depth_row_index:
                self.correction_depth_row_index[depth] = [] #for seeing which rows were changed during each depth iteration
            for sdindex, sdrow in same_depthDF.iterrows():
                # if row has not been processed at this depth before. Need this to avoid reprocessing rows that were already processed \
                # ...in the loop over shared path.
                if sdindex not in self.correction_depth_row_index[depth]:
                    current_location = sdrow['Filepath']
                    og_seglist = splitall(current_location)
                    fix_list = splitall(sdrow['path_fix'])
                    inclusivepath = os.path.join(*og_seglist[:(depth + 1)]) #original path to the directory in question
                    #if/else statement below to determine if process is to remove folder from path (unnest) or rename folder
                    #ToDo: what if previous file position did not mean it was going to be changed with this change but subsequent changes moved it into path of this change?
                    if len(sdrow['intermediary_paths']) > 0:
                        if isinstance(sdrow['intermediary_paths'], list):
                            current_location = sdrow['intermediary_paths'][-1]
                        if isinstance(sdrow['intermediary_paths'], str):
                            current_location = sdrow['intermediary_paths']
                    current_list = splitall(current_location)
                    clean_current_loc = clean_path(current_location)  # create path accessible by python if path length is too long.
                    unnested =False
                    error_occurred = False
                    if len(og_seglist) == len(fix_list):  # check if the path change removes dir
                        path_to_correction = os.path.join(*fix_list[:depth + 1])
                        changed_path_list = current_list[:depth + 1]
                        changed_path = os.path.join(*changed_path_list)
                        adjusted_fix = path_to_correction + current_location[len(changed_path):]
                        if current_location != adjusted_fix:
                            if not os.path.exists(clean_current_loc):
                                errormessage = f"Error: the file originally located here: \n{sdrow['Filepath']} \n ...is missing. Expected to be here: \n{current_location}"
                                print(errormessage)
                                self.pathsDF.at[sdindex, 'errors'] = errormessage
                            elif os.path.exists(clean_current_loc):
                                # record each row that has been changed in the dict. Dict is then used to avoid redundant efforts at changing path
                                fixresults = change_path_dir(current_location, adjusted_fix)
                                if fixresults[0]:
                                    # add new location to intermediary paths
                                    sd_depth_finish = self.correction_depth_row_index[depth]
                                    sd_depth_finish.append(sdindex)
                                    self.correction_depth_row_index[depth] = sd_depth_finish
                                    # record intermediary paths to dataframe
                                    int_paths = sdrow['intermediary_paths']
                                    if int_paths == '':
                                        int_paths = []
                                    if not isinstance(int_paths, list):
                                        int_paths = [int_paths]
                                    if adjusted_fix not in int_paths:
                                        int_paths.append(adjusted_fix)
                                    self.pathsDF.at[sdindex, 'intermediary_paths'] = int_paths
                                    same_depthDF.at[sdindex, 'intermediary_paths'] = int_paths
                                    self.pathsDF.at[sdindex, 'result_path'] = adjusted_fix
                                    self.pathsDF.at[sdindex, 'date_corrected'] = currentdt
                                else:
                                    self.pathsDF.at[sdindex, 'errors'] = fixresults[1]
                                    error_occurred =True
                    if len(og_seglist) > len(fix_list): #Mostly repeat of above commands but for an unnesting operation
                        unnested = True
                        path_to_correction = os.path.join(*fix_list[:depth])
                        changed_path_list = current_list[:depth + 1]
                        changed_path = os.path.join(*changed_path_list)
                        adjusted_fix = path_to_correction + current_location[len(changed_path):]
                        if current_location != adjusted_fix:
                            if not os.path.exists(clean_current_loc):
                                errormessage = f"Error: the file originally located here: \n{row['Filepath']} \n ...is missing. Expected to be here: \n{current_location}"
                                print(errormessage)
                                self.pathsDF.at[sharedrowindex, 'errors'] = errormessage
                            elif os.path.exists(clean_current_loc):
                                # record each row that has been changed in the dict. Dict is then used to avoid redundant efforts at changing path
                                fixresults = unnest_dir(current_location, adjusted_fix)
                                if fixresults[0]: #Todo: need to correct this per unnest function
                                    # add new location to intermediary paths
                                    sd_depth_finish = self.correction_depth_row_index[depth]
                                    sd_depth_finish.append(sdindex)
                                    self.correction_depth_row_index[depth] = sd_depth_finish
                                    # record intermediary paths to dataframe
                                    int_paths = sharedrow['intermediary_paths']
                                    if int_paths == '':
                                        int_paths = []
                                    if not isinstance(int_paths, list):
                                        int_paths = [int_paths]
                                    if adjusted_fix not in int_paths:
                                        int_paths.append(adjusted_fix)
                                    self.pathsDF.at[sdindex, 'intermediary_paths'] = int_paths
                                    same_depthDF.at[sdindex, 'intermediary_paths'] = int_paths
                                    self.pathsDF.at[sdindex, 'result_path'] = adjusted_fix
                                    self.pathsDF.at[sdindex, 'date_corrected'] = currentdt
                                else:
                                    self.pathsDF.at[sdindex, 'errors'] = fixresults[1]
                                    error_occurred = True
                    if len(og_seglist) < len(fix_list):
                        error_txt = f"The row {sdindex} generated an solution that is longer than the original"
                        self.pathsDF.at[sdindex, 'errors'] = error_txt
                        print(error_txt)
                    if not error_occurred:
                        sharedDF = self.pathsDF.copy()
                        path_contains = lambda i : inclusivepath in i[:len(inclusivepath)+1]
                        sharedDF = sharedDF[sharedDF['Filepath'].apply(path_contains)]
                        ####################################################################################################
                        ####################################################################################################
                        for sharedrowindex, sharedrow in sharedDF.iterrows():
                            #[i for i in range(len(sharedrow['path_fix'])) if sharedrow['Filepath'][i] != sharedrow['path_fix'][i]]
                            previous_location = sharedrow['Filepath']
                            #if sharedrow['intermediary_paths'] and len(sharedrow['intermediary_paths']) > 0:
                            if len(sharedrow['intermediary_paths']) > 0:
                                if isinstance(sharedrow['intermediary_paths'], list):
                                    previous_location = sharedrow['intermediary_paths'][-1]
                                if isinstance(sharedrow['intermediary_paths'], str):
                                    previous_location = sharedrow['intermediary_paths']
                            previous_list = splitall(previous_location)
                            previous_path_list = previous_list[depth + 1:]
                            new_loc_list = fix_list[:depth + 1] + previous_path_list
                            if unnested:
                                new_loc_list = fix_list[:depth] + previous_path_list
                            new_path = os.path.join(*new_loc_list)
                            new_path_clean = new_path
                            if len(new_path) > 250:
                                new_path_clean = clean_path(new_path)
                            if not os.path.exists(new_path_clean):
                                errormessage = f"Error: the file originally located here: \n{sharedrow['Filepath']} \n ...has been misplaced. Expected to be here: \n{new_path}"
                                print(errormessage)
                                self.pathsDF.at[sharedrowindex, 'errors'] = errormessage
                            elif os.path.exists(new_path_clean):
                                    #add new location to intermediary paths
                                    shared_depth_finish = self.correction_depth_row_index[depth]
                                    shared_depth_finish.append(sharedrowindex)
                                    self.correction_depth_row_index[depth] = shared_depth_finish
                                    # record intermediary paths to dataframe
                                    int_paths = sharedrow['intermediary_paths']
                                    if int_paths == '':
                                        int_paths = []
                                    if not isinstance(int_paths, list):
                                        int_paths = [int_paths]
                                    if new_path not in int_paths:
                                        int_paths.append(new_path)
                                    self.pathsDF.at[sharedrowindex, 'intermediary_paths'] = int_paths
                                    same_depthDF.at[sharedrowindex, 'intermediary_paths'] = int_paths
                else:
                    continue

    def save_df(self, savepath):
        csvDF = self.pathsDF.copy()
        columns2drop = ['change_depth']
        for col in columns2drop:
            csvDF.drop(col, axis = 'columns', inplace =True)
        csvDF.to_csv(savepath)
        print(f"Dataframe successfully saved in following location \n{savepath}")

if __name__ == "__main__":
    csvfilename = "sdrive_2long_test2.csv"
    csvpath = establish_csv(csvfilename, ['segments', 'shared_with', 'fixed', 'solution', 'path_fix'])
    paths2fixDF = pd.read_csv(csvpath)
    constdoc = pathfixer(paths2fixDF)
    constdoc.get_change_depths()
    constdoc.correct_all()
    constdoc.save_df(csvpath)
    