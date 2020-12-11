import midi


# Object for each midiEvent
class MidiEvent:
    def __init__(self, eventName, ticks, velocity=0, pitch=0):
        self.eventName = eventName
        self.velocity = velocity
        self.pitch = pitch
        self.ticks = ticks


# objext for midi file meta
class MidiMeta:
    def __init__(self, ticksPerBeat, timeSig, BPM, MSPB):
        self.timeSig = timeSig
        self.BPM = BPM
        self.ticksPerBeat = ticksPerBeat
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


# grabs track names by searching for meta command = 3
# for some reason end of track and start of track commands also have meta command = 3,
# so i filter them out by searching for length too

# meta command 3 is not he way to search for tracks properly... doesnt work on rickroll2.mid
# However, musescore is able to tell the different tracks apart. Maybe look at status messages?
# I see there are channels assigned to events too but in musescore for rickroll3.mid, DRUMS and bongo are on the same channel but different staffs/tracks
def scrapeTracks(pattern):
    instruments = []
    for track in pattern:
        try:
            for x in track:
                if len(track) > 2 and x.metacommand == 3:
                    instruments.append(x.text)
        except AttributeError:
            pass
    return instruments


# Loads all the midi events from each instrument track into an array
def getMidiEvents(instruments):
    instrumentData = {}
    for instrument in instruments:
        for track in pattern:
            try:
                if track[0].metacommand == 3 and track[0].text.lower() == instrument.split(":")[0]:
                    tempData = []
                    for x in track:
                        try:
                        # The way I scraped events was if the midi event was "Note On",
                        # to pass args to fill out the whole midiEventObj.
                            if x.name == "Note On":
                                tempData.append(MidiEvent(x.name, x.tick, x.velocity, x.pitch))
                            else:
                                # Otherwise I just saved the ticks inbetween events as objects without velocity or pitch.
                                tempData.append(MidiEvent(x.name, x.tick))
                        except AttributeError:
                            print("skipped Index")
                    instrumentData[instrument] = tempData
                    print("")
            except AttributeError:
                print("Skipped track")
    return instrumentData


# trasnlate the midi code to lua
def translateMidi(instrumentMidi):
    instrumentLua = []
    for instrument in instrumentMidi:
        luaCode = []
        extraTicks = 0
        for event in instrumentMidi[instrument]:
            if event.eventName != "Note On":
                extraTicks += event.ticks
            else:
                minecraftPitch = event.pitch-30-(noteBlockRangeStart[instrument.split(':')[1]]*12)
                sleep = round((event.ticks + extraTicks) / meta.ticksPerBeat / (meta.BPM/60), 8)
                # This while loop checks if a note in a chord is just below the 2 octave range and moves it up an octave.
                # This is technically not the same chord and is called an inverted chord but its fine for what you need.
                while minecraftPitch < 0:
                    minecraftPitch += 12
                if sleep != 0 and event.velocity != 0:
                    luaCode.append(f"os.sleep({sleep})\n")
                    luaCode.append(f"speaker.playNote('{instrument.split(':')[1]}', {3/127 * event.velocity}, {minecraftPitch})\n")
                    extraTicks = 0
                elif 3/127 * event.velocity == 0:
                    extraTicks += event.ticks
                    continue
                else:
                    luaCode.append(f"speaker.playNote('{instrument.split(':')[1]}', {3/127 * event.velocity}, {minecraftPitch})\n")
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
                timeB += float(mergeA[indexA].strip("os.sleep()")) - float(timeA)
                timeA = 0
                indexA += 1
            elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) > round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
                print(str(round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8)) + " is greater then " + str(round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8)))
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
# I included 3 different midi files, I found that this thrid one worked the best
global noteBlockRangeStart
noteBlockRangeStart = {
    "bass": -1,
    "snare": 2,
    "hat": 0,
    "bd": 0,
    "bell": 4,
    "flute": 4,
    "chime": 4,
    "guitar": 1,
    "xylophone": 4,
    "iron_xylophone": 2,
    "cow_bell": 2,
    "didgeridoo": 0,
    "bit": 2,
    "banjo": 2,
    "pling": 2,
    "harp": 2
}
global pattern
global meta
midiName = input("Input file name (must be in the same dir): ")
pattern = midi.read_midifile(midiName)
meta = scrapeMeta(pattern)
tracks = scrapeTracks(pattern)
print(f"Found {len(tracks)} tracks:")
for x in tracks:
    print("    " + x)
convertWhich = input("Please type which tracks you would like to convert with a minecraft sound:\nExample: 'piano:harp sax:bit'\n(for a list of minecraft sound names please go to https://minecraft.gamepedia.com/Note_Block)\n").lower()
convertWhich = convertWhich.split()
for x in range(len(convertWhich)):
    convertWhich[x] = convertWhich[x].replace("-", " ")
instrumentMidi = getMidiEvents(convertWhich)
luaCommands = []
luaCommands = translateMidi(instrumentMidi)
merged = luaCommands[0]
for x in range(1, len(luaCommands)):
    merged = merge(merged, luaCommands[x])
with open(f"{midiName.replace('.mid', '')}.lua", "w+") as f:
    f.write("local speaker = peripheral.find('speaker')\n\n")
    for x in merged:
        f.write(x + "\n")
    f.close()
