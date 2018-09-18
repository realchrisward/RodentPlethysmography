import os
import tkinter
import tkinter.filedialog

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
# import wardcode
##
#x=wardcode.guiOpenFileNames()
x=guiOpenFileNames()
##
fl={}
for i in x:
    print(i)
    with open(i) as f:
        f.seek(0,2)
        fl[i]={}
        fl[i]['binlen']=f.tell()
        ##
        f.seek(fl[i]['binlen']-1000,0)
        fl[i]['lines']=f.read().split('\n')
##
for i in fl:
    ts=fl[i]['lines'][-2].split()
    print(ts[0]+"\t"+os.path.basename(i))

input("press enter to close")
