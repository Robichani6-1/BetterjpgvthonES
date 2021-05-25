#!/usr/bin/python

import struct
import os
import sys
import subprocess
import shlex
import glob
import shutil
import time

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

# Program syntax:

# "vid2jpgv" by itself will start interactive mode.
# "vid2jpgv inputfile outputfile fps width height scaling quality channels samplerate codec" will run in non-interactive mode.
# 
# inputfile - Input filename
# outputfile - outputfile filename
# fps - Framerate.
# channels - Number of audio channels.
# width height - Desired (not source!) width and height in pixels. 400x240 is a safe default and will be suggested as default in interactive mode.
# scaling - Scaling type. 1 for stretching, 2 for scale-and-pad. 
# samplerate - Audio samplerate. 44100 is a safe default and will be suggested as default in interactive mode.
# codec - Desired (not source!) audio codec. 1 or 2, 1 being PCM16, 2 being Vorbis. 
# quality - High or low quality, 1 for HQ, 2 for LQ.
#
# Optionally, you may put "quiet" at the end of a non-interactive mode line for no output whatsoever.
#

# FFMpeg scale-and-pad algo by slhck from superuser.com

# Scaling filter line:
# -filter:v "scale=iw*min($width/iw\,$height/ih):ih*min($width/iw\,$height/ih), pad=$width:$height:($width-iw*min($width/iw\,$height/ih))/2:($height-ih*min($width/iw\,$height/ih))/2, transpose=1"
# Stretching filter line:
# -vf "transpose=1" -s $heightx$width

def interactive():
    retdict = {}
    print("Codificador de videos para 3Ds, traducido y reducido por Robichani6")
    print("-------------------------------------------------------------------")
    try:
        print()
        print("--------")
        print("Archivos")
        print("--------")
        print()
        ifile = ""
        while (ifile == ""):
            ifile = input("Nombre del archivo (EJ: ejemplo.mp4): ")
            if not os.path.isfile(ifile):
                print("Error: El archivo no está en el directorio.")
                ifile = ""
        ofile = ""
        while (ofile == ""):
            ofile = input("Nombre del archivo codificado (EJ: estoycodificado.jpgv): ")
            if ofile.split(".")[-1] != "jpgv":
                print("Error: El archivo tiene que acabar en .jpgv")
                ofile = ""
        print()
        print("-----")
        print("VIDEO")
        print("-----")
        print()
        fps = 30
        width = 400
        height = 240
        scalemode = 1
        quality = 1
        print()
        print("-----")
        print("AUDIO")
        print("-----")
        print()
        channels = 2
        samplerate = 1
        codec = 2
    except EOFError:
        print("Interactive mode ended prematurely by user.")
        sys.exit(1)
    except:
        print("Interactive mode encountered unknown error. Re-raising.")
        raise
    retdict = {"ifile": ifile, "ofile": ofile, "fps": fps, "width": width, "height": height, "scalemode": scalemode, "quality": quality, "channels": channels, "samplerate": samplerate, "codec": codec}
    return retdict
    
# "vid2jpgv inputfile outputfile fps width height scaling quality channels samplerate codec" will run in non-interactive mode.    
def argvparse(paramlist):
    retdict = {}
    retdict['ifile'] = paramlist[1]
    retdict['ofile'] = paramlist[2]
    retdict['fps'] = paramlist[3]
    retdict['width'] = paramlist[4]
    retdict['height'] = paramlist[5]
    retdict['scalemode'] = paramlist[6]
    retdict['quality'] = paramlist[7]
    retdict['channels'] = paramlist[8]
    retdict['samplerate'] = paramlist[9]
    retdict['codec'] = paramlist[10]
    if not os.path.isfile(retdict['ifile']):
        raise FileNotFoundError("Input file not found.")
    if retdict['ofile'].split(".")[-1] != "jpgv":
        raise ValueError("output filename doesn't end in .jpgv")
    if not retdict['fps'].isdigit():
        raise TypeError("FPS must be numeric.")
    else:
        retdict['fps'] = int(retdict['fps'])
    if not retdict['width'].isdigit():
        raise TypeError("Width and Height must be numeric.")
    else:
        retdict['width'] = int(retdict['width'])
    if not retdict['height'].isdigit():
        raise TypeError("Width and Height must be numeric.")
    else:
        retdict['height'] = int(retdict['height'])
    if ((retdict['scalemode'] != "1") and (retdict['scalemode'] != "2")):
        raise ValueError("Scaling value must be either 1 or 2.")
    else:
        retdict['scalemode'] = int(retdict['scalemode'])
    if ((retdict['quality'] != "1") and (retdict['quality'] != "2")):
        raise ValueError("Quality value must be either 1 or 2.")
    else:
        retdict['quality'] = int(retdict['quality'])
    if not retdict['channels'].isdigit():
        raise TypeError("Channels must be numeric.")
    else:
        retdict['channels'] = int(retdict['channels'])
    if not retdict['samplerate'].isdigit():
        raise TypeError("Samplerate must be numeric, got " + retdict['samplerate'])
    else:
        retdict['samplerate'] = int(retdict['samplerate'])
    if ((retdict['codec'] != "1") and (retdict['codec'] != "2")):
        raise ValueError("Quality value must be either 1 or 2.")
    else:
        retdict['codec'] = int(retdict['codec'])
    return retdict

def speak(str = ""):
    if quiet == 1:
        return
    elif str == "":
        print()
        return
    else:
        print(str)
        return
        
if not os.path.isdir("temp"):
    if os.path.exists("temp"):
        os.remove("temp")
        os.mkdir("temp")
    else:
        os.mkdir("temp")
        
quiet = 0
if len(sys.argv) == 11: # Non-interactive mode.
    params = argvparse(sys.argv)
elif (len(sys.argv) == 12) and (sys.argv[-1] == "quiet"): # Non-interactive quiet mode. Let's bury our heads in the sand!
    params = argvparse(sys.argv)
    quiet = 1
else: # Interactive mode
    params = interactive()

if params['scalemode'] == 1:
    scaleline = '-vf "transpose=1" -s ' + str(params['height']) + 'x' + str(params['width'])
else:
    scaleline = '-filter:v "scale=iw*min(' + str(params['width']) + '/iw\,' + str(params['height']) + '/ih):ih*min(' + str(params['width']) + '/iw\,' + str(params['height']) + '/ih), pad=' + str(params['width']) + ':' + str(params['height']) + ':(' + str(params['width']) + '-iw*min(' + str(params['width']) + '/iw\,' + str(params['height']) + '/ih))/2:(' + str(params['height']) + '-ih*min(' + str(params['width']) + '/iw\,' + str(params['height']) + '/ih))/2, transpose=1"'
if params['quality'] == 1:
    qualline = '-qscale:v 2'
else:
    qualline = ""

ffmpegcommand = 'ffmpeg -i ' + params['ifile'] + ' -r ' + str(params['fps']) + ' ' + qualline + ' ' + scaleline + ' "temp\\output%1d.jpg"'
try:
    if quiet == 1:
        subprocess.check_call(shlex.split(ffmpegcommand), stdout=DEVNULL, stderr=subprocess.STDOUT)
    else: 
        subprocess.check_call(shlex.split(ffmpegcommand))
except subprocess.CalledProcessError:
    sys.exit(1)


if params['codec'] == 1:
    ffmpegcommand = 'ffmpeg -i ' + params['ifile'] + ' -acodec pcm_s16le -ac ' + str(params['channels']) + ' -ar ' + str(params['samplerate']) + ' "temp\\audio.wav"'
else:
    ffmpegcommand = 'ffmpeg -i ' + params['ifile'] + ' -acodec: libvorbis -ac ' + str(params['channels']) + ' -ar ' + str(params['samplerate']) + ' -vn "temp\\audio.ogg"'
try:
    if quiet == 1:
        subprocess.check_call(shlex.split(ffmpegcommand), stdout=DEVNULL, stderr=subprocess.STDOUT)
    else: 
        subprocess.check_call(shlex.split(ffmpegcommand))
except subprocess.CalledProcessError:
    sys.exit(1)

# Now for the hard part...

# First, we read in the audio files so we can set some header values.

if params['codec'] == 1:
    headercodec = 0
    # Read WAV headers, parse into JPGV header.
    wavfile = open("temp/audio.wav", 'rb')
    wavfile.seek(22)
    audiotype = wavfile.read(2)
    audiotype = struct.unpack('<H',audiotype)
    audiotype = audiotype[0]
    samplerate = wavfile.read(2)
    samplerate = struct.unpack('<H',samplerate)
    samplerate = samplerate[0]
    wavfile.seek(32)
    bytespersample = wavfile.read(2)
    bytespersample = struct.unpack('<H',bytespersample)
    bytespersample = bytespersample[0]
    wavfile.seek(16)
    chunk = 0
    jump = 0
    while chunk != 0x61746164:
        jump = wavfile.read(4)
        if len(jump) < 4:
            sys.exit(1)
        jump = struct.unpack('<L',jump)
        wavfile.seek(jump[0], 1)
        chunk = wavfile.read(4)
        if len(chunk) < 4:
            sys.exit(1)
        chunk = struct.unpack('<L',chunk)
        chunk = chunk[0]
    wavdata_start = wavfile.tell() + 4 # Oops, forgot this bit the first time!
    wavfile.seek(0, 2)
    size = wavfile.tell()
    wavdata_size = size - wavdata_start
    # Read WAV data into a buffer.
    wavfile.seek(wavdata_start)
    audiosize = wavdata_size
    audiodata = wavfile.read(wavdata_size)
    if len(audiodata) != wavdata_size:
        sys.exit(1)
    wavfile.close()
else:
    # JPGV OGG header is simple, just put in some zeroes
    headercodec = 1
    audiotype = 0
    samplerate = 0
    bytespersample = 0
    oggfile = open("temp/audio.ogg", 'rb')
    oggfile.seek(0, 2)
    audiosize = oggfile.tell()
    oggfile.seek(0)
    audiodata = oggfile.read(audiosize)
    if len(audiodata) != audiosize:
        sys.exit(1)
    oggfile.close()


if audiosize == 0:
    sys.exit(1)

if len(audiodata) == 0:
    sys.exit(1)
    
if audiosize != len(audiodata):
    sys.exit(1)

# Grab number of frames

dirlist = glob.glob('temp/*.jpg')
numframes = len(dirlist)

# JPGV format details

# 24 byte header

# All values are little-endian
# 0x00 String "JPGV"
# 0x04 4-byte integer (Is that really necessary? One byte would do...) Framerate
# 0x08 2-byte WAV audiotype
# 0x0A 2-byte WAV bytes-per-sample
# 0x0C 2-byte WAV samplerate
# 0x0E 2-byte (For a boolean? WHY?) codec. 0 for WAV, 1 for OGG. If OGG, 0x8, 0xA, 0xC should be 0.
# 0x10 4-byte number of frames.
# 0x14 4-byte size of audio stream in bytes.

# Directly following the header is either the OGG file, or the data chunk from the WAV file, in its entirety.

# Directly following that is an 8*number-of-frames sized section containing 64-bit offsets for the start of each JPEG, however these offsets do not
# include the size of this section, so 8*number-of-frames needs to be added to these offsets to get the correct starting point.
# Couldn't you just have the player automatically find the next frame whenever it encounters 0xFFD8FFE0 (JPEG header)?

# Directly following this is all the JPEG files in sequence.

# Writing the header.
outputfile = open(params['ofile'], 'wb')
outputfile.write(b'JPGV')
outputfile.write(struct.pack('<L', params['fps']))
outputfile.write(struct.pack('<H', audiotype))
outputfile.write(struct.pack('<H', bytespersample))
outputfile.write(struct.pack('<H', samplerate))
outputfile.write(struct.pack('<H', headercodec))
outputfile.write(struct.pack('<L', numframes))
outputfile.write(struct.pack('<L', audiosize))

# Writing the audiodata
outputfile.write(audiodata)

# Writing the offsets.
offset = audiosize + 24
for i in range(1, numframes+1):
    if os.path.isfile("temp/output" + str(i) + ".jpg"):
        offset64 = struct.pack('<Q', offset)
        outputfile.write(offset64)
        framesize = os.path.getsize("temp/output" + str(i) + ".jpg")
        offset = offset + framesize
    else:
        sys.exit(1)

# Writing the frames
for i in range(1, numframes+1):
    try:
        frame = open("temp/output" + str(i) + ".jpg", "rb")
        framebuffer = frame.read()
        outputfile.write(framebuffer)
        frame.close()
    except (IOError, OSError) as e:
        sys.exit(1)

# And we're done!
outputfile.close()
# Was having some weird "File in use" shit going on here, so this is a bit messy, but it generally ends with temp cleared out.
try:
    shutil.rmtree("temp")
except PermissionError:
    time.sleep(1)
    try:
        shutil.rmtree("temp")
    except PermissionError:
        # At this point there shouldn't be anything left anyway, and if there is oh well.
        pass
if not os.path.isdir("temp"):
    if os.path.exists("temp"):
        os.remove("temp")
    os.mkdir("temp")
