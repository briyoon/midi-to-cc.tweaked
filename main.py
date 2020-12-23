import logging
import traceback
import midi
from generalMidi import generalMidiInstList, percussionMidiInstList, noteBlockRangeStart
from midi_timings import getEventTime, getTempoMap


# object for midi file meta
class MidiMeta:
    def __init__(self, ticksPerBeat, timeSig, BPM, MSPB):
        self.timeSig = timeSig
        self.BPM = BPM
        self.TPB = ticksPerBeat
        self.MSPB = MSPB


# grabs meta data from midi to find Ticks per Beat, Time Signature, BPM, and Microseconds Per Beat.
# discovered that each meta event will have a meta command. I am using this to find the vars above.
def scrapeMeta(pattern):
    midiMeta = MidiMeta(0, 0, 0, 0)
    try:
        # ticks per beat is found at the top of midi data
        midiMeta.TPB = pattern.resolution
        for track in pattern:
            for x in track:
                # meta command for time signature = 88
                if x.metacommand == 88:
                    midiMeta.timeSig = f"{x.numerator}/{x.denominator}"
                # meta command for set tempo = 81
                # set tempo command has bpm and micro seconds per beat
                elif x.metacommand == 81:
                    midiMeta.BPM = x.bpm
                    midiMeta.MSPB = x.mpqn
                    return midiMeta
    except AttributeError:
        logging.warning("Scrape Meta: attribute error [may not be able to finish conversion]")


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
            logging.info(f"Scrape Tracks: Detected note in track {track}")
            # if percussion track, name it drums
            # has a counter to adjust for multiple drum tracks
            if detectPercussion:
                midiTracks[f"Drums {drumNum}"] = pattern[track]
                drumNum += 1
                logging.info(f"Scrape Tracks: Track {track} is a drum track")
            else:
                # if instrument change detected,
                # print instrument name and save to midiTracks
                if detectProgram:
                    midiTracks[instrumentName] = pattern[track]
                    logging.info(f"Scrape Tracks: Track {track}'s name is {instrumentName}")
                # otherwise if no instrument change detected,
                # grab last track name and append bass onto it
                # then save to midiTracks
                # (most likly solution, needs more testing)
                else:
                    midiTracks[[*midiTracks][len(midiTracks) - 1] + " (bass)"] = pattern[track]
                    logging.info(f"Scrape Tracks: No program change in track {track} deteced (usually means its the bass part of the last track)")
                    logging.info(f"Scrape Tracks: Track {track}'s name is {[*midiTracks][track-1] + ' (bass)'}")
    return midiTracks


# trasnlate the midi code to lua
def translateMidi(instrumentMidi):
    instrumentLua = []
    for instrument in instrumentMidi:
        instrumentName = instrument
        instrument = instrumentMidi[instrument]
        luaCode = []
        extraTicks = 0
        sleepTemp = 0
        # if it is a drum track, convert with sepcial rules
        if instrumentName == "Drums":
            for event in instrument:
                if event.name != "Note On":
                    extraTicks += event.tick
                else:
                    drumNote = percussionMidiInstList[event.pitch-35].split(":")
                    sleep = getEventTime(pattern, event, tempoMap)
                    logging.debug(f"Translate MIDI: Sound: {drumNote[0]}, Pitch: {drumNote[1]}, Timing: {sleep}")

                    # if there is sleep and note plays, write the sleep amount and note
                    if sleep-sleepTemp != 0 and event.velocity != 0:
                        luaCode.append(f"os.sleep({abs(sleep - sleepTemp)})")
                        luaCode.append(f"speaker.playNote('{drumNote[0]}', {round(event.velocity / 127, 8)}, {drumNote[1]})")
                        extraTicks = 0
                        sleepTemp = sleep
                    # if the note has no volume, add ticks
                    elif event.velocity == 0:
                        extraTicks += event.tick
                    # else write the rest of drumkit
                    else:
                        luaCode.append(f"speaker.playNote('{drumNote[0]}', {round(event.velocity / 127, 8)}, {drumNote[1]})")
            instrumentLua.append(luaCode)
        else:
            for event in instrument:
                if event.name != "Note On":
                    extraTicks += event.tick
                else:
                    minecraftPitch = event.pitch-30-(noteBlockRangeStart[instrumentName]*12)
                    sleep = getEventTime(pattern, event, tempoMap)
                    logging.debug(f"Translate MIDI: Sound: {instrumentName}, Pitch: {minecraftPitch}, Timing: {sleep}")

                    # This while loop checks if a note in a chord is just below the 2 octave range and moves it up an octave.
                    # This is technically not the same chord and is called an inverted chord but its fine for what you need.
                    while minecraftPitch < 0:
                        minecraftPitch += 12
                    # also checks if the note is too high
                    while minecraftPitch > 24:
                        minecraftPitch -= 12
                    # if there is sleep and note plays, write the sleep amount and note
                    if sleep-sleepTemp != 0 and event.velocity != 0:
                        luaCode.append(f"os.sleep({abs(sleep - sleepTemp)})")
                        luaCode.append(f"speaker.playNote('{instrumentName}', {round(event.velocity / 127, 8)}, {minecraftPitch})")
                        extraTicks = 0
                        sleepTemp = sleep
                    # if the note has no volume, add ticks
                    elif event.velocity == 0:
                        extraTicks += event.tick
                    # else write the rest of the chord
                    else:
                        luaCode.append(f"speaker.playNote('{instrumentName}', {round(event.velocity / 127, 8)}, {minecraftPitch})")
            instrumentLua.append(luaCode)
    return instrumentLua


# Merge function for merging two lists together sorted by os.sleep() length
def merge(mergeA, mergeB):
    indexA = 0
    indexB = 0
    timeA = 0
    timeB = 0
    merged = []
    while indexA in range(len(mergeA)) or indexB in range(len(mergeB)):
        # check if listA is out of index
        try:
            mergeA[indexA]
        # if out of index, add the rest of listB
        except IndexError:
            for x in range(indexB, len(mergeB)):
                merged.append(mergeB[x])
            logging.info("Merge: Merge complete")
            return merged
        # check if listB is out of index
        try:
            mergeB[indexB]
        # if out of index, add the rest of listA
        except IndexError:
            for x in range(indexA, len(mergeA)):
                merged.append(mergeA[x])
            logging.info("Merge: Merge complete")
            return merged
        if "playNote" in mergeA[indexA]:
            merged.append(mergeA[indexA])
            indexA += 1
        elif "playNote" in mergeB[indexB]:
            merged.append(mergeB[indexB])
            indexB += 1
        elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) < round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
            logging.debug(f"Merge: {str(round(float(mergeA[indexA].strip('os.sleep()')) - float(timeA), 8))} is less then {str(round(float(mergeB[indexB].strip('os.sleep()')) - float(timeB), 8))}")
            merged.append(f"os.sleep({round(float(mergeA[indexA].strip('os.sleep()')) - float(timeA), 8)})")
            timeB += float(mergeA[indexA].strip("os.sleep()")) - float(timeA)
            timeA = 0
            indexA += 1
        elif round(float(mergeA[indexA].strip("os.sleep()")) - float(timeA), 8) > round(float(mergeB[indexB].strip("os.sleep()")) - float(timeB), 8):
            logging.debug(f"Merge: {str(round(float(mergeA[indexA].strip('os.sleep()')) - float(timeA), 8))} is greater then {str(round(float(mergeB[indexB].strip('os.sleep()')) - float(timeB), 8))}")
            merged.append(f"os.sleep({round(float(mergeB[indexB].strip('os.sleep()')) - float(timeB), 8)})")
            timeA += float(mergeB[indexB].strip("os.sleep()")) - float(timeB)
            indexB += 1
            timeB = 0
        else:
            logging.debug("Merge: Equal timing")
            merged.append("os.sleep({})".format(float(mergeA[indexA].strip("os.sleep()")) - timeA))
            timeA = 0
            timeB = 0
            indexA += 1
            indexB += 1


# takes all tracks and a list of tracks to convert
def convert(tracks, convertList):
    convertTracks = {}
    for x in tracks:
        for y in range(len(convertList)):
            if x == convertList[y][0]:
                convertTracks[convertList[y][1]] = tracks[x]

    luaCommands = translateMidi(convertTracks)

    merged = luaCommands[0]
    for x in range(1, len(luaCommands)):
        merged = merge(merged, luaCommands[x])

    return merged


# Use this branch of 'python-midi' for python3 (https://github.com/sniperwrb/python-midi)
global pattern
global meta
global tempoMap

# Quick logging setup
logging.basicConfig(filename='logs.log', filemode='w', level=logging.DEBUG)

# get midi path and scrape meta and tracks
midiName = input("Input midi file path: ")
pattern = midi.read_midifile(midiName)
meta = scrapeMeta(pattern)
tracks = scrapeTracks(pattern)

# change ticks to absolute and get tempo map then change ticks back to relative
pattern.make_ticks_abs()
tempoMap = getTempoMap(pattern)
pattern.make_ticks_rel()

# display found tracks and ask which tracks should be converted
print(f"Found {len(tracks)} tracks:")
for x in tracks:
    print("    " + x)
convertList = input(
    "Please type which tracks you would like to convert with a minecraft sound:\n\
Example: 'piano:harp brass-section:bit drums:drums'\n(for a list of minecraft sound names please go to\
https://minecraft.gamepedia.com/Note_Block)\nDRUMS ARE UNTESTED\n").lower().split()
for x in range(len(convertList)):
    convertList[x] = convertList[x].replace("-", " ")
    convertList[x] = convertList[x].split(":")
print("Converting, please wait...")

# take all tracks, and a list of tracks to converted and return a merged list (in correct time order) of lua code
merged = convert(tracks, convertList)

# write to output file and tell user
with open(f"{midiName.replace('.mid', '.lua')}", "w+") as f:
    f.write("local speaker = peripheral.find('speaker')\n\n")
    for x in merged:
        f.write(x + "\n")
    print(f"Finished, wrote to {midiName.replace('.mid', '.lua')}")
    f.close()
