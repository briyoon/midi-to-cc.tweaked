import midi
from generalMidi import generalMidiInstList, percussionMidiInstList


# Object for each midiEvent
class MidiEvent:
    def __init__(self, eventName, ticks, velocity=0, pitch=0, bpm=0):
        self.eventName = eventName
        self.velocity = velocity
        self.pitch = pitch
        self.ticks = ticks
        self.bpm = bpm


# objext for midi file meta
class MidiMeta:
    def __init__(self, ticksPerBeat, timeSig, BPM, MSPB):
        self.timeSig = timeSig
        self.BPM = BPM
        self.TPB = ticksPerBeat
        self.MSPB = MSPB


# grabs meta data from midi to find Ticks per Beat, Time Signature, BPM, and Microseconds Per Beat.
# discovered that each meta event will have a meta command. I am using this to find the vars above.
# THIS WILL CHANGE DEPENDING ON WHAT LIBRARY YOU USE (you basically have a choice between this and the mido library for python)
def scrapeMeta(pattern):
    # returnMeta = False
    midiMeta = MidiMeta(0, 0, 0, 0)
    try:
        # ticks per beat is found at the top of midi data
        midiMeta.TPB = pattern.resolution
        for track in pattern:
            for x in track:
                # meta command for time signature = 88
                if x.metacommand == 88:
                    midiMeta.timeSig = f"{x.numerator}/{x.denominator}"
                # meta command for BPM = 81
                # set tempo command also has micro seconds per beat
                elif x.metacommand == 81:
                    midiMeta.BPM = x.bpm
                    midiMeta.MSPB = x.mpqn
                    return midiMeta
    except AttributeError:
        print("attribute error")


# scrapes tracks from midi file
def scrapeTracks(pattern):
    midiTracks = {}
    drumNum = 1
    # searches each track
    for track in range(len(pattern)):
        detectNote = False
        detectProgram = False
        detectName = False
        detectPercussion = False
        instrumentName = []
        # searches each event in track
        for x in pattern[track]:
            if not detectNote and "Note On" in x.name:
                detectNote = True
            elif not detectProgram and "Program Change" in x.name:
                detectProgram = True
                # grabs instrument name from general midi list
                # (exmaple: https://jazz-soft.net/demo/GeneralMidi.html)
                if generalMidiInstList[x.value] in midiTracks.keys():
                    dupe = 1
                    for each in midiTracks.keys():
                        if each == generalMidiInstList[x.value]:
                            dupe += 1
                    instrumentName = generalMidiInstList[x.value] + f" {dupe}"
                else:
                    instrumentName = generalMidiInstList[x.value]
                if not detectName and hasattr(x, "text"):
                    detectName = x.text
            # marks a track as a percussion track
            # which has to use a different midi list found here
            # (https://jazz-soft.net/demo/GeneralMidiPerc.html)
            if hasattr(x, "channel") and x.channel == 9:
                detectPercussion = True

        # if track has a note in it, print info about track
        # it also saves it to mitiTracks dict with proper naming
        if detectNote:
            # print(f"Detected note in track {track}")
            # if percussion track, name it drums
            # has a counter to adjust for multiple drum tracks
            if detectPercussion:
                midiTracks[f"Drums {drumNum}"] = pattern[track]
                drumNum += 1
                # print(f"    Track {track} is a drum track")
            else:
                # if instrument change detected,
                # print instrument name and save to midiTracks
                if detectProgram:
                    midiTracks[instrumentName] = pattern[track]
                    # print(f"    Track {track}'s name is {instrumentName}")
                # otherwise if no instrument change detected,
                # grab last track name and append bass onto it
                # then save to midiTracks
                # (most likly solution, needs more testing)
                else:
                    midiTracks[[*midiTracks][len(midiTracks) - 1] + " (bass)"] = pattern[track]
                    # print(f"    No program change in track {track} deteced (usually means its the bass part of the last track)")
                    # print(f"    Track {track}'s name is {[*midiTracks][track-1] + ' (bass)'}")
    return midiTracks


# Loads all the midi events from each instrument track into an array
def getMidiEvents(instruments):
    instrumentData = {}
    for instrument in instruments:
        instrumentName = instrument
        instrument = instruments[instrument]
        tempData = []
        for x in instrument:
            try:
            # The way I scraped events was if the midi event was "Note On",
            # to pass args to fill out the whole midiEventObj.
                if x.name == "Note On":
                    tempData.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                elif x.name == "Set Tempo":
                    tempData.append(MidiEvent(x.name, x.tick, bpm=x.bpm))
                else:
                    # Otherwise I just saved the ticks inbetween events as objects without velocity or pitch.
                    tempData.append(MidiEvent(x.name, x.tick))
            except AttributeError:
                print("skipped Index")
        instrumentData[instrumentName] = tempData
    return instrumentData


# trasnlate the midi code to lua
def translateMidi(instrumentMidi):
    instrumentLua = []
    for instrument in instrumentMidi:
        instrumentName = instrument
        instrument = instrumentMidi[instrument]
        luaCode = []
        extraTicks = 0
        for event in instrument:
            # if event.eventName == "Set Tempo":
            #     meta.BPM = event.bpm
            if event.eventName != "Note On":
                extraTicks += event.ticks
            else:
                minecraftPitch = event.pitch-30-(noteBlockRangeStart[instrumentName]*12)
                sleep = round((event.ticks + extraTicks) / meta.TPB / (meta.BPM/60), 8)
                # This while loop checks if a note in a chord is just below the 2 octave range and moves it up an octave.
                # This is technically not the same chord and is called an inverted chord but its fine for what you need.
                while minecraftPitch < 0:
                    minecraftPitch += 12
                if sleep != 0 and event.velocity != 0:
                    luaCode.append(f"os.sleep({sleep})\n")
                    luaCode.append(f"speaker.playNote('{instrumentName}', {round(3/127 * event.velocity, 8)}, {minecraftPitch})\n")
                    extraTicks = 0
                elif 3/127 * event.velocity == 0:
                    extraTicks += event.ticks
                    continue
                else:
                    luaCode.append(f"speaker.playNote('{instrumentName}', {round(3/127 * event.velocity, 8)}, {minecraftPitch})\n")
        instrumentLua.append(luaCode)
    return instrumentLua


# And now the big boy merger, this is just some annoying math that you can copy part for part.
# I still need to fix the while statement, right now it'll cut the end off of a song.
# You can delete the print statments if you want, those were for debugging.
def merge(mergeA, mergeB):
    for x in range(len(mergeA)):
        mergeA[x] = mergeA[x].strip("\n")
    for x in range(len(mergeB)):
        mergeB[x] = mergeB[x].strip("\n")
    indexA = 0
    indexB = 0
    timeA = 0
    timeB = 0
    merged = []
    try:
        # while True:
        while indexA in range(len(mergeA)) or indexB in range(len(mergeB)):
            if "playNote" in mergeA[indexA]:
                merged.append(mergeA[indexA])
                indexA += 1
            elif "playNote" in mergeB[indexB]:
                merged.append(mergeB[indexB])
                indexB += 1
            elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) < round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
                # print(str(round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8)) + " is less then " + str(round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8)))
                merged.append(f"os.sleep({round(float(mergeA[indexA].strip('os.sleep()')) - float(timeA), 8)})")
                timeB += float(mergeA[indexA].strip("os.sleep()")) - float(timeA)
                timeA = 0
                indexA += 1
            elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) > round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
                # print(str(round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8)) + " is greater then " + str(round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8)))
                merged.append(f"os.sleep({round(float(mergeB[indexB].strip('os.sleep()')) - float(timeB), 8)})")
                timeA += float(mergeB[indexB].strip("os.sleep()")) - float(timeB)
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


# Using this branch of 'python-midi' for python3 (https://github.com/sniperwrb/python-midi)
global noteBlockRangeStart
noteBlockRangeStart = {
    "bass": 1,
    "snare": 2,
    "hat": 0,
    "bd": 0,
    "bell": 4,
    "flute": 3,
    "chime": 4,
    "guitar": 1,
    "xylophone": 4,
    "iron_xylophone": 2,
    "cow_bell": 2,
    "didgeridoo": 0,
    "bit": 2,
    "banjo": 2,
    "pling": 2,
    "harp": 3
}
global pattern
global meta
midiName = input("Input file path: ")
# midiName = "sample_midi/rickroll3.mid"
pattern = midi.read_midifile(midiName)
meta = scrapeMeta(pattern)
tracks = scrapeTracks(pattern)
print(f"Found {len(tracks)} tracks:")

for x in tracks:
    print("    " + x)
convertWhich = input(
    "Please type which tracks you would like to convert with a minecraft sound:\n\
Example: 'piano:harp brass-section:bit'\n(for a list of minecraft sound names please go to\
https://minecraft.gamepedia.com/Note_Block)\nPLEASE DO NOT CONVERT A DRUM TRACK YET\n").lower()
# convertWhich = "electric-piano-2:pling test:test2"
convertWhich = convertWhich.split()
for x in range(len(convertWhich)):
    convertWhich[x] = convertWhich[x].replace("-", " ")
    convertWhich[x] = convertWhich[x].split(":")

convertTracks = {}
for x in tracks:
    for y in range(len(convertWhich)):
        if x == convertWhich[y][0]:
            convertTracks[convertWhich[y][1]] = tracks[x]

instrumentMidi = getMidiEvents(convertTracks)

luaCommands = []
luaCommands = translateMidi(instrumentMidi)

merged = luaCommands[0]
for x in range(1, len(luaCommands)):
    merged = merge(merged, luaCommands[x])

with open(f"{midiName.replace('.mid', '.lua')}", "w+") as f:
    f.write("local speaker = peripheral.find('speaker')\n\n")
    for x in merged:
        f.write(x + "\n")
    f.close()
