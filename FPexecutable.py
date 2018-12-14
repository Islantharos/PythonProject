import tkinter as tk # a python gui framework 
import uproot #an interface between root and python code 
import pandas as pd#a convenient data processing tool
import matplotlib.pyplot as plt#standard plotting toolbox
import numpy as np#a numerical python tool
from scipy.optimize import minimize#useful fittings(delete later)
import matplotlib # redundancy for the full plotting toolbox
import tkinter.filedialog #nonstandard file accessing tool for tkinter
import tkinter.ttk #nonstandard combobox library for tkinter
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
#This file uses a mix of the admittedly spotty information available at http://effbot.org/tkinterbook/tkinter-classes.htm
#and the information avaiable in the main python documentation

#this can and should be edited by the user to make accessing a specific root file more convienient for repeated processing
homefolder="/home/matthew/ROOT/Phase2"

class RDFPG:
    '''
        Root Data Frame Processing GUI (RDFPG) is a graphical user interface designed to
        rapily and efficiently processes root dataframes and produce well labeled and
        structured plots.  
    '''
    def __init__(self,master):
        '''
            This program creates a GUI that will then be used to to load and process the
            data
            Arguments:
            master: the current tk interpreture to be used 
        '''
        self.rootcodefile ="{"
        self.currentfile = '/home/matthew/ROOT/Phase2/ana-dsttod0pip_90.root'
        #set a default file 
        self.master=master
        #set an accesable tk window 
        self.frame= tk.Frame(self.master)
        #create a frame within the window
        self.frame.pack()
        
        #create a quit button 
        self.quitbutton = tk.Button(self.frame,text = "QUIT", fg ="red", command=self.quit)
        self.quitbutton.pack(side='left')

        

        #create file search execution button 
        self.getfile = tk.Button(self.frame, text = "CHOOSE A FILE", command = self.openfile)
        self.getfile.pack(side= 'left')

        

    def quit(self):
        """
            Simple command clears out and deletes the existing window
        """
        self.frame.quit()
        self.frame.destroy()
        
        
    def openfile(self):
        """
            This command uses the file dialog to open a new file and then construct
            an option menu to select the specific data set to use 
        
        """
        #remove a misleading button
        self.getfile.destroy()
        
        #use a file dialog to allow the user to select 
        self.currentfilenm = tk.filedialog.askopenfilename(initialdir =homefolder,title = "Select a file", filetypes = (("root files","*.root"),("all files(not recommended","*.*")))
        self.curfolder = uproot.open(self.currentfilenm)
        
        #notify the user of file selection
        print("file selected")
        
        #create a drop down menu view and select the available data files
        self.subfl = tk.StringVar(self.master)
        self.optmn1=tk.ttk.Combobox(self.master, textvariable=self.subfl,values=self.curfolder.keys())
        self.optmn1.pack(side='left')
        
        #createbuttons to access subfolders within root file and initialize the function once that folder is selected
        self.axsubfl = tk.Button(self.frame, text="ACCESS SUB FOLDER", command = self.opensub)
        self.axsubfl.pack(side='left')
        self.comfirmsub = tk.Button(self.frame, text= "Confirm current subfolder",command = self.finalize)
        self.comfirmsub.pack(side='left')

    def opensub(self):
        ''' 
            This program opens up a sub folder within a main file so say you have a root file with a class bears 
            and a class dogs it could open bears and reach the classes sunbears polarbears brownbears and grizzly 
            bears
        '''
        #grab the file name from the dropdown menu and format it so that it can actually be read
        self.curfolder= self.curfolder[ self.subfl.get().replace('b','').replace( '\'','')]
        print('subfolder selected')
        
        #clear and reset the dropdown menu so that more files may be accessed
        self.optmn1.destroy()
        self.optmn1=tk.ttk.Combobox(self.master,textvariable=self.subfl, values=self.curfolder.keys())
        self.optmn1.pack(side='left')
        
        
    def finalize(self):
        '''
            This class finalizes the subfolder selection and clears the entry region for subfolders. then
            replaces them with the commands for selecting the variables to use from the folder. 
        '''
        
        #clear the workspace of misleading buttons 
        self.comfirmsub.destroy()
        self.axsubfl.destroy()
       
 
        #create a place for new variable names to be defined by the user
        self.variablename = tk.StringVar(self.master)
        self.variablename.set("variablename")
        self.varnamefield = tk.Entry(self.frame,textvariable=self.variablename)
        self.varnamefield.pack(side='left')
        
        #preinitialize a location to store variables used and their associated call signs
        self.varsused= [];
        self.varnames= [];
        
        #create controlls to remove and 
        self.choosevar = tk.Button(self.frame,text="Confirm variable name",command = self.setvar)
        self.choosevar.pack(side='left')
        self.confirmallv = tk.Button(self.frame,text="Use Just These Variables",command= self.finalizevar)
        self.confirmallv.pack(side='left')
        
    def setvar(self):
        '''
            This adds the values that you have selected to a list that will be used to load and name the columns of
            the pandas array you will be working in
        '''
        #This prints the variables and how they have been defined to help the user keep track of the choices they have made
        print(self.variablename.get(),"=",self.subfl.get())
        self.varsused+= [self.subfl.get()]
        self.varnames+=[self.variablename.get()]
        
        #prints the lists and names for debugging convineince 
        print(self.varsused)
        print(self.varnames)
        
    def finalizevar(self):
        '''
            This sets up the pandas folder, renames the columns to the variable names then presents the definition areas for the 
            the processing of the data, and cuts to be made on the data. Finally allows for the data to be plotted 
        '''
        #Load the root file as a pandas array and rename its variables
        self.pndsfl= self.curfolder.pandas.df(self.varsused)
        pos = []
        it =0 
        print(self.pndsfl.columns)
        #this may seem bizzare but it allows the system to handle 4 vectors and the like 
        #by creating names out of the name suggested by the user, there is one problem 
        #this doesnt work for redundant names if the longer name is not loaded first
        for j in range(len(self.varnames)):
            pos = []
            it=0
            for i in range(len(self.pndsfl.columns)):
                print(f'{self.pndsfl.columns[i]} contains {self.pndsfl.columns[i].count(self.varsused[j])} {self.varsused[j]}s has length:{len(self.pndsfl.columns[i])}')
                if(((self.pndsfl.columns[i].count(self.varsused[j])>0))):
                    
                    self.pndsfl.columns.values[i] = self.varnames[j]
                    pos+= [i]
                    print(it)
        
                    if(it==1):
                        print(pos[0])
                        self.pndsfl.columns.values[pos[0]]=self.varnames[j]+str(0)
                    if(it>=1):
                        self.pndsfl.columns.values[pos[it]]=self.varnames[j]+str(it)
                    it+=1
        
        self.varnames = self.pndsfl.columns.values
        #clear the missleading buttons 
        self.confirmallv.destroy()
        self.choosevar.destroy()
        self.varnamefield.destroy()
        self.optmn1.destroy()
        
        #create a field to enter the data that is going to be processed
        self.plotteddata =tk.StringVar(self.master)
        self.plotteddata.set('Data to be ploted')
        self.plotteddataent=tk.Entry(self.frame,textvariable=self.plotteddata)
        self.plotteddataent.pack(side='left')  
        
        #initialize a dictionary to store all of the cuts made in the data 
        self.cutsforvars = {}
        #initialize a dictionary to store all of the data entery points
        self.cutsforvarsent={}
        
        #create the entrys and variables for all of the cuts in the list
        for var in self.varnames:
            self.cutsforvars[var]=tk.StringVar(self.master)
            self.cutsforvars[var].set("Cuts for "+var)
            self.cutsforvarsent[var]=tk.Entry(self.frame,textvariable=self.cutsforvars[var])
            self.cutsforvarsent[var].pack(side='left')
            
        #create an additional cut entry point for the total processed data after all cuts have been applied 
        self.cutsforvars['total']=tk.StringVar(self.master)
        self.cutsforvars['total'].set("Cuts for total")
        self.cutsforvarsent['total']=tk.Entry(self.frame,textvariable=self.cutsforvars['total'])
        self.cutsforvarsent['total'].pack(side='left')
        
        #set up entry variables for titles 
        self.xtitle = tk.StringVar(self.master)
        self.xtitle.set('X Title')
        self.ytitle = tk.StringVar(self.master)
        self.ytitle.set('Y Title')
        self.maintitle = tk.StringVar(self.master)
        self.maintitle.set('Main Title')
        
        #set up entry points for titles 
        self.xtitleent = tk.Entry(self.frame,textvariable = self.xtitle)
        self.ytitleent = tk.Entry(self.frame,textvariable = self.ytitle)
        self.maintitleent = tk.Entry(self.frame,textvariable = self.maintitle)
        
        #show the entry points 
        self.xtitleent.pack(side='left')
        self.ytitleent.pack(side='left')
        self.maintitleent.pack(side='left')
        
        #creat a entry for the number of bins to use for the histogram 
        self.binlabel =tk.Label(text="Number of bins",fg="white",bg="black")
        self.binsx = tk.IntVar(self.master)
        self.binsxent = tk.Entry(self.frame,textvariable= self.binsx)
        self.binsxent.pack(side = 'left')
        
        #create a entry for the fit function 
        
        #create a plotting workspace 
        self.pltspc = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.subplt= self.pltspc.add_subplot(111)
        print("figures initialized program ready for data selection")
        
        #create a button to apply all the cuts and show the plot 
        self.showplot = tk.Button(self.frame,text = "SHOW THE PLOT",command = self.showplot)
        self.showplot.pack(side='left')
        

        
    def showplot(self):
        """
            Show plot uses the previously aquired user entries and loaded data to create a
            plot and add fittings to that plot. 
            Show plot was developed with reference to the following site: 
            https://matplotlib.org/examples/user_interfaces/embedding_in_tk.html
        
        """
        fpd = self.pndsfl #set up a dummy data frame to work with in this execution
        
        subplt=self.subplt
        
        #this is pretty wonky but it just grabs the requested cut and reformats 
        #it so it can be read then executes that cut on the data
        for var in self.varnames:
            cutstring = self.cutsforvars[var].get()
            if((cutstring == ("Cuts for "+var))|(cutstring == '')):
                cutstring ="..."
            for name in fpd.columns:
                
                cutstring = cutstring.replace(name,"fpd['"+name+"']")
                
            fpd[var]=fpd[var][eval(cutstring)]
            
        #call upon the users requested data string then convert it to an executable string and execute    
        datatoplot= self.plotteddata.get()
        for name in fpd.columns:
            datatoplot = datatoplot.replace(name,"fpd['"+name+"']")
        fpd['final_data']=eval(datatoplot)
        
        #apply a cut to the finall data set
        finalcut = self.cutsforvars['total'].get()
        if((finalcut=="Cuts for total")|(finalcut=="")):
            finalcut= "..."
        for name in fpd.columns:
            finalcut = finalcut.replace(name,"fpd['"+name+"']")
        finalcut = finalcut.replace('tot',"fpd['"+'final_data'+"']")
        fpd['final_data']=fpd['final_data'][eval(finalcut)]
        
        #clear out blank entries for convienient plotting
        trimmed_data = np.asarray(fpd['final_data'])[~np.isnan(np.asarray(fpd['final_data']))]
        
        
        self.trimmed_data=trimmed_data
        
        numofbins=self.binsx.get()
        
        #set up an x variable for the fitting 
        x = np.linspace(np.min(trimmed_data),np.max(trimmed_data),numofbins)
        totpart = len(trimmed_data)
        print("I've processed the data and will attempt to plot")
        self.subplt.clear()
        
        self.subplt.hist(trimmed_data, bins = numofbins)

        print("I've attempted to plot the data")

        self.subplt.set_xlabel(self.xtitle.get())
        self.subplt.set_ylabel(self.ytitle.get())
        self.subplt.set_title(self.maintitle.get())
        self.canvas = FigureCanvasTkAgg(self.pltspc,master=self.frame)
        self.canvas.draw()
        print("I've attempted to add the plot to the frame")
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        self.getfitbt = tk.Button(self.frame,text="Add A Fit",command=self.getfit)
        self.getfitbt.pack(side="left")
    
    def getfit(self):
        self.diawindow = tk.Toplevel(self.master)
        self.getstring = tk.Button(self.diawindow,text ="Set Fit" ,command=self.getfitstring)
        self.getstring.pack(side='left')
        
        self.fitstring = tk.StringVar(self.master)
        self.fitstring.set("The fit with coeffs in [brackets] use tot for fitted data")
        self.fitstringfield = tk.Entry(self.diawindow,textvariable=self.fitstring)
        self.fitstringfield.pack(side="left")
        
        self.dwquitb = tk.Button(self.diawindow,text = "QUIT", fg ="red",command=self.quitdia)
        self.dwquitb.pack(side='left')
    
    def quitdia(self):
        self.diawindow.quit()
        self.diawindow.destroy()
        
    def getfitstring(self):
        funcstring = self.fitstring.get()
            #find the start bracket indicating the start of the variable names 
        sparpos = -1
        spars = []
        for i in range(funcstring.count('[')):
            sparpos = funcstring.find("[", sparpos+1)
            spars +=[sparpos]
        
        # find the close brackets indicating the variable names
        cparpos = -1
        cpars = []
        for i in range(funcstring.count(']')):
            cparpos = funcstring.find("]", cparpos+1)
            cpars +=[cparpos]
        
        #collect all of the arguments into a cumulative list
        args = []
        for i in range(len(cpars)):
            args += [funcstring[spars[i]+1:cpars[i]]]
        
        #add the np call sign to the npfunctions
        poslist= []
        for npname in dir(np):
            if(npname in funcstring):
                if((poslist.count(funcstring.find(npname))<1)):
                    poslist += [funcstring.find(npname)+3]
                    funcstring=funcstring.replace(npname,"np."+npname)
        
        #create a call to a dictionary with the accesor of the respective argument 
        for arg in args: 
            funcstring=funcstring.replace("["+arg+"]","argdic['"+arg+"']")
        
        self.args = args 
        self.funcstring= funcstring
        
        self.argguess = {}
        self.argguessent={}
        #create entry fields for each argument in the fit function 
        for arg in self.args:
            self.argguess[arg]=tk.StringVar(self.master)
            self.argguess[arg].set("initial guess for"+arg)
            self.argguessent[arg]=tk.Entry(self.diawindow,textvariable=self.argguess[arg])
            self.argguessent[arg].pack(side='left')
        
        # print a double check for the variables and function 
        print("Check this for your final function=>",funcstring)
        print("Check this for your variables=>",args)
        
        # set up a button to try the fitting on 
        self.tryfitbt = tk.Button(self.diawindow,text = "trythefitting",command=self.tryfit)
        self.tryfitbt.pack(side="left")
        
    def tryfit(self):
        def nnlf(coeff,tot):
            argdic = {}
            for arn in range(len(self.args)):
                argdic[self.args[arn]]= coeff[arn]
            y= eval(self.funcstring)
            print(self.args," = ",coeff)
            return -np.sum(np.log(y))
        
        def f(coeff,tot):
            argdic = {}
            for arn in range(len(self.args)):
                argdic[self.args[arn]]= coeff[arn]
            return eval(self.funcstring)
        
        argran =np.zeros((len(self.args),2))
        arggue =np.zeros(len(self.args))
        for arn in range(len(self.args)):
            arggue[arn]=float(self.argguess[self.args[arn]].get())
            argran[arn]= [float(self.argguess[self.args[arn]].get())-3,float(self.argguess[self.args[arn]].get())+3]
        print(argran)
        fit = minimize(nnlf,arggue,args = (self.trimmed_data,),bounds=argran)
        
        x = np.linspace(np.min(self.trimmed_data),np.max(self.trimmed_data),self.binsx.get())
        y = (x[1]-x[0])*len(self.trimmed_data)*f(fit.x,x)
        self.subplt.plot(x,y)
        self.canvas.draw()
        
        

base = tk.Tk()
base.tk.call('tk', 'scaling', 10.0)
w = RDFPG(base)
base.mainloop()
