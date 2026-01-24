# Laser-Disc video concatenation and conversion
Python script that automate Laser-Disc video games conversion. (Useful to use Dirk Simple)

Convert your .m2v separate files on video games like "Dragon's Lair", "Cliffhanger", and convert them to .ogv as needed by "Dirk Simple".
[Dirk Simple on Github](https://github.com/icculus/DirkSimple)

Usage :
```
python Convert.py Path/to/framefile.txt
```

You can set
```
easy_readable = False
```
at the beginning of the script to see orignal FFMPEG and Mencoder outputs.

# On Linux
Install dependencies : Python3, FFMPEG, Mencoder. For Debian :
```
sudo apt install python3 ffmpeg mencoder
```

# On Windows
Install [Python 3](https://www.python.org/).

Unzip FFMPEG in root folder of the convert script (ROOT\ffmpeg\bin\ffmpeg.exe), or add executable to path. [FFMPEG](https://www.ffmpeg.org/download.html)

Unzip MPlayer in root folder of the convert script (ROOT\mplayer\mencoder.exe), or add mencoder executable to path. [MPlayer](https://oss.netfarm.it/mplayer/)


# MJPEG conversion (.avi, .ogg)
I have added MJPEG conversion cause I test to code a similar program that analyse MJPEG. Choose the right option to use with Dirk Simple.

# Language
Some of the Laser-Disc games are dubbed in Spanish. For some files you can choose the language, but it is merge in the final video. (You cannot choose language in Dirk Simple, for now)
