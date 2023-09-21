
## /\ compatability line

## import libraries
import os
import pandas
import tkinter
import tkinter.filedialog

## define functions
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


def grabexphead(px,tab,lab,des,filt):
    for i in range(len(px[tab][lab])):
        if px[tab][lab][i]==filt:
            return px[tab][des][i]
#
def makeAniDict(filename):
    ##
    xl=pandas.read_excel(filename,None)
    xlDict={}
    ##
    for i in range(len(xl['LOG']['Field1'])):
        if xl['LOG']['Field1'][i]=='Protocol File':
            proPath=xl['LOG']['Field2'][i]
            proDateTime=xl['LOG']['RealTime'][i]
            break
    xlDict['filename']=os.path.basename(proPath)[:-4]
    xlDict['vidfilename']=xlDict['filename']+'_Video 1_1.avi'
    xlDict['date']=proDateTime.split()[0]
    xlDict['time']=proDateTime.split()[1]

    xlDict['GroupA']={
            'chamber':1,
            'vidchamber':1,
            'group':'a',
            'line':grabexphead(xl,'GroupA','Label','Description','line'),
            'idno':grabexphead(xl,'GroupA','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupA','Label','Description','Weight')
            }
    
    xlDict['GroupB']={
            'chamber':2,
            'vidchamber':2,
            'group':'b',
            'line':grabexphead(xl,'GroupB','Label','Description','line'),
            'idno':grabexphead(xl,'GroupB','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupB','Label','Description','Weight')
            }
    
    xlDict['GroupC']={
            'chamber':3,
            'vidchamber':3,
            'group':'c',
            'line':grabexphead(xl,'GroupC','Label','Description','line'),
            'idno':grabexphead(xl,'GroupC','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupC','Label','Description','Weight')
            }
    
    xlDict['GroupD']={
            'chamber':4,
            'vidchamber':4,
            'group':'d',
            'line':grabexphead(xl,'GroupD','Label','Description','line'),
            'idno':grabexphead(xl,'GroupD','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupD','Label','Description','Weight')
            }
    
    xlDict['GroupE']={
            'chamber':5,
            'vidchamber':5,
            'group':'E',
            'line':grabexphead(xl,'GroupE','Label','Description','line'),
            'idno':grabexphead(xl,'GroupE','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupE','Label','Description','Weight')
            }
    
    xlDict['GroupF']={
            'chamber':6,
            'vidchamber':6,
            'group':'f',
            'line':grabexphead(xl,'GroupF','Label','Description','line'),
            'idno':grabexphead(xl,'GroupF','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupF','Label','Description','Weight')
            }
    
    xlDict['GroupG']={
            'chamber':7,
            'vidchamber':7,
            'group':'g',
            'line':grabexphead(xl,'GroupG','Label','Description','line'),
            'idno':grabexphead(xl,'GroupG','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupG','Label','Description','Weight')
            }
    
    xlDict['GroupH']={
            'chamber':8,
            'vidchamber':8,
            'group':'h',
            'line':grabexphead(xl,'GroupH','Label','Description','line'),
            'idno':grabexphead(xl,'GroupH','Label','Description','Animal Number'),
            'weight':grabexphead(xl,'GroupH','Label','Description','Weight')
            }
    return xlDict
## run script

x=guiOpenFileNames()
##
o=guiSaveFileName()
##
fl={}
for i in x:
    fl[i]=makeAniDict(i)
##
flkeys=list(fl.keys())
flkeys.sort()
with open(o,'w') as outfile:
    outline="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date='date',
    time='time',
    filename='filename',
    vidfilename='video filename',
    chamber='chamber',
    vidchamber='video chamber',
    group='group',
    line='line',
    idno='id',
    weight='weight'
    )
    outfile.write(outline)

    for i in flkeys:
        outline="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=1,
    vidchamber=1,
    group='a',
    line=fl[i]['GroupA']['line'],
    idno=fl[i]['GroupA']['idno'],
    weight=fl[i]['GroupA']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=2,
    vidchamber=2,
    group='b',
    line=fl[i]['GroupB']['line'],
    idno=fl[i]['GroupB']['idno'],
    weight=fl[i]['GroupB']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=3,
    vidchamber=3,
    group='c',
    line=fl[i]['GroupC']['line'],
    idno=fl[i]['GroupC']['idno'],
    weight=fl[i]['GroupC']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=4,
    vidchamber=4,
    group='d',
    line=fl[i]['GroupD']['line'],
    idno=fl[i]['GroupD']['idno'],
    weight=fl[i]['GroupD']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=5,
    vidchamber=5,
    group='e',
    line=fl[i]['GroupE']['line'],
    idno=fl[i]['GroupE']['idno'],
    weight=fl[i]['GroupE']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=6,
    vidchamber=6,
    group='f',
    line=fl[i]['GroupF']['line'],
    idno=fl[i]['GroupF']['idno'],
    weight=fl[i]['GroupF']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=7,
    vidchamber=7,
    group='g',
    line=fl[i]['GroupG']['line'],
    idno=fl[i]['GroupG']['idno'],
    weight=fl[i]['GroupG']['weight']
    )
        outline+="""{date}\t{time}\t{filename}\t{vidfilename}\t{chamber}\t{vidchamber}\t{group}\t{line}\t{idno}\t{weight}\n""".format(
    date=fl[i]['date'],
    time=fl[i]['time'],
    filename=fl[i]['filename'],
    vidfilename=fl[i]['vidfilename'],
    chamber=8,
    vidchamber=8,
    group='h',
    line=fl[i]['GroupH']['line'],
    idno=fl[i]['GroupH']['idno'],
    weight=fl[i]['GroupH']['weight']
    )
        outfile.write(outline)
##    
input("press enter to close")
