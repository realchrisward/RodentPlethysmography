#!/usr/bin/env/python
## /\ compatability line

## distribution notes - Movement Quantification py34 v8.py
"""
Movement Quantification by Chris Ward (C) 2014
updated for python 3.4 compatability by Chris Ward (C) 2015
revised 2018 by Chris Ward
software is provided "as is" and is offered under the
"MIT license".

This program attempts to quantify movement within
an entire video image, or within subregions of a
video image.  The calculation is based on comparing
the current video frame to the average of previous
video frames and quantifying differences in pixel
values (grayscale)

***NOTE-opencv and numpy are required***
*recommended versions for dependencies*
*opencv [3.1.0]
*numpy [1.9.1]

User inputs:
*VidFiles-name of the video file to be analyzed (selected through GUI)
*OutFile-name of the txt file to be output by this program (selected through GUI)

Customizable Settings:
*FrameSize-size of the object window
*ResolutionDS-downscale factor for video resolution
*DesiredFrameRate-Framerate for movement compatisons
    (determines if some frames will be skipped in analysis)
*TimerOffSet-Time in seconds of offset between start of Video File
    and other analysis (i.e. Plethysmography) default is 0


Outputs:
*a tab delimited file with ...
    -a column for timestamps (calculated from video framerate)
    -and a column with motion scores for each region being analyzed
"""

## import modules
import numpy as np
import cv2
import tkinter
import tkinter.filedialog
import os
## set global variables
CurrObj=1
outs=[]
gframe=None
framesize=None

## define functions - Application Specific
def getVideoData(filename):
    #load video and get metadata
    #based on positions of metadata within cv2.VideoCapture.get()
    cap=cv2.VideoCapture(filename)
    frameX=cap.get(3) #width of video
    frameY=cap.get(4) #height of video
    frameRate=cap.get(5) #framerate of video
    frameTotal=float(cap.get(7)) #total numb of frames in video (to calc duration)
    fileDuration='aprox. %d min %d sec'%(int(frameTotal/frameRate/60),frameTotal/frameRate%60)
    fileDurationSec=float(frameTotal)/float(frameRate)
    print('filename: %s'%filename)
    print('resolution: %d x %d @ %d fps'%(frameX,frameY,frameRate))
    print('length: %s'%fileDuration)
    cap.release()
    return frameX,frameY,frameRate,frameTotal,fileDuration,fileDurationSec

def getSignalData(filename):
    #load ascii file and get recording duration
    with open(filename) as f:
        #seek to end of file
        f.seek(0,2)
        binlen=f.tell()
        #jump 1000 bytes before the end of file - should work unless byte length per line is too large
        f.seek(binlen-1000,0)
        lines=f.read().split('\n')
        ##
        lastline=lines[-2]
        if ',' in lastline:
            tstext=lastline.split(',')
        else:
            tstext=lastline.split()
        ts=float(tstext[0])
    return ts
    
    
def SelectFrames(filename,framesizeDivisor,skiptime=0): 
    #load video and get metadata
    cap=cv2.VideoCapture(filename)
    frameX=cap.get(3)
    frameY=cap.get(4)
    #advance time in case camera does not start in proper position
    for i in range(int(float(cap.get(5))*skiptime)):
        cap.read()
    #calculate resized frames
    newFrameX=int(frameX/framesizeDivisor)
    newFrameY=int(frameY/framesizeDivisor)
    #call global variables
    global gframe
    global framesize
    global CurrObj
    # go to and show 2nd frame (in case first is blank)
    ret,gframe=cap.read()
    ret,gframe=cap.read()
    # resize frame if needed
    if framesizeDivisor!=1:
        gframe=cv2.resize(gframe,(newFrameX,newFrameY))
    # run code to extract object locations
    print('double click to assign a new object...')
    print('now defining object#%s'%CurrObj) 
    cv2.waitKey(20)
    cv2.namedWindow('Video Window')
    cv2.setMouseCallback('Video Window',getBox)
    while(1):
        cv2.imshow('Video Window',gframe)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()
    cap.release()
    return outs

def getBox(event,x,y,flags,param):
    # listen for left mouse button clicks
    if event == cv2.EVENT_LBUTTONDBLCLK:
        # get global variables
        global framesize
        global outs
        global CurrObj
        global gframe
        # set boundries of box centered on click location
        x1=int(x-framesize[0]/2)
        x2=int(x+framesize[0]/2)
        y1=int(y-framesize[1]/2)
        y2=int(y+framesize[1]/2)
        # keep box within the bounds of the image
        if x1<0:x1=0
        if y1<0:y1=0
        if x2>len(gframe[0])-1:x2=len(gframe[0])-1
        if y2>len(gframe)-1:y2=len(gframe)-1
        # display the rectangle
        cv2.rectangle(gframe,(x1,y1),(x2,y2),(255,255,255),5)
        # add the box to the list of ROI's for analysis
        outs.append((y1,y2,x1,x2))
        CurrObj+=1
        print('now defining object #%s'%CurrObj)

def playVideoFrames(filename,frameBounds,framesizeDivisor):
    #load video and get metadata
    cap=cv2.VideoCapture(filename)
    frameX=cap.get(3)
    frameY=cap.get(4)
    #calculate resized frames
    newFrameX=int(frameX/framesizeDivisor)
    newFrameY=int(frameY/framesizeDivisor)
    boxDict={}
    while(1):
        # grab image from video
        ret,frame=cap.read()
        if ret!=True: break
        # resize frame if needed
        if framesizeDivisor!=1:
            frame=cv2.resize(frame,(newFrameX,newFrameY))
        # get ROI video for each of the ROI's in the analysis
        for box in range(len(frameBounds)):
            boxDict[box+1]=frame[
                frameBounds[box][0]:frameBounds[box][1],
                frameBounds[box][2]:frameBounds[box][3],
                ]
            cv2.imshow('%s'%str(box+1),boxDict[box+1])
        cv2.imshow('Video Window',frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyAllWindows()
    cap.release()
    
def getMotionRunAvgDiff(filename,framerateDivisor,framesizeDivisor,runAvgWeight,frameBounds,playback):
    #load video and get metadata
    cap=cv2.VideoCapture(filename)
    frameX=cap.get(3)
    frameY=cap.get(4)
    frameRate=cap.get(5)
    frameTotal=float(cap.get(7)) #total numb of frames in video (to calc duration)
    progressFrames=[i for i in range(int(frameTotal))][::int(frameTotal/10)]
    progressDict={}
    for i in progressFrames:
        progressDict[i]=int(i/frameTotal*100)
        
    #calculate resized frames
    newFrameX=int(frameX/framesizeDivisor)
    newFrameY=int(frameY/framesizeDivisor)
    print('\n*********\n\nAnalyzing...\n%s\n%dx%d - %d fps'%(filename,cap.get(3)/framesizeDivisor,cap.get(4)/framesizeDivisor,round(float(cap.get(5))/framerateDivisor)))
    #grab first frame
    ret,frame=cap.read()
    # resize frame if needed
    if framesizeDivisor!=1:
        frame=cv2.resize(frame,(newFrameX,newFrameY))
    bwFrame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    avg=np.float32(bwFrame.copy())
    i=0 # used for counting skipped frames when down sampling and assigning time stamp
    # prepare output dictionary
    frameMotionDict={}
    for j in range(len(frameBounds)):
        frameMotionDict[j+1]=[]
    # add TimeStamp collumn
    frameMotionDict['TimeStamp']=[]
    # begin video playback
    print('0%...')
    while(1):
        i+=1
        # get frame
        if i in progressDict:
            print(str(progressDict[i])+'%...')
        ret,frame=cap.read()
        # check if frame should be skipped or if it is invalid
        if i%framerateDivisor!=0:continue
        if ret==False:break
        # add time stamp
        frameMotionDict['TimeStamp'].append(i*(1.0/frameRate))
        # resize frame
        if framesizeDivisor!=1:
            frame=cv2.resize(frame,(newFrameX,newFrameY))
        # convert to grayscale
        bwFrame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        # split frame into subregions
        for curObj in range(len(frameBounds)):
            curFrame=bwFrame[
                frameBounds[curObj][0]:frameBounds[curObj][1],
                frameBounds[curObj][2]:frameBounds[curObj][3],
                ]
            try:
                currAvg=avg[
                    frameBounds[curObj][0]:frameBounds[curObj][1],
                    frameBounds[curObj][2]:frameBounds[curObj][3],
                    ]
            except:
                currAvg=curFrame
                print('avg frame missing for : %s'%str(i))
            # calc movement score
            dif=cv2.absdiff(currAvg,np.float32(curFrame))
            # prep playback of sub regions
            if playback=='all' or playback=='objects':
                # convertScaleAbs - renormalizes the pixel intensities to avoid floating point artifacts
                dif2=cv2.convertScaleAbs(dif)
                try:
                    cv2.imshow('feed %s'%str(int(curObj)+1),curFrame)
                    cv2.imshow('movement %s'%str(int(curObj)+1),dif2)
                except: print('problem with video frame subdivision')
            # record motion score
            try:
                frameMotionDict[int(curObj)+1].append(sum(sum(dif)))
            except:
                frameMotionDict[int(curObj)+1].append('error')
        # updated running average of frame #***just moved this to follow frame comparison
        cv2.accumulateWeighted(bwFrame,avg,runAvgWeight)
        
        # prep playback of raw feed
        if playback=='all' or playback=='raw feed':
            cv2.imshow('raw feed',bwFrame)
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    cap.release()
    return frameMotionDict

def ResetGlobals():
    global CurrObj
    global outs
    global gframe

    CurrObj=1
    outs=[]
    gframe=None

def ResetSettings():
    FrameSize=(100,100)
    TimerOffset=0
    ResolutionDS=1
    DesiredFrameRate=5 #best to choose an easily divisible number
    CurrentFrameWeight=0.1
    Playback='none' #'all','objects','raw feed','none'
    SkipInto=5
    ynCheckFrames='n'
    return FrameSize,TimerOffset,ResolutionDS,DesiredFrameRate,CurrentFrameWeight,Playback,SkipInto,ynCheckFrames

def OutputResults(outputfilename,dataDict):
    # open the output file
    openout=open(outputfilename+'.mtn','w')
    # write the header line to the file
    openout.write('FileName'+'\t'+'parameterstring'+'\t'+'TimeStamp'+'\t'+'animal'+'\t'+'movement'+'\n')
    # append output data for each video analyzed
    for VidFile in dataDict:
        print('output for :'+str(VidFile))
        TS=dataDict[VidFile]['OutputData']['TimeStamp']
        OutKeys=sorted([i for i in dataDict[VidFile]['OutputData'].keys() if i!='TimeStamp'])
        curfilename=os.path.basename(VidFile)
        
        parameterstring=''.join([str(i) for i in
                                  [
            'framerate:',dataDict[VidFile]['VidRate'],
            ',desframerate:',dataDict[VidFile]['DesiredFrameRate'],
            ',resolutionds:',dataDict[VidFile]['ResolutionDS'],
            ',frameweight:',dataDict[VidFile]['CurrentFrameWeight'],
            ',mousepositions:',dataDict[VidFile]['ObjectFrames']
            ]
                                  ])
        for i in range(len(TS)):
            for j in OutKeys:
                openout.write(curfilename+'\t'+parameterstring+'\t'+str(TS[i])+'\t'+
                              str(j)+'\t'+str(dataDict[VidFile]['OutputData'][j][i])+'\n')
    openout.close()

def ChangeSettings(framesize,timeroffset,resolutionDS,desiredFrameRate,currentFrameWeight,playback,skipinto,yncheckframes,keepSettings):
    # get current setting values
    values=['Frame Size - %s'%str(framesize),
            'Timer Offset - %s'%str(timeroffset),
            'Resolution Down Scale Factor - %s'%str(resolutionDS),
            'Desired Frame Rate (fps) - %s'%str(desiredFrameRate),
            'Frame Weight for Motion Scoring - %s'%currentFrameWeight,
            'Video Playback - %s'%playback,
            'Skip into video for frame assignment __sec - %s'%str(skipinto),
            'Check frame sizes before assignment - %s'%yncheckframes
            ]
            
    keys=[i+1 for i in range(len(values))]
    
    while(keepSettings!='y'):
        #select option to change
        OptionSelect,dumpVal=getChoice(keys,values,'Select Setting To Change')
        #change option
        # fs
        if OptionSelect==1:
            newFX=getInt('Enter new Frame Size (x dimension in pixels)')
            newFY=getInt('Enter new Frame Size (y dimension in pixels)')
            framesize=(newFX,newFY)
        # to
        elif OptionSelect==2:
            timeroffset=getFloat('Timer Offset for Time Stamping (seconds)- default 0, (+)for video start after, (-)for video start before')
        # rds
        elif OptionSelect==3:
            resolutionDS=getInt('Resolution Scaling Factor (decrease resolution from raw feed by this factor during analysis')
        # dfr
        elif OptionSelect==4:
            desiredFrameRate=getInt('Please Select Desired Frame Rate For Analysis (fps)')
        # cfw
        elif OptionSelect==5:
            currentFrameWeight=getFloat('Current Frame Weight (number between 0 and 1...ex 0.1)')
        # pb
        elif OptionSelect==6:
            dumpkey,playback=getChoice(['1','2','3','4'],['all','objects','raw feed','none'],'Video Playback Options...')

        #si
        elif OptionSelect==7:
            skipinto=getInt('Please select desired amount of time to skip (seconds) for frame assignment')
        #ycf
        elif OptionSelect==8:
            yncheckframes=input('Preview Frame Size before final assignment? (y/n)')
        #confirm
        values=['Frame Size - %s'%str(framesize),
                'Timer Offset - %s'%str(timeroffset),
                'Resolution Down Scale Factor - %s'%str(resolutionDS),
                'Desired Frame Rate (fps) - %s'%str(desiredFrameRate),
                'Frame Weight for Motion Scoring - %s'%currentFrameWeight,
                'Video Playback - %s'%playback,
                'Skip into video for frame assignment __sec - %s'%str(skipinto),
                'Check frame sizes before assignment - %s'%yncheckframes]            
        for i in range(len(keys)):
            print('%8s:%s'%(keys[i],values[i]))
        keepSettings=getYN('\n***confirm these settings? (n-to make additional changes)***')
        
    #show current settings
    print('Current Analysis Settings')
    for i in range(len(keys)):
        print('%8s:%s'%(keys[i],values[i]))
    #exit
    return framesize,timeroffset,resolutionDS,desiredFrameRate,currentFrameWeight,playback,skipinto,yncheckframes
    
## define Functions - Generic
def GUIopenfilenames(kwargs={}): 
    """A quick callable function to generate
a GUI for selecting multiple files to open.\n......\n
Function calls on tkFileDialog and uses those arguments
(declare as a dictionairy)
{defaultextensions:'',filetypes:'',initialdir:'',...
initialfile:'',multiple:'',message:'',parent:'',title:''}
......"""
    root=tkinter.Tk()
    openfilenames=tkinter.filedialog.askopenfilenames(**kwargs)
    root.destroy()
    return openfilenames

def GUIopenfilename(kwargs={}):
    """A quick callable function to generate
a GUI for selecting a file to open.\n......\n
Function calls on tkFileDialog and uses those arguments
(declare as a dictionairy)
{defaultextension:'',filetypes:'',initialdir:'',...
initialfile:'',multiple:'',message:'',parent:'',title:''}
......"""
    root=tkinter.Tk()
    openfilename=tkinter.filedialog.askopenfilename(**kwargs)
    root.destroy()
    return openfilename

def GUIsavefilename(kwargs={}):
    """A quick callable function to generate
a GUI for selecting a filename and path for saving.\n......\n
Function calls on tkFileDialog and uses those arguments
(declare as a dictionairy)
{defaultextension:'',filetypes:'',initialdir:'',...
initialfile:'',multiple:'',message:'',parent:'',title:''}
......"""
    root=tkinter.Tk()
    savefilename=tkinter.filedialog.asksaveasfilename(**kwargs)
    root.destroy()
    return savefilename

def getInt(text=''):
    """Prompts user for an integer number.
accepts integers
returns the entered integer
other inputs prompt user to re-enter a response"""
    while 1:
        print(text)
        try:
            userInput=int(input('Please enter an integer:'))
            return userInput
        except: print('\nInvalid input - not recognized as an integer\n[Proper response required to exit loop]')

def getFloat(text=''):
    """Prompts user for a real number.
accepts any real number (in integer and decimal format)
returns the entered number
other inputs prompt user to re-enter a response"""
    while 1:
        print(text)
        try:
            userInput=float(input('Please enter a number:'))
            return userInput
        except: print('\nInvalid input - not recognized as a real number\n[Proper response required to exit loop]')

def getChoice(keys,values,text=''):
    """Prompts user to select from a list of options.
the list is presented in two columns:
keys (input choices) : values (option values)
***note - the number of keys and values must match and...
   key values must be unique otherwise ambiguous returns may result
***also note - to use a number list for the key,...
   convert the number entries to strings

accepts inputs that match the key list
returns a tuple of the (key,value) corresponding to the choice
other inputs prompt user to re-enter a response"""
    #print keys
    text_keys=[str(j) for j in keys]
    while 1:
        print(text)
        for i in range(len(keys)):
            print('%8s:%s'%(keys[i],values[i]))
        userInput=input('Please select an option:')
        if userInput in keys:
            try:
                return (keys[keys.index(userInput)],values[keys.index(userInput)])
            except:
                return 'oops'
        elif userInput in  text_keys:
            try:
                return (keys[text_keys.index(userInput)],values[text_keys.index(userInput)])
            except:
                return 'more oops'
        else:
            print('\nInvalid input - not recognized as an option\n[Proper response required to exit loop]')

def getYN(text=''):
    """Prompts user for yes or no input.
accepts y,Y,yes,Yes,YES,n,N,no,No,NO.
returns 'y' for yes and 'n' for no.
other inputs prompt user to re-enter a response"""
    AcceptableResponses={'y':'y','yes':'y','n':'n','no':'n'}
    while 1:
        print(text)
        userInput=input('Please select Yes or No (y/n):').lower()
        if userInput in list(AcceptableResponses.keys()):
            return AcceptableResponses[userInput]
        else:
            print("""
Invalid input - not recognized as yes or no \n
[Proper response required to exit loop]""")
            
## main section

def main():
    ## get input filenames
    VidList=GUIopenfilenames({'title':'Select Video Files For Analysis',
                              'filetypes':[('avi video','.avi'),('wmv video','.wmv'),
                  ('all files','.*')
                  ]})
    VidList=list(VidList)
    VidList.sort()
    ## get ouput filename
    OutFile=GUIsavefilename({'title':'Select Filename for Output'})

    ## show file values and ascii lengths
    VidDict={}
    for VidFile in VidList:
        xVidX,xVidY,xVidRate,xVidFrCt,xVidDur,xVidDurSec = getVideoData(VidFile)
        VidDict[VidFile]={'VidX':xVidX,'VidY':xVidY,'VidRate':xVidRate,
                          'VidFrCt':xVidFrCt,'VidDur':xVidDur,'VidDurSec':xVidDurSec}
        try:
            VidDict[VidFile]['SigDur']=getSignalData(VidFile[:-14]+'.ascii')
            VidDict[VidFile]['Offset']=round(VidDict[VidFile]['SigDur']-VidDict[VidFile]['VidDurSec'],1)
        except:
            VidDict[VidFile]['SigDur']='unknown'
            VidDict[VidFile]['Offset']='unknown'
    #
    print('{Video:<15}\t{Signal:<15}\t{Offset:<11}\t{filename}'.format(Video='Video (s)',Signal='Signal (s)',
                                                                      Offset='Offset (s)',filename='Video Filename'))          
    
    for VidFile in VidList:
        print('{Video:<15}\t{Signal:<15}\t{Offset:<11}\t{filename}'.format(
            Video=VidDict[VidFile]['VidDurSec'],Signal=VidDict[VidFile]['SigDur'],
            Offset=VidDict[VidFile]['Offset'],filename=os.path.basename(VidFile)))
          
                                                   
    
    ## set default analysis settings
    (xFrameSize,xTimerOffset,xResolutionDS,xDesiredFrameRate,
    xCurrentFrameWeight,xPlayback,xSkipInto,xynCheckFrames)=ResetSettings()
    

    ## query for analysis setting changes and call globals for assingment
    global framesize
    global CurrObj

    for VidFile in VidList:
        ## show current settings
        print("\n\n***\n"+os.path.basename(VidFile)+"\n***")
        print("\n***Current Settings***\n")
        if VidDict[VidFile]['Offset']=='unknown':
            xTimerOffset=0
        else:
            xTimerOffset=VidDict[VidFile]['Offset']
    
        ChangeSettings(
            xFrameSize,xTimerOffset,xResolutionDS,xDesiredFrameRate,
            xCurrentFrameWeight,xPlayback,xSkipInto,xynCheckFrames,'y'
            )
        print('\n')

        ResetGlobals()
        KeepSettings=getYN('Keep Current Settings? (y-to keep,n-to change)\n')

        while 1:
            (xFrameSize,xTimerOffset,xResolutionDS,xDesiredFrameRate,
             xCurrentFrameWeight,xPlayback,xSkipInto,xynCheckFrames)=ChangeSettings(
                xFrameSize,xTimerOffset,xResolutionDS,xDesiredFrameRate,
                xCurrentFrameWeight,xPlayback,xSkipInto,xynCheckFrames,KeepSettings
                )
            framesize=xFrameSize
            # test object frame size
            if xynCheckFrames=='y':
                print('\n\n...\n'+
                      'test current frame size setting (press ESC while in Video Window to continue)')
                SelectFrames(VidFile,xResolutionDS,xSkipInto)
                ResetGlobals()
            
                # confirm settings
                print('\nRECONFIRM CURRENT SETTINGS')
                KeepSettings=getYN('Keep These Settings? (y-to keep,n-to change)\n')
            else:
                break
            if KeepSettings=='y': break
        VidDict[VidFile]['FrameSize']=xFrameSize
        VidDict[VidFile]['TimerOffset']=xTimerOffset
        VidDict[VidFile]['ResolutionDS']=xResolutionDS
        VidDict[VidFile]['DesiredFrameRate']=xDesiredFrameRate
        VidDict[VidFile]['CurrentFrameWeight']=xCurrentFrameWeight
        VidDict[VidFile]['Playback']=xPlayback
            

        # get object positions
        while 1:
            ResetGlobals()
            print('Select Frames...hit ESC in Video Window to continue\n')
            xObjectFrames=SelectFrames(VidFile,xResolutionDS,xSkipInto)
            VidDict[VidFile]['ObjectFrames']=xObjectFrames
            print('SubRegions in Analysis: %d\n%s'%(CurrObj-1,str(xObjectFrames)))
            print('Showing Video of Subregions hit ESC in Video Window to continue\n')
            playVideoFrames(VidFile,xObjectFrames,xResolutionDS)
            KeepSettings=getYN('Keep These Settings? (y-to keep,n-to change)\n')
            if KeepSettings=='y': break
        
    ## run motion detection
    for VidFile in VidList:
        VidRate=VidDict[VidFile]['VidRate']
        DesiredFrameRate=VidDict[VidFile]['DesiredFrameRate']
        ResolutionDS=VidDict[VidFile]['ResolutionDS']
        CurrentFrameWeight=VidDict[VidFile]['CurrentFrameWeight']
        ObjectFrames=VidDict[VidFile]['ObjectFrames']
        Playback=VidDict[VidFile]['Playback']
        
        OutputData=getMotionRunAvgDiff(
            VidFile,int(round(VidRate/DesiredFrameRate)),
            ResolutionDS,CurrentFrameWeight,
            ObjectFrames,Playback)
        VidDict[VidFile]['OutputData']=OutputData
    
    # output results
    OutputResults(OutFile,VidDict)
    input('ANALYSIS FINISHED\n(press enter to close program)')
    
## run program
if __name__=='__main__':
    main()
