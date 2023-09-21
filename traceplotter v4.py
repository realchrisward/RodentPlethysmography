#!usr/bin/env python3
## /\ compatability line
"""
Breathing Graph Maker
(C) 2016 Christopher Ward
"""
## import modules
import numpy as np
import matplotlib.pyplot as plt
import json
import wardcode
import os
import scipy
from scipy import signal

## functions
def getindexedvals(inputlist,indexlist):
    """returns a list corresponding to the chosen index
"""
    outputlist=[inputlist[i] for i in indexlist]
    return outputlist

def getlistfromfilter(inputlist,filterlist,filtval):
    """returns a list of only the entries that match acceptable filter values"""
    return [inputlist[i] for i in range(len(inputlist)) if filterlist[i]==filtval]


## plethgraphint
def plethgraphint(timewindow,ymin,ymax,TS,CT,FB_TS_TI,FB_TS_TE,AP_SPEC,TS_SEG,TS_FILT,featureoptions,inchX,inchY,savepath,saveorshow):
    # grab trace data
    TW_ind=[i for i in range(len(TS)) if timewindow[1]>TS[i]>=timewindow[0]]
    TS_win=[i for i in TS if timewindow[1]>i>=timewindow[0]]
    CT_win=getindexedvals(CT,TW_ind)
    
    # grab marks
    MK_fTI=[i for i in FB_TS_TI if timewindow[1]>i>timewindow[0]]
    MK_fTE=[i for i in FB_TS_TE if timewindow[1]>i>timewindow[0]]
    MK_SEG=[i for i in TS_SEG if timewindow[1]>i>timewindow[0]]
    MK_FIL=[i for i in TS_FILT if timewindow[1]>i>timewindow[0]]
    MK_special=[i for i in AP_SPEC if timewindow[1]>i>timewindow[0]]
    # generate graph
    plt.clf()
    for horline in featureoptions['horLines'].split(';'):
        plt.plot(timewindow,
                 [float(horline.split(',')[0]),float(horline.split(',')[0])]
                 ,horline.split(',')[1])

    if featureoptions['flowOptions']=='':
        plt.plot(TS_win,CT_win,'b-')
    elif featureoptions['flowOptions']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['flowOptions'].split(',')[0])
        linestyle=featureoptions['flowOptions'].split(',')[1]
        plt.plot(TS_win,[i+offset for i in CT_win],linestyle)

    if featureoptions['soiMarks']=='':
        plt.plot(MK_fTI,[0 for i in MK_fTI],'g^')
    elif featureoptions['soiMarks']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['soiMarks'].split(',')[0])
        linestyle=featureoptions['soiMarks'].split(',')[1]
        plt.plot(MK_fTI,[offset for i in MK_fTI],linestyle)

    if featureoptions['soeMarks']=='':
        plt.plot(MK_fTE,[0 for i in MK_fTE],'mv')
    elif featureoptions['soeMarks']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['soeMarks'].split(',')[0])
        linestyle=featureoptions['soeMarks'].split(',')[1]
        plt.plot(MK_fTE,[offset for i in MK_fTE],linestyle)

    if featureoptions['segMarks']=='':
        plt.plot(MK_SEG,[1 for i in MK_SEG],'b>')
    elif featureoptions['segMarks']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['segMarks'].split(',')[0])
        linestyle=featureoptions['segMarks'].split(',')[1]
        plt.plot(MK_SEG,[offset for i in MK_SEG],linestyle)

    
    if featureoptions['filMarks']=='':
        plt.plot(MK_FIL,[0.9 for i in MK_FIL],'k>')
    elif featureoptions['filMarks']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['filMarks'].split(',')[0])
        linestyle=featureoptions['filMarks'].split(',')[1]
        plt.plot(MK_FIL,[offset for i in MK_FIL],linestyle)
    
    if featureoptions['apneaMarks']=='':
        plt.plot(MK_special,[0.5 for i in MK_special],'ro')
    elif featureoptions['apneaMarks']=='none':
        #donothing
        donothing=1
    else:
        offset=float(featureoptions['apneaMarks'].split(',')[0])
        linestyle=featureoptions['apneaMarks'].split(',')[1]
        plt.plot(MK_special,[offset for i in MK_special],linestyle)

    plt.axis([timewindow[0],timewindow[1],ymin,ymax])
    x=plt.gcf()
    x.set_size_inches(inchX,inchY)
    x.suptitle(os.path.basename(savepath))
    if saveorshow=='save':
        x.savefig(savepath)
    else:
        x.show()
        input('press ENTER to continue')
    

## get breath list
def grabjson(jsfile):
    with open(jsfile,'r') as f:
        outputobject=json.load(f)
    f.closed
    return outputobject
        
## get ascii file
def grabascii(xFilePath,header):
    CurFile=os.path.basename(xFilePath)
    #print('opening file '+CurFile)
    AsciiData=wardcode.dataGrab(xFilePath)
    #print('parsing data')
    xPD=wardcode.dataParseTextToColumns(AsciiData,int(header))
    return xPD

## define main
def main():
    #%%
    # specify apnea definition and graph settings
    segrange=input(
        'check for apneas within which segment? (enter as string text)\n')
    minVStime=wardcode.getFloat(
        'minimum duration of apnea (seconds)\n')
    minVSloc=wardcode.getFloat(
        'minimum duration of apnea relative to local TT\n')
    minVSseg=wardcode.getFloat(
        'minimum duration of apnea relative to segment TT\n')
    gwin=wardcode.getFloat(
        'x-axis length plotted (seconds)\n')
    ##
    ymin=wardcode.getFloat(
        'y-axis minimum\n')
    ymax=wardcode.getFloat(
        'y-axis maximum\n')
    inchX=wardcode.getFloat(
        'Chart Size (x-dimension [inches])\n')
    inchY=wardcode.getFloat(
        'Chart Size (y-dimension [inches])\n')
    saveorshow=wardcode.getListValue(
        'Save graphs or show without saving',['save','show'])
    timeorapnea=input("Press ENTER for default: graphs will plot graphs centered on apnea events\n-alternatively you can view specific times - please enter the times (seconds, commas between values)\n")
    FeatureOptions={}
    FeatureOptions['horLines']=input("""
    please enter desired horzontal line settings:
    y-value,color style;...
    comma to seperate y value from line setting
    semi colon to seperate multiple lines
    default = 0,-k;0.05,-r
    (black line at 0, red line at 0.05)
    press enter for default, input "none" for no horizontal lines
    colors          b|g|r|c|m|y|k|w
    line styles     -|--|-.|:
    marker styles   .|o|v|^|<|>|8|s|p|*|h|+|x|d|_
    """)
    if FeatureOptions['horLines']=="":FeatureOptions['horLines']="0,-k;0.05,-r"        
    FeatureOptions['soiMarks']=input("""
    please enter y-value for Start of Inspiration marks:
    press enter for default (y=0,g^ [green triangles]),
    or input y-value and color style settings
    input "none" for no marks
    """)
    FeatureOptions['soeMarks']=input("""
    please enter y-value for Start of Expiration marks:
    press enter for default (y=0,mv [magenta triangles]),
    or input y-value and color style settings
    input "none" for no marks
    """)
    FeatureOptions['segMarks']=input("""
    please enter y-value for Segment marks:
    press enter for default (y=1,b> [blue right-pointing-triangles]),
    or input y-value and color style settings
    input "none" for no marks
    """)
    FeatureOptions['filMarks']=input("""
    please enter y-value for Filter marks:
    press enter for default (y=0.9,k> [black right-pointing-triangles]),
    or input y-value and color style settings
    input "none" for no marks
    """)
    FeatureOptions['apneaMarks']=input("""
    please enter y-value for Apnea marks:
    press enter for default (y=0.5,ro [red circles]),
    or input y-value and color style settings
    input "none" for no marks
    """)
    FeatureOptions['flowOptions']=input("""
    please enter y-value offset and style for Flow Trace
    press enter for default (0,b- [no offset,blue line])
    input none to omit from the plot
    colors          b|g|r|c|m|y|k|w
    line styles     -|--|-.|:
    marker styles   .|o|v|^|<|>|8|s|p|*|h|+|x|d|_
    """)

    ## get data
    xFilePathList=wardcode.guiOpenFileNames({'title':'Load Ascii Files With Trace Data','filetypes':[('ascii','.ascii'),
                  ('all files','.*')]})
    breathlistfiles=wardcode.guiOpenFileNames({'title':'Load Breath List Files ".js"','filetypes':[('json','.js'),
                  ('all files','.*')]})
    ## set output location
    if saveorshow=='save':
        rootsavepath=wardcode.guiSaveFileName({'title':'root filename for output impages'})
    else:
        rootsavepath='*PREVIEW*'
    ##

    breathlist={}
    for xJS in breathlistfiles:
        tempbreathlist=grabjson(xJS)
        for f in tempbreathlist:
            breathlist[f]=tempbreathlist[f]
    
    ## loop through files
    # check headers
    xFD={}
    for xFP in xFilePathList:
        xFD[xFP]=wardcode.dataFindHeaderByText([i.lower() for i in wardcode.dataGrab(xFP)],['time','flow'])
    ## process data
    for xFilePath in xFD:
        try:
            #%%#
            xPD=grabascii(xFilePath,xFD[xFilePath])
            ##
            CurFile=os.path.basename(xFilePath).lower()
            TS=[float(i) for i in xPD[0]['Time']]
            ##
            SPEC_OUT='file\tanimal\tapneaTimeStamp'
            ##
            
            for stranimal in breathlist[os.path.basename(CurFile)]:
                    try:
                        animal=int(stranimal)
                        ##
                        CT=[float(i) for i in xPD[animal]['Flow']]
    
                        # apply smoothing filter to signal
                        sampleHz=1/(TS[2]-TS[1])
    
                        hpf_b,hpf_a=signal.butter(2,0.1/(sampleHz/2),'high')
                        hpfCT=signal.filtfilt(hpf_b,hpf_a,CT)
    
                        lpf_b,lpf_a=signal.bessel(10,50/(sampleHz/2),'low')
                        lpfhpfCT=signal.filtfilt(lpf_b,lpf_a,hpfCT)
                        CT=lpfhpfCT
                        ## end of smoothing filter
                        AP=breathlist[CurFile][stranimal]['BL']['AP']
                        
                        FB_DVTV=breathlist[CurFile][stranimal]['BL']['DVTV']
                        DVTV_filt=[1 if i<AP['maxDVTV'] else 0 for i in FB_DVTV]
                                                       
                        FB_per500=breathlist[CurFile][stranimal]['BL']['per500']
                        p500_filt=[1 if i<AP['maxPer500'] else 0 for i in FB_per500]
    
                        qual_filter=[min(DVTV_filt[i],p500_filt[i]) for i in range(len(FB_DVTV))]
                        
                        
                        FB_TS_TI=breathlist[CurFile][stranimal]['BL']['TS_TI']
                        #FB_IL_TI=[int((i-TS[0])/(TS[0]-TS[1])) for i in FB_TS_TI]
    
                        FB_TS_TE=breathlist[CurFile][stranimal]['BL']['TS_TE']
                        FB_TT=[FB_TS_TI[i+1]-FB_TS_TI[i] for i in range(len(FB_TS_TI)-1)]+[0]
                        FB_LOC=breathlist[CurFile][stranimal]['BL']['ApLocTT']
    
                        segTT=breathlist[CurFile][stranimal]['segTT'][segrange]
                        filt_segTT=[1 if i>=(minVSseg*segTT) else 0 for i in FB_TT]
                        filt_locTT=[1 if FB_TT[i]>=(minVSloc*FB_LOC[i]) else 0 for i in range(len(FB_TT))]
                        filt_timTT=[1 if i>=minVStime else 0 for i in FB_TT]
                        filt_segTS=breathlist[CurFile][stranimal]['BL']['SEG'][segrange]
    
                        TS_SEG=getlistfromfilter(FB_TS_TI,filt_segTS,1)
                        TS_FILT=getlistfromfilter(FB_TS_TI,qual_filter,1)
                        
                        mergedfilter=[min(
                            filt_segTS[i],filt_segTT[i],filt_locTT[i],
                            filt_timTT[i])
                            for i in range(len(FB_TT))]
    
                        #try:
                        #    filt_filt=breathlist[CurFile][stranimal]['BL']['filter']
                        #    TS_FILT=getlistfromfilter(FB_TS_TI,filt_filt,1)
                        #except:
                        #    TS_FILT=FB_TS_TI
                            
                        AP_SPEC=getlistfromfilter(FB_TS_TI,mergedfilter,1)
                        freqHz=60/(TS[1]-TS[0])
                        SPEC_OUT+=''.join(['\n'+CurFile+'\tanimal '+stranimal+'\t'+str(i) for i in AP_SPEC])
                        if timeorapnea=='':
                            TS_SPEC=AP_SPEC
                        else:
                            TS_SPEC=[]
                            timelist=timeorapnea.split(',')
                            try:
                                for i in timelist:
                                    TS_SPEC.append(float(i))
                            except:
                                print('error in times selected for graphs - '+str(i))
            
                        ## generate output graphs for each timestamp in a list (and save them)
                        for i in range(len(TS_SPEC)):
                            ##
                            timewindow=[TS_SPEC[i]-gwin/2.0,TS_SPEC[i]+gwin/2.0]
                            ##
                            savepath=rootsavepath+CurFile+'_animal_'+stranimal+'_'+str(TS_SPEC[i])
                            plethgraphint(
                                timewindow,ymin,ymax,TS,CT,
                                FB_TS_TI,FB_TS_TE,AP_SPEC,
                                TS_SEG,TS_FILT,
                                FeatureOptions,inchX,inchY,savepath+'_trace.png',
                                saveorshow)
                            ##
                    except:
                        print('unable to plot animal - '+stranimal)
        #%%                        
                
        except:
            print('error processing file '+xFilePath)
    if saveorshow=='save':
        with open (rootsavepath+'ApneaList.txt','wb') as f:
            f.write(SPEC_OUT.encode('utf-8'))
        f.closed

    input('All Done...Press Enter to Exit')
#%%
if __name__=="__main__":
    main()
