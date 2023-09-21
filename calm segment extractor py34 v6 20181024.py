#!usr/bin/env python3
## /\ compatability line

## distribution notes - Calm Segment Extractor py34 v4.py
"""
Calm Segment Extractor by Chris Ward (C) 2015
updated for python 3.4 compatability by Chris Ward (C) 2016
provided free for non-commercial/fair use.

This program attempts to define periods of calm behavior
by marking contiguous segments below a movement score
(uses the output from the Movement Quantification script)


*recommended versions for dependencies*
*matplotlib [1.4.2]
*numpy [1.9.1]

User inputs:
*motion scores-tab delimited file containing movements scores by time
*animal information-tab delimited file containing animal information for
the motion files to be analyzed
*OutFile-name of the txt file to be output by this program

Customizable Settings:
*padding - amount of time to subtract from 'calm bouts' to correct for time stamp
and threshold inaccuracies when resumping calm behavior after an active bout
*baseline percentile - percentile of overall motion score considered 'background noise'
*relative threshhold - threshhold relative to baseline used to define calm vs avtive

Outputs:
*a tab delimited file with ...
    -animal information and time segments corresponding to 'calm behavior'
"""

## import modules
import datetime
import wardcode3 as wardcode
import matplotlib.pyplot as plt
import numpy

## define functions
def AutoCallSegs(timestamps,movement,pd,bs,rt):
    # determin threshold level for movement
    timestamps=[float(i) for i in timestamps]
    movement=[float(i) for i in movement]
    thresh=numpy.percentile(movement,bs)*rt
    # calculate intervals above and below theshold
    crossings=wardcode.getbelowthresh(movement,thresh)
    diffcross=wardcode.getdifflist(crossings)
    starts=wardcode.getlistfromfilter(timestamps[1:],diffcross,1)
    stops=wardcode.getlistfromfilter(timestamps[1:],diffcross,-1)
    if len(starts)<1:starts=[timestamps[0]-1]
    if len(stops)<1:stops=[timestamps[-1]+1]
    #align lists
    if starts[0]>stops[0]:
        starts=[timestamps[0]-1]+starts
    if starts[-1]>stops[-1]:
        stops.append(timestamps[-1])
    #populate calmseg tuples and check padding
    calmsegs=[]
    segdur=[]
    for i in range(min(len(starts),len(stops))):
        calmsegs.append((starts[i]+pd,stops[i]-pd))
        segdur.append((stops[i]-pd)-(starts[i]+pd))
    goodsegs=wardcode.getabovethresh(segdur,0)
    calmsegsout=wardcode.getlistfromfilter(calmsegs,goodsegs,1)

    return calmsegsout,thresh
        
    

def checkExpActScores(expdict,exp,bs,rt):
    # expdict - dictionary containing data
    # exp - current experiment
    # bs - baseline
    # rt - relative threshold
    ##
    anikey=[int(i) for i in expdict[exp].keys()]
    anikey.sort()
    spx=int(numpy.ceil(len(anikey)/4))

    if len(anikey)<4:
        spy=len(anikey)
    else:
        spy=int(numpy.ceil(len(anikey)/spx))
        
    plt.figure(exp)
    
    for i in range(len(anikey)):
        animal=str(anikey[i])
        cs=expdict[exp][animal]['auto']['calmsegs']
        ts=[float(i) for i in expdict[exp][animal]['data']['timestamp']]
        y1=[float(i) for i in expdict[exp][animal]['data']['movement']]
        noise=numpy.percentile(y1,bs)
        thresh=noise*rt
        aniname=expdict[exp][animal]['line']+'-'+expdict[exp][animal]['id']

        plt.subplot(spx,spy,i+1)
        
        plt.plot(hold=False)
        plt.plot(hold=True)
        plt.plot((ts[0],ts[-1]),
                 (thresh,thresh),'y-')
        plt.plot(ts,y1,'r-')
        plt.plot((ts[0],ts[-1]),
                 (noise,noise),'b-')
        for j in cs:
            plt.plot(j,(thresh,thresh),'ko-')
        plt.title('|'+str(i+1)+'|'+aniname)
        plt.axis([ts[0],ts[-1],0,thresh*3])
        
    plt.show()

    
## define main
def main():
    ## get filenames
    # get motion scores
    MotionName=wardcode.guiOpenFileName({'title':'Open Motion Score File','filetypes':[('motion','.mtn'),('all files','.*')]})
    # get animal information
    AnimalName=wardcode.guiOpenFileName({'title':'Open Animal Information File','filetypes':[('animal list','.al'),('all files','.*')]})
    # get output filename
    outputname=wardcode.guiSaveFileName({'title':'Save Output As...'})
    
    ## set parameters
    PD=wardcode.getInt('pad inactive time by __ seconds:')
    BS=wardcode.getInt('consider baseline noise at __ percentile of movement signal (3% recommended)')
    RT=wardcode.getFloat('set relative threshold for movement at __ x of baseline noise (1.4x recommended)')
    CheckCalls=wardcode.getYN('Check calm segment calls? (y/n)')
    
    ## get data
    MotionDict=wardcode.dataDictUnfold(
        wardcode.dataParseTabDelToColumns(
            [i.lower() for i in wardcode.dataGrab(MotionName)]
            ,0)
        )
    AnimalDict=wardcode.dataDictUnfold(
        wardcode.dataParseTabDelToColumns(
            [i.lower() for i in wardcode.dataGrab(AnimalName)]
            ,0)
        )

    ## convert motion scores and timestamps to numbers
    for i in range(len(MotionDict['movement'])):
        MotionDict['movement'][i]=float(MotionDict['movement'][i])
        MotionDict['timestamp'][i]=float(MotionDict['timestamp'][i])
        
    ## parse MotionDict into experiment groups
    ExpDict={}
    # step through experiments to get animal information
    for Exp in set(MotionDict['filename']):
        ##
        print(str(datetime.datetime.now())+' : parsing data : '+Exp)
        ExpDict[Exp]={}
        CurAniDict={}
        CurAniDict[Exp]={}
        # populate current experiment animal information
        for k in AnimalDict.keys():
            CurAniDict[Exp][k]=wardcode.getlistfromfilter(AnimalDict[k],AnimalDict['video filename'],Exp)
        # iterate through animals in current video and get info
        ##
        filefilter=[1 if i==Exp else 0 for i in MotionDict['filename']]
        CurExp={}
        # populate CurExp dictionary with animal, timestamp, and movement data
        for k in ['animal','timestamp','movement']:
            CurExp[k]=wardcode.getlistfromfilter(MotionDict[k],filefilter,1)
        # grab the data from the current experiment - auto populate animals with motion data using "set" passing the current file filter
        for animal in set(
            wardcode.getlistfromfilter(
                MotionDict['animal'],MotionDict['filename'],Exp)
            ):
            
            ExpDict[Exp][animal]={}
            ExpDict[Exp][animal]['data']={}
            for k in AnimalDict.keys():
                try:
                    ExpDict[Exp][animal][k]=''.join(
                        wardcode.getlistfromfilter(
                        CurAniDict[Exp][k],CurAniDict[Exp]['video chamber'],animal)
                        )
                except:
                    ExpDict[Exp][animal][k]='unk'
            animalfilter=[1 if i==animal else 0 for i in CurExp['animal']]
            for k in ['timestamp','movement']:#<-MotionDict.keys():
            
                ExpDict[Exp][animal]['data'][k]=wardcode.getlistfromfilter(
                    CurExp[k],
                    animalfilter,
                    1)
 
    ## auto call segments
    for Exp in ExpDict:
        print(str(datetime.datetime.now())+' : calling calm segs : '+Exp)
        for animal in ExpDict[Exp]:
            TS=ExpDict[Exp][animal]['data']['timestamp']
            ExpDict[Exp][animal]['auto']={'calmsegs':[],'thresh':0}
            ExpDict[Exp][animal]['auto']['calmsegs'],ExpDict[Exp][animal]['auto']['thresh']=AutoCallSegs(
                TS,ExpDict[Exp][animal]['data']['movement'],PD,BS,RT)

            ExpDict[Exp][animal]['cBS']=BS
            ExpDict[Exp][animal]['cRT']=RT
            cBS=BS
            cRT=RT
        
        ##
        if CheckCalls=='y':
            while 1:
                checkExpActScores(ExpDict,Exp,cBS,cRT)
                if wardcode.getYN('Accept current results ("N" to try alternate settings)\n')=='y':
                    break
                cBS=wardcode.getInt('consider baseline noise at __ percentile of movement signal (3% recommended)')
                cRT=wardcode.getFloat('set relative threshold for movement at __ x of baseline noise (1.4x recommended)')
                for animal in ExpDict[Exp]:
                    ExpDict[Exp][animal]['auto']['calmsegs'],ExpDict[Exp][animal]['auto']['thresh']=AutoCallSegs(
                        TS,ExpDict[Exp][animal]['data']['movement'],PD,cBS,cRT)                       
                ExpDict[Exp][animal]['cBS']=cBS
                ExpDict[Exp][animal]['cRT']=cRT
    ## prepare header - asciifile, line, id, animalcode, subsegment, mainsegment, start, stop, base, relthresh, absthresh
    outheader=("{asciifile}\t{videofile}\t{line}\t{idno}\t{animalcode}\t{subsegment}\t{mainsegment}\t{start}\t{stop}\t{base}\t{relthresh}\t{absthresh}".format(
        asciifile='asciifile',videofile='videofile',line='line',idno='idno',animalcode='animalcode',
        subsegment='subsegment',mainsegment='mainsegment',start='start',stop='stop',
        base='base',relthresh='relthresh',absthresh='absthresh'))
    ## output data
    outlist=[]
    outlist.append(outheader)
    for Exp in ExpDict:
        for animal in ExpDict[Exp]:
            for startseg,stopseg in ExpDict[Exp][animal]['auto']['calmsegs']:
                nextline=("{asciifile}\t{videofile}\t{line}\t{idno}\t{animalcode}\t{subsegment}\t{mainsegment}\t{start}\t{stop}\t{base}\t{relthresh}\t{absthresh}".format(
        asciifile=ExpDict[Exp][animal]['filename'],videofile=Exp,
        line=ExpDict[Exp][animal]['line'],
        idno=ExpDict[Exp][animal]['id'],animalcode=ExpDict[Exp][animal]['chamber'],
        subsegment='calm',mainsegment='calm',start=startseg,stop=stopseg,
        base=ExpDict[Exp][animal]['cBS'],relthresh=ExpDict[Exp][animal]['cRT'],
        absthresh=ExpDict[Exp][animal]['auto']['thresh']))
                outlist.append(nextline)
    ## write results to output file
    with open(outputname+'.seg','w') as f:
        f.write('\n'.join(outlist))
        f.close()
        
    input('finished calm segment extraction...\npress ENTER to exit')

## run main
if __name__=='__main__':
    main()
