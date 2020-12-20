# midi-to-cc.tweaked

[![Alt text](https://img.youtube.com/vi/QLyWg_v8z5U/0.jpg)](https://www.youtube.com/watch?v=QLyWg_v8z5U)

Used https://minecraft.gamepedia.com/Note_Block to find noteblock ranges and sound names!

# Installation
To use this program make sure to install python-midi library with:
- Python 3: https://github.com/vishnubob/python-midi/issues/184

# Usage
1. Type path to midi file
2. Input instruments you want to convert
   - I recomend opening the midi file in a midi viewer such as Musescore first to figure out which tracks you want to convert
3. *(Hopefully)* Profit!

If you need help there are example configs in the sample_midi folder

# Tips
- Use Musescore to find midi tracks
  - The "cleaner" the midi file the better
  - Less instruments are better
  - I know rolled chords and complicated bass chords sound cool, but it really hurts the sound quality in game

# ToDo
- ~~Reliably finding tracks (medium)~~ done
  - ~~I was using metacommand = 3 to find tracks however this is not it. musescore is able to tell the different tracks apart. Maybe look at status messages? I see there are channels assigned to events too but in musescore for rickroll3.mid, DRUMS and bongo are on the same channel but different staffs/tracks.~~
  - ProgramChangeEvent is the event that lets you know there is an instrument change!
- Accuratly finding ranges for tracks. (easy)
  - (Most) MineCraft sounds can only play 2 octaves. I need to figure out a way to reliably find the range and adjust properly.
  - ~~Added a simple fix, will see if this is good enough~~ Wasn't good enough (as apparent in alliwant.mid)
- ~~Allow tempo changes (hard)~~ done
  - Found an example online of finding proper timing of events with chagnes in tempo and modified code to fit mine. However, this increased the conversion time from less then a second to several seconds due to the amount of for loops and iter() functions. Might try to fix
     - Found that it is creating a tempo map for each event, I need to modify it to where it only uses one tempoMap
- Add drum track support (easy)
  - Have to find each precussion sound manually
  - 16/46 (most common drum sounds first)
    - Havn't tuned the sounds to their final point
    - Might experiment with double sounds
- ~~Fix merging tracks that don't end at the same time (easy)~~ done
- ~~Look into fixing volume scale (easy)~~ done
  - ~~I think it's an exponential function rather than linear~~ 0-1 is volume, 1-3 is max volume but increases in range
- ~~Added some simple logs~~ (easy) done
- Clean up my messy code lol (hard :P)

# Future Features

- Add a mixer to change track volumes. (medium)
- GUI practice at the very end. (hard)

# Considered Features
- Maybe add swing into the track to make it sound more human.
