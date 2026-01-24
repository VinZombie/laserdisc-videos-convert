#! /usr/bin/env python3
# -*- coding: ISO-8859-1 -*-


## VinceIsZombie (2026)
## Python script for convert Daphne videos (m2v) to .ogv format (and MJPEG format, for purpose of test)
## To get full log on console, set "easy_readable = False"
########################

easy_readable = True

import os, sys, shutil, time, math
from pathlib import Path
if easy_readable:
    from subprocess import Popen, PIPE, STDOUT
else:
    import subprocess

fullTime = 0
startTime = 0

def main(argv):
    warningList = []
    print(" ")
    global startTime
    pythonScriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    resultPath = Path(pythonScriptDir).joinpath("RESULT")
    tmpPath = Path(pythonScriptDir).joinpath("RESULT/tmp")
    if not resultPath.exists():
        os.mkdir(resultPath)
    if tmpPath.exists():
        shutil.rmtree(tmpPath)
    if not tmpPath.exists():
        os.mkdir(tmpPath)
    ## Set encoding binaries path
    ffmpegBin = "ffmpeg"
    mencoderBin = "mencoder"
    if os.name == 'nt':
        ffmpegBin = Path(pythonScriptDir + "/ffmpeg/bin/ffmpeg.exe")
        mencoderBin = Path(pythonScriptDir + "/mplayer/mencoder.exe")
        
    ## Get source folder (containing m2v, ogg and framefile txt)
    ## And verify its content
    sourceFramefile = None
    if len(argv) > 1:
        if argv[1] != None:
            sourceFramefile = argv[1]
    else:
        print("Usage : python Convert.py [Path to framefile.txt]")
        sys.exit(" ")
    exists = False
    if sourceFramefile != None:
        if os.path.exists(sourceFramefile):
            if os.path.isfile(sourceFramefile):
                _, ext = os.path.splitext(sourceFramefile)
                if ext == ".txt":
                    exists = True 
    mediasList = []
    if not exists:
        sys.exit("Error : The given framefile does not exists. Can not continue.")
    else:
        ## Try to iterate through framefile and get videos path list
        p = Path(sourceFramefile)
        sourceFramefilePath = p.parents[0]
        framefile = open(sourceFramefile)
        framefileContent = framefile.read()
        framefile:close()
        number = 0
        mediasPath = ""
        languages = []
        for line in framefileContent.splitlines():
            lineParts = line.split()
            if len(lineParts) != 0:
                if number == 0:
                    mediasPath = sourceFramefilePath.joinpath(lineParts[0])
                    ## Detect multiple languages
                    for file in mediasPath.iterdir():
                        langParts = file.stem.split("_")
                        if len(langParts) > 1:
                            found = False
                            lineNumber = 0
                            for line2 in framefileContent.splitlines():
                                line2Parts = line2.split()
                                if len(line2Parts) != 0:
                                    if lineNumber != 0:
                                        if line2Parts[1] == file.stem + ".m2v":
                                            found = True
                                            break
                                lineNumber += 1
                            if not found:
                                if len(langParts[1].split(".")) == 1:
                                    foundLang = False
                                    for l in languages:
                                        if l == langParts[1].lower():
                                            foundLang = True
                                    if not foundLang:
                                        languages.append(langParts[1].lower())
                elif len(lineParts) == 2:
                    found = False
                    videoFilePath = mediasPath.joinpath(lineParts[1]).resolve()
                    if videoFilePath.exists():
                        for l in mediasList:
                            if l[0] == videoFilePath:
                                found = True
                        p = Path(lineParts[1])
                        audioFilePath = mediasPath.joinpath(p.with_suffix('.ogg')).resolve()
                        addAudio = False
                        if audioFilePath.exists():
                            addAudio = True
                        else:
                            if not found:
                                warningList.append("Warning : Audio file listed in framefile not exist (" + str(p.with_suffix('.ogg')) + "). Some parts of the video will not have sound.")
                        if not found:
                            m = [videoFilePath, None]
                            if addAudio:
                                m[1] = [audioFilePath]
                                for l in languages:
                                    if mediasPath.joinpath(str(Path(audioFilePath.stem)) + "_" + l + ".ogg").resolve().exists():
                                        m[1].append(mediasPath.joinpath(str(Path(audioFilePath.stem)) + "_" + l + ".ogg").resolve())
                            mediasList.append(m)
                    else:
                        sys.exit("Error : One video file listed in framefile does not exist (" + lineParts[1] + "). Can not continue")
                number += 1
        
        
        choice, langIndex = userInput(languages)
        if choice == "1":
            sys.exit(" ")
        print("")
        for w in (warningList):
            print(w)
        startTime = time.time()
        ## Merge audio(s) and video(s) files to a .mp4 file
        i = 0
        for m in (mediasList):
            ## FOR DEBUGGING
            #if i > 2:
            #    break
            i += 1
            videoFile = m[0].resolve()
            resultVideoPath = Path("RESULT/tmp/" + (Path(videoFile).stem + ".mp4")).resolve()            
            if len(mediasList) == 1:
                resultVideoPath = Path("RESULT/tmp/" + (Path(sourceFramefile).stem + "_temp.mp4")).resolve()
            else:
                videoName = Path(videoFile).stem + ".mp4"
                videoListPath = Path("RESULT/tmp/video_list.txt").resolve()
                with open(str(videoListPath), "a") as f:
                    f.write("file '" + str(videoName) + "'\n")
            if m[1] == None:
                if len(mediasList) == 1:
                    sys.exit("Error : Missing audio file for " + str(Path(videoFile).name) + " video file. Audio will not have sound. Can not continue.")
                else:
                    cmdline = [str(ffmpegBin), "-y", "-i", str(videoFile), "-f", "lavfi", "-i", "anullsrc", "-c:v", "libx264", "-preset", "veryslow", "-crf", "0", "-c:a", "libvorbis", "-shortest", "-filter:v", "fps=23.98", str(resultVideoPath)]                    
            else:
                audioFile = m[1][langIndex].resolve()
                cmdline = [str(ffmpegBin), "-y", "-i", str(videoFile), "-i", str(audioFile), "-c:v", "libx264", "-preset", "veryslow", "-crf", "0", "-c:a", "libvorbis", "-shortest", "-filter:v", "fps=23.98", str(resultVideoPath)]
            run_ffmpeg(cmdline, "Combine video and audio for " + str(Path(videoFile).stem) + " (" + str(i) + "/" + str(len(mediasList)) + ")")
            
        concatVideoPath = Path("RESULT/tmp/" + (Path(sourceFramefile).stem + "_temp.mp4")).resolve()
        if len(mediasList) != 1:            
            videoListPath = Path("RESULT/tmp/video_list.txt").resolve()
            cmdline = [str(ffmpegBin), "-y", "-f", "concat", "-i", str(videoListPath), "-crf", "0", str(concatVideoPath)]
            print("")
            run_ffmpeg(cmdline, "Concatenate all video parts to " + str(concatVideoPath.name))
        if choice == "3" or choice == "4":
            oggPath = Path("RESULT/" + (Path(sourceFramefile).stem + ".ogg")).resolve()
            cmdline = [str(ffmpegBin), "-y", "-i", str(concatVideoPath), "-map", "0:a", str(oggPath)]
            print("")
            run_ffmpeg(cmdline, "Extract full audio to " + str(oggPath.name))
            aviPath = Path("RESULT/" + (Path(sourceFramefile).stem + ".avi")).resolve()
            cmdline = [str(mencoderBin), str(concatVideoPath), "-o", str(aviPath), "-ovc", "lavc", "-lavcopts", "vcodec=mjpeg", "-nosound"]
            print("")
            run_mencoder(cmdline, "Convert to silent MJPEG video " + str(aviPath.name))
        if choice == "2" or choice == "4":
            ogvPath = Path("RESULT/" + (Path(sourceFramefile).stem + ".ogv")).resolve()
            cmdline = [str(ffmpegBin), "-y", "-i", str(concatVideoPath), "-c:v", "libtheora", "-q:v", "10", "-c:a", "libvorbis", "-q:a", "-1", str(ogvPath)]
            print("")
            run_ffmpeg(cmdline, "Finally convert to " + str(ogvPath.name))
        
        shutil.rmtree(tmpPath)
    logPath = os.path.dirname(os.path.realpath(sys.argv[0])) + "/convert.log"
    os.remove(logPath)
    print("")
    print("")
    print("Good. Get your media(s) under \"RESULT\" folder.")
    print("(Done in " + readableTime() + ")")
    print(" ")
            
    
def run_ffmpeg(cmdline, title):
    global fullTime
    if not easy_readable:
        subprocess.run(cmdline)
    else:
        print("")
        print(title)
        logPath = os.path.dirname(os.path.realpath(sys.argv[0])) + "/convert.log"
        process = Popen(cmdline, stdout=PIPE, stderr=STDOUT, encoding='utf-8', errors='replace')
        if os.path.exists(logPath):
            os.remove(logPath)
        log = open(logPath, "a")
        duration = 0
        print("\r[" + (" " * 50) + "] " + "0%          ", end='', flush=True)
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                line = realtime_output.strip()
                if line[:9] == "Duration:":
                    if line[10:13] != "N/A":
                        duration = toMs(line[10:21])
                        fullTime += duration
                if line[:6] == "frame=":
                    lineParts = line.split()
                    done = False
                    time = 0
                    i = 0
                    while not done:
                        if i >= len(lineParts):
                           break
                        if lineParts[i][:5] == "time=":
                            time = toMs(lineParts[i][5:16])
                            done = True
                        i += 1
                    if time != None:
                        if duration == 0:
                            duration = fullTime
                        percent = 0
                        if duration != 0:
                            percent = (time * 100) / duration
                        past = "*" * int(percent / 2)
                        left = " " * (50 - int(percent / 2))
                        if duration != 0:
                            print("\r[" + past + left + "] " + str(int(percent)) + "%          ", end='', flush=True)
                        else:
                            print("\r[" + past + left + "] N/A          ", end='', flush=True)
                log.write(line + "\n")
        log.close()
        print("\r[" + ("*" * 50) + "] " + "100%          ", end='', flush=True)
        
   
def run_mencoder(cmdline, title):
    if not easy_readable:
        subprocess.run(cmdline)
    else:
        print("")
        print(title)
        logPath = os.path.dirname(os.path.realpath(sys.argv[0])) + "/convert.log"
        process = Popen(cmdline, stdout=PIPE, stderr=STDOUT, encoding='utf-8', errors='replace')
        if os.path.exists(logPath):
            os.remove(logPath)
        log = open(logPath, "a")
        print("\r[" + (" " * 50) + "] " + "100%          ", end='', flush=True)
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                line = realtime_output.strip()
                if line[:4] == "Pos:":
                    lineParts = line.split()
                    done = False
                    percent = 0
                    i = 0
                    while not done:
                        if i >= len(lineParts):
                           break
                        if len(lineParts[i].split("%)")) > 1:
                            percent = lineParts[i][:1]
                            if percent[:1] == "(":
                                percent = lineParts[i][1:3]
                            percent = int(percent)
                        i += 1
                    past = "*" * int(percent / 2)
                    left = " " * (50 - int(percent / 2))
                    print("\r[" + past + left + "] " + str(int(percent)) + "%          ", end='', flush=True)
                log.write(line + "\n")
        log.close()
        print("\r[" + ("*" * 50) + "] " + "100%          ", end='', flush=True)
 

def userInput(l):    
    result = None
    langNumber = 0
    err = True
    while err:
        cls()
        print(" ")
        print("        Convert Laser-Disc videos")
        print("        -------------------------")
        print(" ")
        print("1. Exit")
        print("2. OGV (DirkSimple)")
        print("3. MJPEG (AVI and OGG, for future application)")
        print("4. Both")
        print(" ")
        number = input("What format do you want to convert your Laser-Disc video ? ")
        try:
            if int(number) > 0 and int(number) < 5:
                result = number
                if len(l) == 0:
                    err = False  
                if int(number) == 1:
                    print(" ")
                    print("Exiting program...")
                    err = False
        except:
            pass
        if len(l) > 0 and number != "1":
            print(" ")
            i = 0
            print("1. Back")
            print("2. Initial language")
            for v in (l):
                print(str(i + 3) + ". \"" + v + "\" language")
                i += 1            
            print(" ")
            langNumber = input("Multiple languages detected. Wich one do you choose ? ")
            try:
                if int(langNumber) > 0 and int(langNumber) < len(l) + 4:
                    langNumber = int(langNumber)
                    if langNumber == 2:
                        langNumber = 0
                        err = False  
                    elif langNumber > 2:
                        langNumber = langNumber - 2
                        err = False 
            except:
                pass
    return number, langNumber
  

def readableTime():
    global startTime
    text = ""
    seconds = time.time() - startTime
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds - (3600 * hours)) / 60)
    if hours > 0:
        if hours == 1:
            text = "1 hour "
        text = str(hours) + " hours "
    if minutes != 0:
        if minutes > 1:
            text = text + str(minutes) + " minutes"
        else:
            text = "1 minute"
    return text
 
def toMs(timeStr):
    time = None
    if timeStr != "N/A":
        timeParts = timeStr.split(":")
        msParts = timeParts[2].split(".")
        time = (((int(timeParts[0]) * 3600) + (int(timeParts[1]) * 60) + int(msParts[0])) * 100) + int(msParts[1])
    return time
    
    
def cls():
    os.system('cls' if os.name=='nt' else 'clear')
    
    
if __name__ == '__main__':
    main(sys.argv)
