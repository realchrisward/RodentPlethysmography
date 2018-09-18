#!usr/bin/env python3
## /\ compatability line
"""
Wardcode v2- updated for python 3.4.2
(C) 2015 Christopher Ward

simple functions designed to simplify
data i/o interactions with the user


copy to the python Lib folder to allow 
import of these functions

update 2018-02-13 for comma delim parsing (note-this could use improvement)
"""

## import modules
import os
import tkinter
import tkinter.filedialog

## function set 1 - text based
def getYN(inputtext=''):
    """Promtpes the user for a Yes or No response.
Returns 'y' or 'n' based on user response.
Non-Y/N responses prompt user to re-enter a response.
*inputtext defines the text preceding the user interaction"""
    while 1:
        outputtext=input(inputtext + '\nPlease Enter Y/N:\n')
        if outputtext.lower() in ['y','n']:
            return outputtext.lower()[0]
        else: print('INVALID SELECTION')

def getInt(inputtext=''):
    """Prompts the user for an integer.
Returns the integer entered by the user.
If a non-integer is entered, the user is prompted
to re-enter a value until an integer is submitted.
"""
    while 1:
        try:
            outputint=int(input(inputtext + '\nPlease Enter an Integer:\n'))
            return outputint
        except: print('INVALID ENTRY')

def getFloat(inputtext=''):
    """Prompts the user for a real number.
Returns the real number entered by the user.
Other inputs prompt the user to re-enter a
response until a real number is submitted.
"""
    while 1:
        try:
            outputfloat=float(input(inputtext + '\nPlease Enter a Number:\n'))
            return outputfloat
        except: print('INVALID ENTRY')

def getListItem(inputtext='',inputlist=[]):
    """Prompts the user for a value.
Values are accepted if they can be found in a predefined list.
Other values prompt the user to re-enter a response.
*inputtext defines the text preceding the user interaction
*inputlist defines the values acceptable as a user response
## *note that the values in inputlist and returned value
should all be text strings
"""
    while 1:
        outputtext=input(inputtext + '\n\t' + '\n\t'.join(inputlist) +
                     '\nPlease Select From The Listed Options (case sensitive):\n')
        if outputtext in inputlist:
            return outputtext
        else: print('INVALID SELECTION')

def getListKey(inputtext='',inputlist=[]):
    """Prompts the user to select a value from a list.
Returns the index of the value enterred by the user 
that matches an entry in a predefined key:value list
(should be key-1),(the key values are generated automatically)
*inputtext defines the text preceding the user interaction
*inputlist defines the values acceptable as a user response
## *note that the values in inputlist and returned value
should all be text strings
"""
    while 1:
        inputkey=[str(i+1) for i in range(len(inputlist))]
        displaylist=[str(i+1)+'\t:\t'+inputlist[i]
                     for i in range(len(inputlist))]
        outputtext=input(inputtext + '\n\t' + '\n\t'.join(displaylist) +
                     '\nPlease Select From The Listed Options:\n')
        if outputtext in inputkey:
            return inputkey.index(outputtext)
        else: print('INVALID SELECTION')

def getListValue(inputtext='',inputlist=[]):
    """Prompts the user to select a value from a list.
Returns the value corresponding to the key enterred by the
user that matches an entry in a predefined key:value list.
(the key values are generated automatically)
*inputtext defines the text preceding the user interaction
*inputlist defines the values acceptable as a user response
## *note that the values in inputlist and returned value
should all be text strings
"""
    while 1:
        inputkey=[str(i+1) for i in range(len(inputlist))]
        displaylist=[str(i+1)+'\t:\t'+inputlist[i]
                     for i in range(len(inputlist))]
        outputtext=input(inputtext + '\n\t' + '\n\t'.join(displaylist) +
                     '\nPlease Select From The Listed Options:\n')
        if outputtext in inputkey:
            return inputlist[inputkey.index(outputtext)]
        else: print('INVALID SELECTION')

def getKeyFromKV(inputtext='',keylist=[],valuelist=[]):
    """Prompts the user to select a value from a list.
Returns the key enterred by the user that matches an
entry in a predefined key:value list.
(the key values are provided when defining the function call)
*inputtext defines the text preceding the user interaction
*keylist defines the values acceptable as a user response
*valuelist defines the values that correspond to the keys
## *note that the values in inputlist and returned value
should all be text strings
"""
    while 1:
        displaylist=[keylist[i]+'\t:\t'+valuelist[i]
                     for i in range(len(keylist))]
        outputtext=input(inputtext + '\n\t' + '\n\t'.join(displaylist) +
                     '\nPlease Select From The Listed Options:\n')
        if outputtext in keylist:
            return outputtext
        else: print('INVALID SELECTION')

## function set 2 - GUI based (mostly tkinter calls)
def guiOpenFileName(kwargs={}):
    """Returns the path to the file selected by the GUI.
*Function calls on tkFileDialog and uses those arguments
  ......
  (declare as a dictionairy)
  {"defaultextension":'',"filetypes":'',"initialdir":'',...
  "initialfile":'',"multiple":'',"message":'',"parent":'',"title":''}
  ......"""
    root=tkinter.Tk()
    outputtext=tkinter.filedialog.askopenfilename(
        **kwargs)
    root.destroy()
    return outputtext

def guiOpenFileNames(kwargs={}):
    """Returns the path to the files selected by the GUI.
*Function calls on tkFileDialog and uses those arguments
  ......
  (declare as a dictionairy)
  {"defaultextension":'',"filetypes":'',"initialdir":'',...
  "initialfile":'',"multiple":'',"message":'',"parent":'',"title":''}
  ......"""
    root=tkinter.Tk()
    outputtextraw=tkinter.filedialog.askopenfilenames(
        **kwargs)
    outputtext=root.tk.splitlist(outputtextraw)
    root.destroy()
    return outputtext

def guiDirectory(kwargs={}):
    """Returns the directory path selected by the GUI.
*Function calls on tkFileDialog and uses those arguments
  ......
  (declare as a dictionairy)
  {"defaultextension":'',"filetypes":'',"initialdir":'',...
  "initialfile":'',"multiple":'',"message":'',"parent":'',"title":''}
  ......"""
    root=tkinter.Tk()
    outputtext=tkinter.filedialog.askdirectory(
        **kwargs)
    root.destroy()
    return outputtext

def guiSaveFileName(kwargs={}):
    """Returns the path to the filename and location entered in the GUI.
*Function calls on tkFileDialog and uses those arguments
  ......
  (declare as a dictionairy)
  {"defaultextension":'',"filetypes":'',"initialdir":'',...
  "initialfile":'',"multiple":'',"message":'',"parent":'',"title":''}
  ......"""
    root=tkinter.Tk()
    outputtext=tkinter.filedialog.asksaveasfilename(
        **kwargs)
    root.destroy()
    return outputtext

## function set 3 - DATA I/O text file <-> list reading and writing
def dataGrab(filepath):
    """Returns the contents of a text file as a list
with one item in the list per line in the file"""
    outputdata=[]
    with open(filepath,'r') as f:
        for line in f:
            outputdata.append(line)
    f.closed
    print('\n{x} lines in file: {y} \n'.format(
        x=len(outputdata),y=os.path.basename(filepath)))
    return outputdata

def dataFindHeaderByText(inputdata,headertextlist):
    """checks input data for headerline that contains all items in headertextlist
Returns the first line number that meets the header text criteria"""
    try:
        for lineno in range(len(inputdata)):
            if all(col in inputdata[lineno] for col in headertextlist):
                   return lineno
        print('HEADER NOT FOUND')
    except:
        print('HEADER NOT FOUND')
                            
def dataCheckForHeader(inputdata,startline,linestocheck):
    """Displays lines of data to allow user to declare position of 'Header Columns'
Returns line number chosen by the user"""
    try:
        while 1:
            keys=[i for i in range(startline,startline+linestocheck)]
            headerindex=getKeyFromKV('select the header line',
                         [str(i) for i in keys]+['na'],
                         inputdata[startline:startline+linestocheck]
                                     +['header line not present'])
            if headerindex=='na':
                startline+=linestocheck
            else:
                return headerindex
    except:
        print('HEADER NOT FOUND')
        return 'na'
    
def dataParseTextToColumns(inputdata,headerline):
    """Creates a python dictionary of lists corresponding to
columns of data in the line seperated input (uses whitespace to split columns)"""
    
    headercolumns=inputdata[headerline].replace(',','\t').replace(', ','\t').replace(',  ','\t').split()
    datadict={}
    for i in range(len(headercolumns)):
        datadict[i]={headercolumns[i]:[]}
    for line in inputdata[headerline+1:]:
        try:

            splitline=line.replace(',','\t').replace(', ','\t').replace(',  ','\t').split()
            for i in range(len(headercolumns)):
                datadict[i][headercolumns[i]].append(splitline[i])
        except:
            print('{x} lines parsed'.format(x=
                len(datadict[0][headercolumns[0]])))
            return datadict
    print('{x} lines parsed --'.format(x=
        len(datadict[0][headercolumns[0]])))
    return datadict

def dataParseTabDelToColumns(inputdata,headerline):
    """Creates a python dictionary of lists corresponding to
columns of data in the line seperated input (uses tabs '\t' to split columns)"""
    headercolumns=inputdata[headerline].replace('\n','\t').split('\t')
    datadict={}
    for i in range(len(headercolumns)):
        datadict[i]={headercolumns[i]:[]}
    for line in inputdata[headerline+1:]:
        try:
            splitline=line.replace('\n','\t').split('\t')
            for i in range(len(headercolumns)):
                datadict[i][headercolumns[i]].append(splitline[i])
        except:
            print('{x} lines parsed'.format(x=
                len(datadict[0][headercolumns[0]])))
            return datadict
    print('{x} lines parsed --'.format(x=
        len(datadict[0][headercolumns[0]])))
    return datadict

def dataDictUnfold(inputdict):
    """returns a dictionary with the 1st layer of keys removed
note-this is only suited to dictionairies with 2 layers of singleton keys
common when importing using the dataParse functions defined above
"""
    x={}
    k=inputdict.keys()
    for i in k:
        x[list(inputdict[i].keys())[0]]=inputdict[i][list(inputdict[i].keys())[0]]
    return x
          
def dataWriteDict(inputdata,keyorder,keyname,columnorder,outputfilename):
    """creates a simple tab delimited text file populated in table format
from the entries in a 2-layer dictionary
...
*inputdata - dictionary of data to be output
*keyorder - list indicating the order to output the 1st layer keys from the inputdata (as row blocks)
*keyname - text used as column header for key output
*columnorder - list indicating the order to output 2nd layer keys from the inputdate (as columns)
*outputfilename - filename/path for output of the data
"""

    headerline=keyname+'\t'.join(columnorder)+'\n'
    with open(outputfilename,'w') as f:
        f.write(headerline)
        for keyitem in keyorder:
            f.write(str(keyitem)+'\t')
            for row in inputdata[keyitem][columnorder[0]]:
                for col in columnorder:
                    f.write(str(inputdata[keyitem][col])+'\t')
                f.write('\n')

def dataWriteList(inputdata,outputfilename):
    """creates a simple tab delimited text file populated in table format
from the entries in a list (one line per item in the input list)"""
    with open(outputfilename,'w') as f:
        for row in inputdata:
            f.write('\t'.join(row)+'\n')
        f.close()

## function set 4 - List and Set Comparison/Modification
def getabovethresh(inputlist,thresh):
    """creates a binary list, indicating comparison of
inputlist entries to thresh value
1 if above (exclusive), else 0"""
    abovethreshlist=[1 if i>thresh else 0
                     for i in inputlist]
    return abovethreshlist

def getinrangelist(inputlist,minval,maxval):
    """creates a binary list, indicating inputlist entries are
between (inclusive) the minval and maxval"""
    inrangelist=[1 if maxval>=i>=minval else 0
                 for i in inputlist]
    return inrangelist

def getsegdict(inputlist,segdic,segheader):
    outlisttemp=[0 for i in inputlist]
    outDict={}
    for seg in segdic[segheader]:
        outDict[seg]=list(outlisttemp)
    for i in range(len(segdic[segheader])):
        outDict[segdic[segheader][i]]=mergelistmax(
            outDict[segdic[segheader][i]],
            getinrangelist(inputlist,
                           float(segdic['Start'][i]),
                           float(segdic['Stop'][i])))
    return outDict

def getbelowthresh(inputlist,thresh):
    """creates a binary list, indicating comparison of
inputlist entries to thresh value
1 if below (exclusive), else 0"""
    belowthreshlist=[1 if i<thresh else 0
                     for i in inputlist]
    return belowthreshlist

def getdifflist(inputlist):
    """returns a list of length-1 relative to the input list
list values are the differential of the inputlist [n+1]-[n]"""
    difflist=[inputlist[i+1]-inputlist[i]
              for i in range(len(inputlist)-1)]
    return difflist

def getindexlist(inputlist,acceptedvaluelist):
    """returns a list of index values that match accepted values
acceptedvaluelist should be entered as a list.
[1,-1] is suggested for breathing analysis
"""
    indexlist=[i for i in
                    range(len(inputlist))
                    if inputlist[i] in acceptedvaluelist]
    return indexlist

def getfilteredlist(inputlist,acceptedvaluelist):
    """returns a list containing only the accepted values
"""
    outputlist=[i for i in inputlist if i in acceptedvaluelist]
    return outputlist

def getlistfromfilter(inputlist,filterlist,filtval):
    """returns a list of only the entries that match acceptable filter values"""
    return [inputlist[i] for i in range(len(inputlist)) if filterlist[i]==filtval]

def getindexedvals(inputlist,indexlist):
    """returns a list corresponding to the chosen index
"""
    outputlist=[inputlist[i] for i in indexlist]
    return outputlist

def getdiffbyindex(inputlist,indexlist):
    """can get durations using timestamp list for inputlist
and appropriate crossvals Ti,Te,Ttot
"""
    diffbyindexlist=[inputlist[indexlist[i+1]]-
                     inputlist[indexlist[i]]
                     for i in range(len(indexlist)-1)]
    return diffbyindexlist

def getsumbyindex(inputlist,indexlist):
    """can get TV calcs using flow data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    sumbyindexlist=[sum(
        inputlist[indexlist[i]:indexlist[i+1]]
                        )
                    for i in range(len(indexlist)-1)]
    return sumbyindexlist

def getmaxbyindex(inputlist,indexlist):
    """can get PIF calcs using flow data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    maxbyindexlist=[max(inputlist[indexlist[i]:indexlist[i+1]])
                    for i in range(len(indexlist)-1)]
    return maxbyindexlist

def getminbyindex(inputlist,indexlist):
    """can get PEF calcs using flow data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    minbyindexlist=[min(inputlist[indexlist[i]:indexlist[i+1]])
                    for i in range(len(indexlist)-1)]
    return minbyindexlist

def getsumby2index(inputlist,index1,index2):
    """can get TV calcs using flox data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    sumbyindexlist=[sum(
        inputlist[index1[i]:index2[i]]
                        )
                    for i in range(len(index1))]
    return sumbyindexlist

def getmaxby2index(inputlist,index1,index2):
    """can get PIF calcs using flox data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    maxbyindexlist=[max(
        inputlist[index1[i]:index2[i]]
                        )
                    for i in range(len(index1))]
    return maxbyindexlist

def getminby2index(inputlist,index1,index2):
    """can get PIF calcs using flox data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    minbyindexlist=[min(
        inputlist[index1[i]:index2[i]]
                        )
                    for i in range(len(index1))]
    return minbyindexlist

def getavg(inputlist):
    """returns the arithmatic average of the values in a list
"""
    try:
        return sum(inputlist)/len(inputlist)
    except:
        return 'NAN'

def mergelistmax(lst1,lst2):
    """returns the maximum value at each index comparing 2 lists"""
    try:
        return [max([lst1[i],lst2[i]]) for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistmin(lst1,lst2):
    """returns the minimum value at each index comparing 2 lists"""
    try:
        return [min([lst1[i],lst2[i]]) for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistadd(lst1,lst2):
    """returns the sum at each index comparing 2 lists"""
    try:
        return [lst1[i]+lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistmult(lst1,lst2):
    """returns the product at each index comparing 2 lists"""
    try:
        return [lst1[i]*lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistsubt(lst1,lst2):
    """returns the difference at each index comparing 2 lists"""
    try:
        return [lst1[i]-lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistdiv(lst1,lst2):
    """returns the division result at each index comparing 2 lists"""
    try:
        return [lst1[i]/lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

## function set 5 - graphing functions



