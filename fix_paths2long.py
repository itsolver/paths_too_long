import os, csv
import pandas as pd
from datetime import datetime
import tkinter as tk
'''This uses substantial amounts of code from Stevoisiak's response in this thread:
https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter'''
class AppGui(tk.Tk):
    def __init__(self, csvfile):
        tk.Tk.__init__(self)
        # Eventual handlerdict structure: {'path': <str>, 'segments': <list>, 'paths_shared_with': <list>, 'max_length': <list>,
        # "to_correct": <str>, 'correction': <str>, 'correction_index' : <int>}
        self.csv = csvfile
        self.handlerdict = {}
        self._frame = None
        self.pathsDF = pd.read_csv(csvfile)
        if 'path_fix' not in self.pathsDF.columns.tolist():
            self.pathsDF['path_fix'] = None
            self.pathsDF['path_fix'] = self.pathsDF['path_fix'].astype('object')
        if self.pathsDF.dtypes.path_fix != 'object':
            self.pathsDF['path_fix'] = self.pathsDF['path_fix'].astype('object')
        self.segments = []
        #self.currentpathDF = pd.DataFrame(columns = ['segments', 'shared_with', 'fixed', 'solution'])
        self.extract_next_segs()
        self.switch_frame(ChooseSegmentFrame, params = self.handlerdict)

    def extract_next_segs(self):
        '''Finds the next empty row in the path_fix column of the dataframe and uses the data there to populate the handler
        dictionary'''
        if "path_fix" not in self.pathsDF.columns.tolist():
            print("Error: Necessary column missing")
        else:
            sharedcounts = []
            maxlengths = []
            if self.pathsDF[self.pathsDF.path_fix.isnull()].empty:
                print("no further paths require fixing. Remember to write your recent changes to the csv before quitting ")
            tofixindex = self.pathsDF[self.pathsDF.path_fix.isnull()].index[0]
            tofixpath = self.pathsDF.loc[tofixindex, 'Filepath']
            segmentlist = splitall(tofixpath)
            self.handlerdict['path'] = tofixpath
            self.handlerdict['segments'] = segmentlist
            for i, seg in enumerate(segmentlist): #loop to populate the sharedcountslist
                sharedDF = self.pathsDF.copy()
                #sharedDF["path_list"] = [splitall(x)[:segmentlist.index(seg) + 1] for x in sharedDF.Filepath.values.tolist()] #deprecated
                #recreates path up to and including the 'seg'
                inclusivepath = os.path.join(*segmentlist[:(i + 1)])
                path_contains = lambda i : inclusivepath in i[:len(inclusivepath)+1]
                sharedDF = sharedDF[sharedDF['Filepath'].apply(path_contains)]
                sharedcounts.append(sharedDF.shape[0])
                maxlengths.append(max([int(x) for x in sharedDF.Path_Length.values.tolist()])) #append max path length with each shared directory
            self.handlerdict['paths_shared_with'] = sharedcounts
            self.handlerdict['max_length'] = maxlengths

    def add_correction(self):
        def applycorrection(parametersdict, targetpathlist):
            '''uses values in parametersdict to fix the issues in targetpathlist'''
            pathindex = parametersdict['correction_index']
            if (targetpathlist[pathindex] == parametersdict['to_correct']) and isinstance(parametersdict['correction'], (str, int)):
                if len(str(parametersdict['correction'])) > 0: #if text was entered as
                    targetpathlist[pathindex] = str(parametersdict['correction'])
                else:
                    del targetpathlist[pathindex]
                newpath = os.path.join(*targetpathlist)
                if len(newpath) < 260:
                    return newpath
                else: return ''
            else:
                if targetpathlist[pathindex] != parametersdict['to_correct']:
                    try:
                        print(f"The directory to fix, {parametersdict['to_correct']}, doesn't match that at the same index, {str(pathindex)}, in this path" + os.linesep + f"{os.path.join(*targetpathlist)}")
                    except:
                        print(f"ERROR tocorrect - {type(parametersdict['to_correct'])}, path issue - {type(targetpathlist[pathindex])}")
                if not isinstance(parametersdict['correction'], (str, int)):
                    print(f"Error: correction replacement is the wrong datatype: {type(parametersdict['correction'])}")

        segmentlist = self.handlerdict['segments']
        index_to_correct = int(self.handlerdict["correction_index"])
        inclusivepath = os.path.join(*segmentlist[:index_to_correct + 1])
        path_contains = lambda i : inclusivepath in i[:len(inclusivepath)+1]
        rows_to_fix = self.pathsDF[self.pathsDF['Filepath'].apply(path_contains)].index.tolist()
        for rowindex in rows_to_fix:
            rowpathlist = splitall(self.pathsDF.loc[rowindex, 'Filepath'])
            self.pathsDF.at[rowindex, 'path_fix'] = applycorrection(self.handlerdict, rowpathlist)

    def switch_frame(self, frame_class, params = None):
        """Destroys current frame and replaces it with a new one."""
        if isinstance(params, dict):
            new_frame = frame_class(self, params)
        elif isinstance(params, tuple):
            new_frame = frame_class(self, params)
        else:
            new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def edit_segment_return(self, frame_class, paramsdict = None):
        """Destroys current frame and replaces it with a new one."""
        if isinstance(paramsdict, dict):
            new_frame = frame_class(self, paramsdict)
        else:
            new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class ChooseSegmentFrame(tk.Frame):
    def __init__(self, master, paramsdict):
        tk.Frame.__init__(self, master)
        self.segments = paramsdict['segments']

        tk.Label(self, text=os.path.join(*self.segments), font='Helvetica 9 bold').grid(row = 0, column = 1, columnspan = len(self.segments))
        tk.Label(self, text = "Files with shared path:", font='Helvetica 8 bold').grid(row = 2, column = 0)
        tk.Label(self, text="Max Length with shared path:", font='Helvetica 8 bold').grid(row=3, column=0)
        for segmentindex, dir in enumerate(self.segments):
            sharednum = str(paramsdict['paths_shared_with'][segmentindex])
            maxlen = str(paramsdict['max_length'][segmentindex])
            #sharednum = str(paramsdict['paths_shared_with'][self.segments.index(dir)]) #delete if line above works
            buttext = dir
            if self.segments.count(dir) != 1:
                buttext  = f"{dir} ({str(segmentindex)})"
            my_button = tk.Button(self, text=buttext)
            my_button.segment_index = segmentindex
            my_button.directory = dir
            #my_button.configure(command=lambda button=my_button: master.switch_frame(FixSegmentFrame, (button['text'], button.segment_index))) #before version
            my_button.configure(command=lambda button=my_button: master.switch_frame(FixSegmentFrame, (button.directory, button.segment_index)))
            #self.button.configure(command=lambda: master.switch_frame(FixSegmentFrame, [button['text']]))
            my_button.grid(row = 1, column = segmentindex+1)
            tk.Label(self, text=sharednum).grid(row=2, column=segmentindex+1)  # adds directory labels above buttons
            tk.Label(self, text=maxlen).grid(row=3, column=segmentindex+1)

class FixSegmentFrame(tk.Frame):
    def __init__(self, master, segmenttuple):
        self.segment = segmenttuple[0]
        self.segment_index = segmenttuple[1]
        tk.Frame.__init__(self, master)
        tk.Label(self, text=self.segment).pack(side="top", fill="x", pady=10)
        self.entry = tk.Entry(self)
        self.entry.insert(0, self.segment)
        self.entry.pack()
        def callback(): return (self.entry.get(), self.segment_index)
        tk.Button(self, text="enter", command=lambda entry = self.entry: self.enter_click(callback())).pack()
        tk.Button(self, text="write changes to csv", command= self.save_to_csv).pack()
        #tk.Button(self, text="enter", command= lambda entryclick: self.enter_click(callback())).pack()

    def enter_click(self, correcttuple):
        '''function for 'enter' button when clicked'''
        correction = correcttuple[0]
        self.master.handlerdict["to_correct"] = self.segment
        self.master.handlerdict["correction"] = correction
        self.master.handlerdict['correction_index'] = correcttuple[1]
        self.master.add_correction()
        self.master.extract_next_segs()
        self.master.switch_frame(ChooseSegmentFrame, self.master.handlerdict)
        #Todo: what happens when we run out of rows to fix?

    def save_to_csv(self):
        self.master.pathsDF.to_csv(self.master.csv)
        print("CSV written successfully.")

'''
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is page two").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(ChooseSegmentFrame)).pack()
'''


class pathFixer:
    def __init__(self):
        pass

    def get_path_data(self, csvfile = None):
        if csvfile == None:
            csvfile = self.csvfilename
        csvpath = os.path.join(os.getcwd(), csvfile)
        self.files_2longDF = pd.read_csv(csvpath)
        return(self)

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


if __name__ == "__main__":
    csvfilename = "sdrive_2long_test2.csv"
    csvpath = establish_csv(csvfilename, ['segments', 'shared_with', 'fixed', 'solution', 'path_fix'])
    app = AppGui(csvpath)
    app.mainloop()
