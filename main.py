# Brian Mc Collum
import os
import midi
from midiObj import MidiEvent

# Loads the midi into lists using "python-midi" library.
# Using this branch for python3 (https://github.com/sniperwrb/python-midi)
# I included 3 different midi files, I found that this thrid oen worked the best
pattern = midi.read_midifile("rickroll3.mid")

# grabs meta data from song to find Ticks per Beat, Time Signature, BPM, and Microseconds Per Beat.
# THIS WILL CHANGE DEPENDING ON WHAT LIBRARY YOU USE (you basically have a choice between this and the mido library for python)
meta = {}
try:
    meta["TPB"] = pattern.resolution
    for track in pattern:
        for x in track:
            if x.name.lower() == "time signature":
                meta["timeSig"] = f"{x.numerator}/{x.denominator}"
            elif x.name.lower() == "set tempo":
                # I manually set the bpm here because I wanted the song to play faster.
                # (plus all the numbers look alot nicer with 120 bpm)
                meta["BPM"] = 120
                # meta["BPM"] = 114
    meta["MSPB"] = 60 * 1000000 / meta["BPM"]
except KeyError:
    print("KeyError")


# Loads all the midi events from each track into lists (without functions xD).
# I made my own midiEvent obj because my brain just couldn't work without it lol.
# no practical way to do this with out human intervention due to the looseness of midi track naming, you are going to need
# to open the midi file in some sort of program (i used musescore) and find the names of each track you want to convert.
drums = []
drums2 = []
piano = []
strings = []
brass = []
sax = []
for track in pattern:
    try:
        if "bongos" in track[0].text.lower():
            for x in track:
                # The way i scraped events was if it had the midi event was "Note On" to pass args to fill out the whole midiEventObj.
                if x.name == "Note On":
                    drums.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    # Otherwise I just saved the ticks inbetween events as objects without velocity or pitch.
                    drums.append(MidiEvent(x.name, x.tick))
        if "drums" in track[0].text.lower():
            for x in track:
                if x.name == "Note On":
                    drums2.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    drums2.append(MidiEvent(x.name, x.tick))
        elif "rhodes" in track[0].text.lower():
            for x in track:
                if x.name == "Note On":
                    piano.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    piano.append(MidiEvent(x.name, x.tick))
        elif "strings" in track[0].text.lower():
            for x in track:
                if x.name == "Note On":
                    strings.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    strings.append(MidiEvent(x.name, x.tick))
        elif "brass" in track[0].text.lower():
            for x in track:
                if x.name == "Note On":
                    brass.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    brass.append(MidiEvent(x.name, x.tick))
        elif "sax" in track[0].text.lower():
            for x in track:
                if x.name == "Note On":
                    sax.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                else:
                    sax.append(MidiEvent(x.name, x.tick))
    except AttributeError:
        print("Skipped track")

# Opens the lists and scrapes the data needed (again without functions...),
# saves these to lua files that can play the individual parts
# In the future im going to beable to read the drum part and read pitches to
# determine which ones are hats, snares, and kicks like how midi programs do.

# Converting from midi notes to minecraft pitches is very easy, F#1 starts on pitch 30 (under 30 is more meta data I think).
# I cheated a little and manually found the octive ranges that the blocks are in.
# You can go to the minecraft wiki and find the note ranges for ceratin sounds and convert them.
# For example, the piano in minecraft has a range of F#3 to F#5, 2 octaves and a note (25 notes).
# We ignore the extra note and just take the base 30 and add 2 ocvates worth of ntoes to it (24) to get 54.
# Same thing with the strings, chimes are 4 octives away from F#1 so 4 times 12 is 48 + 30 is 78
# Easy enough to do properly
try:
    os.mkdir("luaDat")
except OSError:
    print("Creation of directory failed")
else:
    print("Successfully created directory")
f = open("luaDat/drums.lua", "w+")
extraTicks = 0
for event in drums:
    # if the event is not "Note On", add its ticks to a buffer that will add it to the next "Note On" event
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        # If the note is not apart of a chord, and the volume of the note is not 0, make a sleep command with the folowing formula
        # Seconds = ticks/ticks per beat / beats per second
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('snare', {3/127 * event.velocity}, {event.pitch-30})\n")
        # If the note makes no sound, ignore but add ticks to next "Note On" event that has sound.
        # This is needed to ignore suistained notes as there are no sustained notes in minecraft
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            # If the ticks inbetween "Note On" events are 0, just add them without sleeping.
            # This is used to make chords
            f.write(f"speaker.playNote('snare', {3/127 * event.velocity}, {event.pitch-30})\n")
        extraTicks = 0
f.close()

f = open("luaDat/drums2.lua", "w+")
extraTicks = 0
for event in drums2:
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('snare', {3/127 * event.velocity}, {event.pitch-30})\n")
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            f.write(f"speaker.playNote('snare', {3/127 * event.velocity}, {event.pitch-30})\n")
        extraTicks = 0
f.close()

f = open("luaDat/piano.lua", "w+")
extraTicks = 0
for event in piano:
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        # This while event makes sure that if a note in a chord is just below the 2 octave range.
        # This is technically not the same chord and is called an inverted chord but its fine for what you need lol.
        while event.pitch - 54 < 0:
            event.pitch += 12
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('pling', {3/127 * event.velocity}, {event.pitch-54})\n")
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            f.write(f"speaker.playNote('pling', {3/127 * event.velocity}, {event.pitch-54})\n")
        extraTicks = 0
f.close()

f = open("luaDat/strings.lua", "w+")
extraTicks = 0
for event in strings:
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        while event.pitch - 78 < 0:
            event.pitch += 12
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('chime', {3/127 * event.velocity}, {event.pitch-78})\n")
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            f.write(f"speaker.playNote('chime', {3/127 * event.velocity}, {event.pitch-78})\n")
        extraTicks = 0
f.close()

f = open("luaDat/brass.lua", "w+")
extraTicks = 0
for event in brass:
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        while event.pitch - 66 < 0:
            event.pitch += 12
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('cow_bell', {3/127 * event.velocity}, {event.pitch-66})\n")
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            f.write(f"speaker.playNote('cow_bell', {3/127 * event.velocity}, {event.pitch-66})\n")
        extraTicks = 0
f.close()

f = open("luaDat/sax.lua", "w+")
extraTicks = 0
for event in sax:
    if event.eventName != "Note On":
        extraTicks += event.ticks
    else:
        if (event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60) != 0 and event.velocity != 0:
            f.write(f"os.sleep({round((event.ticks + extraTicks) / meta['TPB'] / (meta['BPM']/60), 8)})\n")
            f.write(f"speaker.playNote('bit', {3/127 * event.velocity}, {event.pitch-54})\n")
        elif 3/127 * event.velocity == 0:
            extraTicks += event.ticks
            continue
        else:
            f.write(f"speaker.playNote('bit', {3/127 * event.velocity}, {event.pitch-54})\n")
        extraTicks = 0
f.close()


# And now the big boy merger, this is just some annoying math that you can copy part for part.
# I still need to fix the while statement, right now it'll cut the end off of a song.
# You can delete the print statments if you want, those were for debugging.
def merge(mergeA, mergeB):
    indexA = 0
    indexB = 0
    timeA = 0
    timeB = 0
    merged = []
    try:
        while True:
        # while indexA in range(len(mergeA)) and indexB in range(len(mergeB)):
            if "playNote" in mergeA[indexA]:
                merged.append(mergeA[indexA])
                indexA += 1
            elif "playNote" in mergeB[indexB]:
                merged.append(mergeB[indexB])
                indexB += 1
            elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) < round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
                print(str(round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8)) + " is less then " + str(round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8)))
                merged.append(f"os.sleep({round(float(mergeA[indexA].strip('os.sleep()')) - float(timeA), 8)})")
                timeB += float(mergeA[indexA].strip('os.sleep()')) - float(timeA)
                timeA = 0
                indexA += 1
            elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) > round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
                print(str(round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8)) + " is greater then " + str(round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8)))
                merged.append(f"os.sleep({round(float(mergeB[indexB].strip('os.sleep()')) - float(timeB), 8)})")
                timeA += float(mergeB[indexB].strip('os.sleep()')) - float(timeB)
                indexB += 1
                timeB = 0
            else:
                merged.append("os.sleep({})".format(float(mergeA[indexA].strip("os.sleep()")) - timeA))
                timeA = 0
                timeB = 0
                indexA += 1
                indexB += 1
    except IndexError:
        print("finished")
        return merged


# Opens all the files and gets their commands (with out functions, guess im just stupid/lazy).
# The whole saving and opening file thing is redundent but I used it while debugging.
drumMerge = []
pianoMerge = []
stringsMerge = []
brassMerge = []
saxMerge = []
with open("luaDat/drums.lua", "r") as d:
    drumMerge = d.readlines()
    for x in range(0, len(drumMerge)):
        drumMerge[x] = drumMerge[x].strip("\n")
    d.close()
with open("luaDat/piano.lua", "r") as p:
    pianoMerge = p.readlines()
    for x in range(0, len(pianoMerge)):
        pianoMerge[x] = pianoMerge[x].strip("\n")
    p.close()
with open("luaDat/strings.lua", "r") as s:
    stringsMerge = s.readlines()
    for x in range(0, len(stringsMerge)):
        stringsMerge[x] = stringsMerge[x].strip("\n")
    s.close()
with open("luaDat/brass.lua", "r") as b:
    brassMerge = b.readlines()
    for x in range(0, len(brassMerge)):
        brassMerge[x] = brassMerge[x].strip("\n")
    b.close()
with open("luaDat/sax.lua", "r") as s:
    saxMerge = s.readlines()
    for x in range(0, len(saxMerge)):
        saxMerge[x] = saxMerge[x].strip("\n")
    s.close()

# Merges each part together and saves it as a file with the find speaker line at the top.
# Additionally, I manually added the drum filler in the beginning for Never Gonna Give You Up form the drums2.lua file created
merge1 = merge(drumMerge, pianoMerge)
merge2 = merge(merge1, stringsMerge)
merge3 = merge(merge2, brassMerge)
merge4 = merge(merge3, saxMerge)
with open("luaDat/merged.lua", "w+") as m:
    m.write("local speaker = peripheral.find('speaker')\n\n")
    for x in merge4:
        m.write(x + "\n")
    m.close()
