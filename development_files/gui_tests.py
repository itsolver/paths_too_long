import os, csv
import pandas as pd
from datetime import datetime
from tkinter import *
'''
class guiWindow:
    def __init__(self):
        pass

class pathFixer:
    def __init__(self):
        pass

    def start_gui(self):
        self.window = Tk()
        self.window.title("Fix Paths")

    def fields_example(self):
        def click():
            sometext = entry1.get()
            print(sometext)

        label1 = Label(self.window, text = "Enter here:")
        label2 = Label(self.window, text = "more text:")
        check = Checkbutton(self.window, text = "Keep signed in.")
        entry1 = Entry(self.window)
        entry2 = Entry(self.window)
        button1 = Button(self.window, text = "Get entry", command = click )
        label1.grid(row = 0, sticky = E)
        label2.grid(row=1, sticky=E)
        entry1.grid(row = 0, column =1)
        entry2.grid(row=1, column =1)
        check.grid(row = 2, columnspan = 2)
        button1.grid(row = 3)
        self.window.mainloop()

    def click_button(self):
        def print_click():
            print("You clicked a button!")
        button1 = Button(self.window, text = "Click Me", command = self.buttons_example)
        button1.pack()
        self.window.mainloop()

    def buttons_example(self):
        topframe = Frame(self.window)
        topframe.pack()
        bottomframe = Frame(self.window)
        bottomframe.pack(side = BOTTOM)
        button1  = Button(topframe, text = "butt1", fg = "red")
        button2 = Button(topframe, text="butt2", fg="blue")
        button3 = Button(topframe, text="butt3", fg="green")
        button4 = Button(bottomframe, text="butt4", fg="purple")

        button1.grid(row = 0)
        button2.grid(row = 0, column = 1)
        button3.grid(row = 1)
        button4.grid(row= 1, column = 1)



        testlabel = Label(topframe, text = "test label")
        testlabel.grid(row = 2)
        self.window.mainloop()
        pass

    def get_path_data(self, csvfile = None):
        if csvfile == None:
            csvfile = self.csvfilename
        csvpath = os.path.join(os.getcwd(), csvfile)
        self.files_2longDF = pd.read_csv(csvpath)
        return(self)






if __name__ == '__main__':
    constdoc = pathFixer()
    constdoc.start_gui()
    #constdoc.buttons_example()
    constdoc.fields_example()
    #constdoc.click_button()
'''
'''
def raise_frame(frame):
    frame.tkraise()

root = Tk()

f1 = Frame(root)
f2 = Frame(root)
f3 = Frame(root)
f4 = Frame(root)

for frame in (f1, f2, f3, f4):
    frame.grid(row=0, column=0, sticky='news')

Button(f1, text='Go to frame 2', command=lambda:raise_frame(f2)).pack()
Label(f1, text='FRAME 1').pack()

Label(f2, text='FRAME 2').pack()
Button(f2, text='Go to frame 3', command=lambda:raise_frame(f3)).pack()

Label(f3, text='FRAME 3').pack(side='left')
Button(f3, text='Go to frame 4', command=lambda:raise_frame(f4)).pack(side='left')

Label(f4, text='FRAME 4').pack()
Button(f4, text='Goto to frame 1', command=lambda:raise_frame(f1)).pack()

raise_frame(f1)
root.mainloop()

import tkinter as tk
class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is the start page").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Open page one",
                  command=lambda: master.switch_frame(PageOne)).pack()
        tk.Button(self, text="Open page two",
                  command=lambda: master.switch_frame(PageTwo)).pack()

class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is page one").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage)).pack()

class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is page two").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage)).pack()

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()

class appGUI(tk.Tk):
    def __init__(self, nodes):
        #self.window.title("Fix Paths")
        self._frame = None
        self.nodes = nodes
        self.switch_frame(pickSolutionFrame, [nodes])

    def switch_frame(self, frame_class, frame_params):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self, *frame_params)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def node_buttons(self, row, button_command, nodelist = None):
        if nodelist == None:
            nodelist = self.nodes
        if isinstance(nodelist, list):
            self.nodes = nodelist
        self.node_butts = []
        for node in nodelist:
            nodename = name_from_node(node)
            butt = guiButton(self.window, butt_label = nodename, butt_row =row, butt_column = nodelist.index(node), butt_command = button_command)
            self.node_butts.append(butt)
        for bttn in self.node_butts:
            bttn.add_to_grid()

    def start_gui(self):
        self.window.mainloop()


class pickSolutionFrame(tk.Frame):
    def __init__(self, master, pathlist):
        tk.Frame.__init__(self, master, cnf={})
        self.label = tk.Label(self, text=str(os.path.join(*pathlist)))
        self.label.pack(side="top", fill="x", pady=10)
        self.nodes = pathlist
        self.node_buttons(row = 4, button_command=self.button_click(nodename), nodelist=self.nodes)

    def node_buttons(self, row, button_command, nodelist = None):
        if nodelist == None:
            nodelist = self.nodes
        if isinstance(nodelist, list):
            self.nodes = nodelist
        self.node_butts = []
        for node in nodelist:
            nodename = name_from_node(node)
            butt = guiButton(self.window, butt_label = nodename, butt_row =row, butt_column = nodelist.index(node), butt_command =  button_command)
            self.node_butts.append(butt)
        for bttn in self.node_butts:
            bttn.add_to_grid()

    def button_click(self, nodestr):
        pass




class guiButton:
    def __init__(self, butt_window, node, butt_row, butt_column, butt_command):
        self.windowframe = butt_window
        self.node = node
        self.label = self.name_from_node(node)
        self.row = butt_row
        self.column = butt_column
        self.command = butt_command
        self.button = tk.Button(self.windowframe, text = self.label, command = self.command)

    def name_from_node(self, nodestr):
        if len(nodestr) < 7:
            return nodestr
        else:
            return nodestr[:6] + "..."

    def add_to_grid(self):
        self.button.grid(row = self.row, column = self.column)
        return self
'''

class ChooseSegmentFrame(tk.Frame):
    '''frame before trying to add segment index'''
    def __init__(self, master, paramsdict):
        tk.Frame.__init__(self, master)
        self.segments = paramsdict['segments']

        tk.Label(self, text=os.path.join(*self.segments)).grid(row = 0, columnspan = len(self.segments))
        for dir in self.segments:
            sharednum = str(paramsdict['paths_shared_with'][self.segments.index(dir)])
            my_button = tk.Button(self, text=dir)
            my_button.configure(command=lambda button=my_button: master.switch_frame(FixSegmentPage, [button['text']]))
            #self.button.configure(command=lambda: master.switch_frame(FixSegmentPage, [button['text']]))
            my_button.grid(row = 1, column = self.segments.index(dir))
            tk.Label(self, text=sharednum).grid(row=2, column=self.segments.index(dir))  # adds directory labels above buttons