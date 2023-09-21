#!usr/bin/env python3
## /\ compatability line
"""
WardBreathCaller - updated for python 3.6
(C) 2015 Christopher Ward
updated 2019-08-13

plethysmography data analysis code

## still needs
*error log, to indicate files that could not be found/analyzed


"""

## import modules
import wardcode3 as wardcode
import os
import json
import statistics

from scipy import signal
## basic functions
def getabovethresh(inputlist,thresh):
    abovethreshlist=[1 if i>thresh else 0
                     for i in inputlist]
    return abovethreshlist

def getinrangelist(inputlist,minval,maxval):
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
                           float(segdic['start'][i]),
                           float(segdic['stop'][i])))
    return outDict

def getbelowthresh(inputlist,thresh):
    belowthreshlist=[1 if i<thresh else 0
                     for i in inputlist]
    return belowthreshlist

def getdifflist(inputlist):
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
    """can get TV calcs using flox data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    sumbyindexlist=[sum(
        inputlist[indexlist[i]:indexlist[i+1]]
                        )
                    for i in range(len(indexlist)-1)]
    return sumbyindexlist

def getmaxbyindex(inputlist,indexlist):
    """can get PIF calcs using flox data and crossvals
note that cross ref of indexlist with Ti vs Te timestamps
is needed for segregation of the data
"""
    maxbyindexlist=[max(inputlist[indexlist[i]:indexlist[i+1]])
                    for i in range(len(indexlist)-1)]
    return maxbyindexlist

def getminbyindex(inputlist,indexlist):
    """can get PIF calcs using flox data and crossvals
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
    
def getmed(inputlist):
    """returns the median of the values in a list
    """
    try:
        return statistics.median(inputlist)
    except:
        return 'NAN'

def mergelistmax(lst1,lst2):
    try:
        return [max([lst1[i],lst2[i]]) for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistmin(lst1,lst2):
    try:
        return [min([lst1[i],lst2[i]]) for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistadd(lst1,lst2):
    try:
        return [lst1[i]+lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistmult(lst1,lst2):
    try:
        return [lst1[i]*lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistsubt(lst1,lst2):
    try:
        return [lst1[i]-lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def mergelistdiv(lst1,lst2):
    try:
        return [lst1[i]/lst2[i] for i in range(len(lst1))]
    except:
        print('incompatible lists')

def tryget3(x,k1,k2,k3):
    try: return x[k1][k2][k3]
    except: return 'NAN'

def plethdatawriter(AllOutData,OutFilename,AP,xAniData,xSegData):
    ##
    with open(OutFilename,'w') as f:
        ##
        headertext=(
            "{filename}\t{animalNo}\t{animalLine}\t{animalID}\t{Segment}\t{segStart}\t{segStop}\t"+
            "{N}\t{TI}\t{TE}\t{TT}\t{BPM}\t{iTV}\t{eTV}\t{PIF}\t{PEF}\t{DVTV}\t{ISTT}\t{ISBPM}\t{per500}\t"+
            "{NonApN}\t{NonApTI}\t{NonApTE}\t{NonApTT}\t{NonApBPM}\t{NonApiTV}\t{NonApPIF}\t"+
            "{Ap05}\t{Ap08}\t{Ap10}\t{Ap2seg}\t{Ap3seg}\t{Ap2loc}\t{Ap3loc}\t{ApStrict}\t{ApN}\t{ApTT}\t"+
            "{Sigh15TV}\t{Sigh20TV}\t{Sigh30TV}\t{Sigh15PIF}\t{Sigh20PIF}\t{Sigh30PIF}\t{Sigh15PEF}\t{Sigh20PEF}\t{Sigh30PEF}\t"+
            "{median_TI}\t{median_TE}\t{median_TT}\t{median_BPM}\t{median_iTV}\t{median_eTV}\t{median_PIF}\t{median_PEF}\t{median_ISTT}\t"+
            "{minPIF}\t{minTI}\t{maxDVTV}\t{maxPer500}\t{TTwin}\t{per500win}\t{minApTime}\t{minApSeg}\t{minAploc}\t"+
            "{SIGHwin}\t{Smoothed}\n").format(
                filename='filename',animalNo='animalNo',animalLine='animalLine',animalID='animalID',
                Segment='Segment',segStart='segStart',segStop='segStop',
                N='N',TI='TI',TE='TE',TT='TT',BPM='BPM',iTV='iTV',eTV='eTV',
                PIF='PIF',PEF='PEF',DVTV='DVTV',ISTT='ISTT',ISBPM='ISBPM',per500='per500',
                NonApN='NonApN',NonApTI='NonApTI',NonApTE='NonApTE',NonApTT='NonApTT',
                NonApBPM='NonApBPM',NonApiTV='NonApiTV',NonApPIF='NonApPIF',
                Ap05='Ap05',Ap08='Ap08',Ap10='Ap10',Ap2seg='Ap2seg',Ap3seg='Ap3seg',
                Ap2loc='Ap2loc',Ap3loc='Ap3loc',ApStrict='ApStrict',ApN='ApN',ApTT='ApTT',
                Sigh15TV='Sigh1.5xTV',Sigh20TV='Sigh2xTV',Sigh30TV='Sigh3xTV',
                Sigh15PIF='Sigh1.5xPIF',Sigh20PIF='Sigh2xPIF',Sigh30PIF='Sigh3xPIF',
                Sigh15PEF='Sigh1.5xPEF',Sigh20PEF='Sigh2xPEF',Sigh30PEF='Sigh3xPEF',
                minPIF='minPIF',minTI='minTI',maxDVTV='maxDVTV',maxPer500='maxPer500',
                TTwin='TTwin',per500win='per500win',minApTime='minApTime',minApSeg='minApSeg',minAploc='minAploc',
                SIGHwin='SIGHwin',Smoothed='Smoothed',
                median_TI='median_TI',median_TE='median_TE',median_TT='median_TT',median_BPM='median_BPM',median_iTV='median_iTV',
                median_eTV='median_eTV',median_PIF='median_PIF',median_PEF='median_PEF',median_ISTT='median_ISTT'                
                )

        f.write(headertext)
        # prepare output data.  group output by filenames        
        for filename in AllOutData.keys():
            print(filename)
            OutData=AllOutData[filename]
            
            for Animal in OutData:
                animalNo=str(Animal)
                animalLine=str(xAniData['line'][
                    mergelistmin(
                        [1 if i==filename[:-6] else 0 for i in xAniData['filename']],
                        [1 if i==str(Animal) else 0 for i in xAniData['chamber']]
                        ).index(1)]
                    )
                animalID=str(xAniData['id'][
                    mergelistmin(
                        [1 if i==filename[:-6] else 0 for i in xAniData['filename']],
                        [1 if i==str(Animal) else 0 for i in xAniData['chamber']]
                        ).index(1)]
                    )
            
                for seg in OutData[Animal]:
                    
                    Segment=str(seg)
                    segStart=str(xSegData['start'][
                        mergelistmin(
                            mergelistmin(
                                [1 if i==seg else 0 for i in xSegData['subsegment']],
                                [1 if i==filename[:-6] else 0 for i in xSegData['asciifile']]),
                            [1 if i==str(Animal) else 0 for i in xSegData['animalcode']]).index(1)]
                                 )
                    segStop=str(xSegData['stop'][
                        mergelistmin(
                            mergelistmin(
                                [1 if i==seg else 0 for i in xSegData['subsegment']],
                                [1 if i==filename[:-6] else 0 for i in xSegData['asciifile']]),
                            [1 if i==str(Animal) else 0 for i in xSegData['animalcode']]).index(1)]
                                )

                    outputtext=(
                        "{xfilename}\t{xanimalNo}\t{xanimalLine}\t{xanimalID}\t{xSegment}\t{xsegStart}\t{xsegStop}\t"+
                        "{N}\t{TI}\t{TE}\t{TT}\t{BPM}\t{iTV}\t{eTV}\t{PIF}\t{PEF}\t{DVTV}\t{ISTT}\t{ISBPM}\t{per500}\t"+
                        "{NonApN}\t{NonApTI}\t{NonApTE}\t{NonApTT}\t{NonApBPM}\t{NonApiTV}\t{NonApPIF}\t"+
                        "{Ap05}\t{Ap08}\t{Ap10}\t{Ap2seg}\t{Ap3seg}\t{Ap2loc}\t{Ap3loc}\t{ApStrict}\t{ApN}\t{ApTT}\t"+
                        "{Sigh15TV}\t{Sigh20TV}\t{Sigh30TV}\t{Sigh15PIF}\t{Sigh20PIF}\t{Sigh30PIF}\t{Sigh15PEF}\t{Sigh20PEF}\t{Sigh30PEF}\t"+
                        "{median_TI}\t{median_TE}\t{median_TT}\t{median_BPM}\t{median_iTV}\t{median_eTV}\t{median_PIF}\t{median_PEF}\t{median_ISTT}\t"+
                        "{minPIF}\t{minTI}\t{maxDVTV}\t{maxPer500}\t{TTwin}\t{per500win}\t{minApTime}\t{minApSeg}\t{minAploc}\t"+
                        "{SIGHwin}\t{Smoothed}\n").format(
                            xfilename=filename,
                            xanimalNo=animalNo,
                            xanimalLine=animalLine,
                            xanimalID=animalID,
                            xSegment=Segment,
                            xsegStart=segStart,
                            xsegStop=segStop,
                            N=str(tryget3(OutData,Animal,seg,'N')),
                            TI=str(tryget3(OutData,Animal,seg,'TI')),
                            TE=str(tryget3(OutData,Animal,seg,'TE')),
                            TT=str(tryget3(OutData,Animal,seg,'TT')),
                            BPM=str(tryget3(OutData,Animal,seg,'BPM')),
                            iTV=str(tryget3(OutData,Animal,seg,'iTV')),
                            eTV=str(tryget3(OutData,Animal,seg,'eTV')),
                            PIF=str(tryget3(OutData,Animal,seg,'PIF')),
                            PEF=str(tryget3(OutData,Animal,seg,'PEF')),
                            DVTV=str(tryget3(OutData,Animal,seg,'dVTV')),
                            ISTT=str(tryget3(OutData,Animal,seg,'ISTT')),
                            ISBPM=str(tryget3(OutData,Animal,seg,'ISBPM')),
                            per500=str(tryget3(OutData,Animal,seg,'per500')),
                            NonApN=str(tryget3(OutData,Animal,seg,'NonApN')),
                            NonApTI=str(tryget3(OutData,Animal,seg,'NonApTI')),
                            NonApTE=str(tryget3(OutData,Animal,seg,'NonApTE')),
                            NonApTT=str(tryget3(OutData,Animal,seg,'NonApTT')),
                            NonApBPM=str(tryget3(OutData,Animal,seg,'NonApBPM')),
                            NonApiTV=str(tryget3(OutData,Animal,seg,'NonApiTV')),
                            NonApPIF=str(tryget3(OutData,Animal,seg,'NonApPIF')),
                            Ap05=str(tryget3(OutData,Animal,seg,'Ap05')),
                            Ap08=str(tryget3(OutData,Animal,seg,'Ap08')),
                            Ap10=str(tryget3(OutData,Animal,seg,'Ap10')),
                            Ap2seg=str(tryget3(OutData,Animal,seg,'Ap2s')),
                            Ap3seg=str(tryget3(OutData,Animal,seg,'Ap3s')),
                            Ap2loc=str(tryget3(OutData,Animal,seg,'Ap2l')),
                            Ap3loc=str(tryget3(OutData,Animal,seg,'Ap3l')),
                            ApStrict=str(tryget3(OutData,Animal,seg,'ApStrict')),
                            ApN=str(tryget3(OutData,Animal,seg,'ApN')),
                            ApTT=str(tryget3(OutData,Animal,seg,'ApStrTT')),
                            Sigh15TV=str(tryget3(OutData,Animal,seg,'Sigh1.5xTV')),
                            Sigh20TV=str(tryget3(OutData,Animal,seg,'Sigh2xTV')),
                            Sigh30TV=str(tryget3(OutData,Animal,seg,'Sigh3xTV')),
                            Sigh15PIF=str(tryget3(OutData,Animal,seg,'Sigh1.5xPIF')),
                            Sigh20PIF=str(tryget3(OutData,Animal,seg,'Sigh2xPIF')),
                            Sigh30PIF=str(tryget3(OutData,Animal,seg,'Sigh3xPIF')),
                            Sigh15PEF=str(tryget3(OutData,Animal,seg,'Sigh1.5xPEF')),
                            Sigh20PEF=str(tryget3(OutData,Animal,seg,'Sigh2xPEF')),
                            Sigh30PEF=str(tryget3(OutData,Animal,seg,'Sigh3xPEF')),
                            minPIF=str(AP['minPIF']),
                            minTI=str(AP['minTI']),
                            maxDVTV=str(AP['maxDVTV']),
                            maxPer500=str(AP['maxPer500']),
                            TTwin=str(AP['TTwin']),
                            per500win=str(AP['per500win']),
                            minApTime=str(AP['minApSec']),
                            minApSeg=str(AP['minApsTT']),
                            minAploc=str(AP['minAplTT']),
                            SIGHwin=str(AP['SIGHwin']),
                            Smoothed=str(AP['SmoothFilt']),
                            median_TI=str(tryget3(OutData,Animal,seg,'TI(median)')),
                            median_TE=str(tryget3(OutData,Animal,seg,'TE(median)')),
                            median_TT=str(tryget3(OutData,Animal,seg,'TT(median)')),
                            median_BPM=str(tryget3(OutData,Animal,seg,'BPM(median)')),
                            median_iTV=str(tryget3(OutData,Animal,seg,'iTV(median)')),
                            median_eTV=str(tryget3(OutData,Animal,seg,'eTV(median)')),
                            median_PIF=str(tryget3(OutData,Animal,seg,'PIF(median)')),
                            median_PEF=str(tryget3(OutData,Animal,seg,'PEF(median)')),
                            median_ISTT=str(tryget3(OutData,Animal,seg,'ISTT(median)'))
                            )
                            
                    f.write(outputtext)
        
        f.closed
        
def breathcaller(xParsedData,curFile,AP,xAniFile,xSegFile):
    ##
    outdata={}
    breathlist={}
    ## process data - 1st pass breath calls
    print('grabbing timestamps')
    TS=[float(i) for i in xParsedData[0]['Time'][:]]
    for animalNo in range(1,len(xParsedData)):
        breathlist[animalNo]={}
        # get sampling rate information
        sampleTime=TS[2]-TS[1]
        sampleHz=1/sampleTime
        
        print('grabbing trace data for animal '+str(animalNo))
        ##
        CT=[float(i) for i in xParsedData[animalNo]['Flow']]
        if AP['SmoothFilt']=='y':
            hpf_b,hpf_a=signal.butter(2,0.1/(sampleHz/2),'high')
            hpfCT=signal.filtfilt(hpf_b,hpf_a,CT)

            lpf_b,lpf_a=signal.bessel(10,50/(sampleHz/2),'low')
            lpfhpfCT=signal.filtfilt(lpf_b,lpf_a,hpfCT)
            CT=lpfhpfCT
            
        ## check for threshold crossings
        print('checking for threshhold crossings')
        CT_AT=getabovethresh(CT,0)
        CT_DL=getdifflist(CT_AT)
        print('indexing Start of Ins and Exp')
        CT_IL=getindexlist(CT_DL,[1,-1])
        print('get timestamps for crossings')
        CT_TS=getindexedvals(TS,CT_IL)
        print('calculating durations')
        CT_dur=getdiffbyindex(TS,CT_IL)
        print('extracting Ins and Exp codes "1=Ins Start"')
        CT_IE=getindexedvals(CT_DL,CT_IL)
        print('calculating PIF')
        CT_PIF=getmaxbyindex(CT[1:],CT_IL)
        print('generate breath index')
        CT_BR=[]
        br=0
        for i in CT_IE:
            if i==1:
                br+=1
            CT_BR.append(br)
        if len(CT_BR)<20:
            print('insufficient breaths to score - skip to next animal')
            continue
        print('generate breath filters')
        BR_temp=[0 for i in range(max(CT_BR)+1)]
        BR_TS_TI=list(BR_temp)
        BR_TS_TE=list(BR_temp)
        BR_TI=list(BR_temp)
        BR_PIF=list(BR_temp)
        BR_IL_TI=list(BR_temp)
        BR_IL_TE=list(BR_temp)
        if CT_IE[-1]==1:
            CT_BR=CT_BR[:-1]
        for i in range(len(CT_BR)):
            if CT_IE[i]==1:
                BR_TS_TI[CT_BR[i]]=CT_TS[i]
                BR_IL_TI[CT_BR[i]]=CT_IL[i]
                BR_TI[CT_BR[i]]=CT_dur[i]
                BR_PIF[CT_BR[i]]=CT_PIF[i]
            elif CT_IE[i]==-1:
                BR_TS_TE[CT_BR[i]]=CT_TS[i]
                BR_IL_TE[CT_BR[i]]=CT_IL[i]
            else: print('problem with index {x}'.format(x=i))

        filt_TI=getabovethresh(BR_TI,AP['minTI'])
        filt_PIF=getabovethresh(BR_PIF,AP['minPIF'])
        filt_1stPass=mergelistmin(filt_TI,filt_PIF)
        print('roll failed breaths into prev breath')
        FB_IND=getindexlist(filt_1stPass,[1])
        #%% skip channels with too few breaths (minimum is 20)
        if len(FB_IND)<20:
            print('insufficient breaths to score - skip to next animal')
            continue
        print('breaths found:',len(FB_IND))
        FB_TS_TI=getindexedvals(BR_TS_TI,FB_IND)
        FB_TS_TE=getindexedvals(BR_TS_TE,FB_IND)
        FB_IL_TI=getindexedvals(BR_IL_TI,FB_IND)
        FB_IL_TE=getindexedvals(BR_IL_TE,FB_IND)
        FB_TS_END=FB_TS_TI[1:]
        FB_TS_TI=FB_TS_TI[:-1]
        FB_TS_TE=FB_TS_TE[:-1]
        FB_IL_END=FB_IL_TI[1:]
        FB_IL_TI=FB_IL_TI[:-1]
        FB_IL_TE=FB_IL_TE[:-1]
        print('calculating breath components')
        FB_TI=mergelistsubt(FB_TS_TE,FB_TS_TI)
        FB_TE=mergelistsubt(FB_TS_END,FB_TS_TE)
        FB_TT=mergelistsubt(FB_TS_END,FB_TS_TI)
        FB_ISTT=[0]+[abs(FB_TT[i+1]-FB_TT[i])/FB_TT[i+1] for i in range(len(FB_TT)-1)]
        FB_BPM=[60.0/i for i in FB_TT]
        FB_ISBPM=[0]+[abs(FB_BPM[i+1]-FB_BPM[i])/FB_BPM[i+1] for i in range(len(FB_BPM)-1)]
        # use Area under curve to get TV (multiply by sampleTime to correct for sampling rates)
        FB_iTV=[i*(sampleTime) for i in getsumby2index(CT[1:],FB_IL_TI,FB_IL_TE)]
        FB_eTV=[i*(-1*sampleTime) for i in getsumby2index(CT[1:],FB_IL_TE,FB_IL_END)]
        #
        #(updated to new version below)old dvtv filter ->FB_dVTV=[abs(FB_iTV[i]-FB_eTV[i])/FB_iTV[i] for i in range(len(FB_iTV))]
        FB_dVTV=[abs(FB_iTV[i]-FB_eTV[i])/((FB_iTV[i]+FB_eTV[i])/2) for i in range(len(FB_iTV))]
        FB_PIF=getmaxby2index(CT[1:],FB_IL_TI,FB_IL_TE)
        FB_PEF=[i*(-1) for i in getminby2index(CT[1:],FB_IL_TE,FB_IL_END)]
        ## sliding window calculations
        print('calculating local avgs')
        TTwinHalf=int((AP['TTwin']-1)/2)
        per500winHalf=int((AP['per500win']-1)/2)
        SIGHwinHalf=int((AP['SIGHwin']-1)/2)
        ##
        FB_LOC=[sum(
            FB_TT[max(0,i-TTwinHalf):min(len(FB_TT)-1,i+TTwinHalf)]
            )
            /
            len(FB_TT[max(0,i-TTwinHalf):min(len(FB_TT)-1,i+TTwinHalf)]
                )
                for i in range(len(FB_TT))]
        FB_per500=[(sum(
            [1 if i>500 else 0 for i in FB_BPM[max(0,i-per500winHalf):
                               min(len(FB_BPM)-1,i+per500winHalf)]]
             ))
            /
            len([1 for i in FB_BPM[max(0,i-per500winHalf):
                                   min(len(FB_BPM)-1,i+per500winHalf)]]
                 )
                for i in range(len(FB_BPM))]
        FB_LocTT=[sum(
            FB_TT[max(0,i-SIGHwinHalf):min(len(FB_TT)-1,i+SIGHwinHalf)]
            )
            /
            len(FB_TT[max(0,i-SIGHwinHalf):min(len(FB_TT)-1,i+SIGHwinHalf)]
                )
                for i in range(len(FB_TT))]
        FB_LocTV=[sum(
            FB_iTV[max(0,i-SIGHwinHalf):min(len(FB_iTV)-1,i+SIGHwinHalf)]
            )
            /
            len(FB_iTV[max(0,i-SIGHwinHalf):min(len(FB_iTV)-1,i+SIGHwinHalf)]
                )
                for i in range(len(FB_iTV))]
        FB_LocPIF=[sum(
            FB_PIF[max(0,i-SIGHwinHalf):min(len(FB_PIF)-1,i+SIGHwinHalf)]
            )
            /
            len(FB_PIF[max(0,i-SIGHwinHalf):min(len(FB_PIF)-1,i+SIGHwinHalf)]
                )
                for i in range(len(FB_PIF))]
        FB_LocPEF=[sum(
            FB_PEF[max(0,i-SIGHwinHalf):min(len(FB_PEF)-1,i+SIGHwinHalf)]
            )
            /
            len(FB_PEF[max(0,i-SIGHwinHalf):min(len(FB_PEF)-1,i+SIGHwinHalf)]
                )
                for i in range(len(FB_PEF))]

        ## make filts (dvTV and per500)
        filtDVTV=getbelowthresh(FB_dVTV,AP['maxDVTV'])
        filtper500=getbelowthresh(FB_per500,AP['maxPer500'])
        filtDVTVper500=mergelistmin(filtDVTV,filtper500)
        ## get current animals data
        AniNo=animalNo
        xAniCur={}
        xSegCur={}
        for i in xAniFile:
            xAniCur[i]=[xAniFile[i][j] for j in range(len(xAniFile[i])) if xAniFile['chamber'][j]==str(AniNo)]
        for i in xSegFile:
            xSegCur[i]=[xSegFile[i][j] for j in range(len(xSegFile[i])) if xSegFile['animalcode'][j]==str(AniNo)]
            
        CurAniSegDict=getsegdict(FB_TS_TI,xSegCur,'subsegment')

        ## get seg averages for breath params
        CurAniSegRes={}
        for seg in CurAniSegDict:
            if len(getlistfromfilter(FB_TT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))<20:
                print('insufficient breaths to score - skip to next animal')
                continue
            
            CurAniSegRes[seg]={}
            CurAniSegRes[seg]['N']=len(getlistfromfilter(
                FB_TT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['TI']=getavg(getlistfromfilter(
                FB_TI,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['TE']=getavg(getlistfromfilter(
                FB_TE,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['TT']=getavg(getlistfromfilter(
                FB_TT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['BPM']=getavg(getlistfromfilter(
                FB_BPM,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['ISTT']=getavg(getlistfromfilter(
                FB_ISTT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['ISBPM']=getavg(getlistfromfilter(
                FB_ISBPM,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['iTV']=getavg(getlistfromfilter(
                FB_iTV,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['eTV']=getavg(getlistfromfilter(
                FB_eTV,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['dVTV']=getavg(getlistfromfilter(
                FB_dVTV,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['PIF']=getavg(getlistfromfilter(
                FB_PIF,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['PEF']=getavg(getlistfromfilter(
                FB_PEF,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            
            CurAniSegRes[seg]['TI(median)']=getmed(getlistfromfilter(
                FB_TI,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['TE(median)']=getmed(getlistfromfilter(
                FB_TE,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['TT(median)']=getmed(getlistfromfilter(
                FB_TT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['BPM(median)']=getmed(getlistfromfilter(
                FB_BPM,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['ISTT(median)']=getmed(getlistfromfilter(
                FB_ISTT,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['ISBPM(median)']=getmed(getlistfromfilter(
                FB_ISBPM,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['iTV(median)']=getmed(getlistfromfilter(
                FB_iTV,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['eTV(median)']=getmed(getlistfromfilter(
                FB_eTV,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['PIF(median)']=getmed(getlistfromfilter(
                FB_PIF,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['PEF(median)']=getmed(getlistfromfilter(
                FB_PEF,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            
            CurAniSegRes[seg]['per500']=getavg(getlistfromfilter(
                FB_per500,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
            CurAniSegRes[seg]['LOC']=getavg(getlistfromfilter(
                FB_LOC,mergelistmin(filtDVTVper500,CurAniSegDict[seg]),1))
        ## call apneas
        ApSegFilt={}
        breathlist[animalNo]['segTT']={}
        for seg in CurAniSegRes:
            testTT=CurAniSegRes[seg]['TT']
            breathlist[animalNo]['segTT'][seg]=CurAniSegRes[seg]['TT']
            ApSegFilt[seg]={}
            if testTT=='NAN':
                ApSegFilt[seg]['2x']=[0 for i in FB_TT]
                ApSegFilt[seg]['3x']=[0 for i in FB_TT]
                ApSegFilt[seg]['strict']=[0 for i in FB_TT]
            else:
                ApSegFilt[seg]['2x']=[1 if FB_TT[i]>=testTT*2 else 0 for i in range(len(FB_TT))]
                ApSegFilt[seg]['3x']=[1 if FB_TT[i]>=testTT*3 else 0 for i in range(len(FB_TT))]
                ApSegFilt[seg]['strict']=[1 if FB_TT[i]>=testTT*AP['minApsTT'] else 0 for i in range(len(FB_TT))]

        ApLocFilt={}
        ApLocFilt['2x']=[1 if FB_TT[i]>=FB_LOC[i]*2 else 0 for i in range(len(FB_TT))]
        ApLocFilt['3x']=[1 if FB_TT[i]>=FB_LOC[i]*3 else 0 for i in range(len(FB_TT))]
        ApLocFilt['strict']=[1 if FB_TT[i]>=FB_LOC[i]*AP['minAplTT'] else 0 for i in range(len(FB_TT))]

        ApTimeFilt={}
        ApTimeFilt['05']=[1 if FB_TT[i]>=0.5 else 0 for i in range(len(FB_TT))]
        ApTimeFilt['08']=[1 if FB_TT[i]>=0.8 else 0 for i in range(len(FB_TT))]
        ApTimeFilt['10']=[1 if FB_TT[i]>=1.0 else 0 for i in range(len(FB_TT))]
        ApTimeFilt['strict']=[1 if FB_TT[i]>=AP['minApSec'] else 0 for i in range(len(FB_TT))]

        ## call sighs
        SegLocFilt={}
        SegLocFilt['1.5xTV']=[1 if FB_iTV[i]>FB_LocTV[i]*1.5 else 0 for i in range(len(FB_iTV))]
        SegLocFilt['2xTV']=[1 if FB_iTV[i]>FB_LocTV[i]*2 else 0 for i in range(len(FB_iTV))]
        SegLocFilt['3xTV']=[1 if FB_iTV[i]>FB_LocTV[i]*3 else 0 for i in range(len(FB_iTV))]
        SegLocFilt['1.5xPIF']=[1 if FB_iTV[i]>FB_LocPIF[i]*1.5 else 0 for i in range(len(FB_PIF))]
        SegLocFilt['2xPIF']=[1 if FB_iTV[i]>FB_LocPIF[i]*2 else 0 for i in range(len(FB_PIF))]
        SegLocFilt['3xPIF']=[1 if FB_iTV[i]>FB_LocPIF[i]*3 else 0 for i in range(len(FB_PIF))]
        SegLocFilt['1.5xPEF']=[1 if FB_iTV[i]>FB_LocPEF[i]*1.5 else 0 for i in range(len(FB_PEF))]
        SegLocFilt['2xPEF']=[1 if FB_iTV[i]>FB_LocPEF[i]*2 else 0 for i in range(len(FB_PEF))]
        SegLocFilt['3xPEF']=[1 if FB_iTV[i]>FB_LocPEF[i]*3 else 0 for i in range(len(FB_PEF))]
        
        ## sum apneas
        for seg in CurAniSegRes:
            try:
                N=CurAniSegRes[seg]['N']
                ApStrictFilt=mergelistmin(mergelistmin(
                    ApSegFilt[seg]['strict'],ApLocFilt['strict']),ApTimeFilt['strict'])
                CurAniSegRes[seg]['Ap2s']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApSegFilt[seg]['2x']))/N*10000
                CurAniSegRes[seg]['Ap3s']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApSegFilt[seg]['3x']))/N*10000
                CurAniSegRes[seg]['Ap2l']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApLocFilt['2x']))/N*10000
                CurAniSegRes[seg]['Ap3l']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApLocFilt['3x']))/N*10000
                CurAniSegRes[seg]['Ap05']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApTimeFilt['05']))/N*10000
                CurAniSegRes[seg]['Ap08']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApTimeFilt['08']))/N*10000
                CurAniSegRes[seg]['Ap10']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApTimeFilt['10']))/N*10000
                CurAniSegRes[seg]['ApStrict']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApStrictFilt))/N*10000
                CurAniSegRes[seg]['Sigh1.5xTV']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['1.5xTV']))/N*10000
                CurAniSegRes[seg]['Sigh2xTV']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['2xTV']))/N*10000
                CurAniSegRes[seg]['Sigh3xTV']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['3xTV']))/N*10000
                CurAniSegRes[seg]['Sigh1.5xPIF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['1.5xPIF']))/N*10000
                CurAniSegRes[seg]['Sigh2xPIF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['2xPIF']))/N*10000
                CurAniSegRes[seg]['Sigh3xPIF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['3xPIF']))/N*10000
                CurAniSegRes[seg]['Sigh1.5xPEF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['1.5xPEF']))/N*10000
                CurAniSegRes[seg]['Sigh2xPEF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['2xPEF']))/N*10000
                CurAniSegRes[seg]['Sigh3xPEF']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 SegLocFilt['3xPEF']))/N*10000
                
                CurAniSegRes[seg]['ApN']=sum(mergelistmin(
                    mergelistmin(filtDVTVper500,CurAniSegDict[seg]),
                                 ApStrictFilt))
                CurAniSegRes[seg]['ApStrTT']=getavg(getlistfromfilter(
                    FB_TT,mergelistmin(
                        mergelistmin(
                            filtDVTVper500,CurAniSegDict[seg])
                        ,ApStrictFilt)
                    ,1))
                NonApStrictFilt=[0 if ApStrictFilt[i]==1 else 1 for i in range(len(ApStrictFilt))]
                NonApInSegFilt=mergelistmin(mergelistmin(filtDVTVper500,CurAniSegDict[seg]),NonApStrictFilt)

                CurAniSegRes[seg]['NonApTT']=getavg(getlistfromfilter(
                    FB_TT,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApTI']=getavg(getlistfromfilter(
                    FB_TI,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApTE']=getavg(getlistfromfilter(
                    FB_TE,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApBPM']=getavg(getlistfromfilter(
                    FB_BPM,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApiTV']=getavg(getlistfromfilter(
                    FB_iTV,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApPIF']=getavg(getlistfromfilter(
                    FB_PIF,NonApInSegFilt,1))
                CurAniSegRes[seg]['NonApN']=sum(NonApInSegFilt)
                print('apneas called for '+seg)
            except:
                print('problem with '+seg)
        outdata[animalNo]=CurAniSegRes
        breathlist[animalNo]['BL']={'TS_TI':FB_TS_TI,'TS_TE':FB_TS_TE,'iTV':FB_iTV,
                                    'PIF':FB_PIF,'PEF':FB_PEF,
                                    'ApLocTT':FB_LOC,'SighLocTT':FB_LocTT,
                                    'SighLocTV':FB_LocTV, 'SighLocPIF':FB_LocPIF,
                                    'SighLocPEF':FB_LocPEF,'SEG':CurAniSegDict,
                                    'DVTV':FB_dVTV,'per500':FB_per500,'AP':AP}
      
    return outdata,breathlist

    
#%%# main
def main():
    try:
        #%%#
        # set parameters
        AnalysisParameters={}
        AnalysisParameters['minTI']=wardcode.getFloat('minimum TI for breath calling [recommend 0.025]')
        AnalysisParameters['minPIF']=wardcode.getFloat('minimum PIF for breath calling [recommend 0.05]')
        AnalysisParameters['TTwin']=wardcode.getInt('window size for calculating local TT during apnea detection [recommend 7]')
        AnalysisParameters['per500win']=wardcode.getInt('window size for per500 filter [recommend 201]')
        AnalysisParameters['maxPer500']=wardcode.getFloat('per500 filter level [recommend *1.0* for no filtering, 0.1 for strict filtering]')
        AnalysisParameters['maxDVTV']=wardcode.getFloat('inhaled vs exhaled tidal volume filter [recommend *100* for no filtering, 0.5 for moderate filtering')
        AnalysisParameters['minApSec']=wardcode.getFloat('minimum breath duration (seconds) for apnea detection [recommend 0.5]')
        AnalysisParameters['minApsTT']=wardcode.getFloat('minimum breath duration relative to local average for apnea detection [recommend 2]')
        AnalysisParameters['minAplTT']=wardcode.getFloat('minimum breath duration relative to overall average for apnea detection [recommend 2]')
        AnalysisParameters['SIGHwin']=wardcode.getInt('window size for sigh detection [recommend 11]')
        AnalysisParameters['SmoothFilt']=wardcode.getYN('use high-pass filter [0.1Hz] and low-pass [50Hz] Y or N')
        # get input files
    
        ##
        # get data
        xFilePathList=wardcode.guiOpenFileNames({'title':'Load Ascii Files With Trace Data','filetypes':[('ascii','.ascii'),
                      ('all files','.*')]})
        ##
        AL_FilePath=wardcode.guiOpenFileName({'title':'Load Text File With Animal Data','filetypes':[('animal list','.al'),('all files','.*')]})
        SL_FilePath=wardcode.guiOpenFileName({'title':'Load Text File With Segment Data','filetypes':[('segments','.seg'),('all files','.*')]})
        OutputFilename=wardcode.guiSaveFileName({'title':'Choose Filename for Output Data'})
        ##
        OutputData={}
        breathlist={}
        ##
        
        # get animal and segment lists
        xAniData=wardcode.dataDictUnfold(
            wardcode.dataParseTabDelToColumns(
                [i.lower() for i in wardcode.dataGrab(AL_FilePath)],0
                )
            )
        xSegData=wardcode.dataDictUnfold(
            wardcode.dataParseTabDelToColumns(
                [i.lower() for i in wardcode.dataGrab(SL_FilePath)],0
                )
            )
        xFileData={}
        ##
        print('Checking for headerlines...')
        for xFilePath in xFilePathList:
            xFileData[xFilePath.lower()]=wardcode.dataFindHeaderByText([i.lower() for i in wardcode.dataGrab(xFilePath)],['time','flow'])
            print(str(xFileData[xFilePath.lower()])+' : '+os.path.basename(xFilePath))
    
                
        #%%#
        for xFilePath in xFileData:
            ##
            CurFile=os.path.basename(xFilePath)
            print('opening file '+CurFile)
            AsciiData=wardcode.dataGrab(xFilePath)
            print('parsing data')
            xPD=wardcode.dataParseTextToColumns(AsciiData,int(xFileData[xFilePath]))
            
            xAniFile={}
            xSegFile={}
            for i in xAniData:
                xAniFile[i]=[xAniData[i][j] for j in range(len(xAniData[i])) if xAniData['filename'][j].lower()==CurFile[:-6]]
    
            for i in xSegData:
                xSegFile[i]=[xSegData[i][j] for j in range(len(xSegData[i])) if xSegData['asciifile'][j].lower()==CurFile[:-6]]
    
            #%%# run breathcaller
            OutputData[CurFile],breathlist[CurFile]=breathcaller(xPD,CurFile,AnalysisParameters,xAniFile,xSegFile)
            print('Saving Python BreathList')
            with open(os.path.dirname(OutputFilename)+'/'+CurFile+'_breathlist.js','w') as f:
                json.dump({CurFile:breathlist[CurFile]},f)
            f.closed
            del breathlist[CurFile]
        ##
        print('Creating Data Output')
        plethdatawriter(OutputData,OutputFilename,AnalysisParameters,xAniData,xSegData)
        print('All Done')
    except:
        print('Script Unable to continue - unknown ERROR during runtime')
        input('press enter to exit')
#%%#

if __name__=="__main__":
    main()
    input('Finished...PRESS ENTER TO CLOSE')
