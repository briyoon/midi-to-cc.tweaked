# midi-to-cc.tweaked

[![Alt text](https://img.youtube.com/vi/QLyWg_v8z5U/0.jpg)](https://www.youtube.com/watch?v=QLyWg_v8z5U)

Used https://minecraft.gamepedia.com/Note_Block to find noteblock ranges and sound names!

# Installation
To use this program make sure to install python-midi library

# Usage
1. Type Path to midi file
2. Input instruments you want to convert
   - I recomend opening the midi file in a midi viewer such as Musescore first to figure out which tracks you want to convert
3. *(Hopefully)* Profit!

# Tips
- Use Musescore to find midi tracks
  - The "cleaner" the midi file the better
  - Less instruments are better
- I've included some exmaple configs to show that it works

# ToDo
- ~~Reliably finding tracks~~
  - ~~I was using metacommand = 3 to find tracks however this is not it. musescore is able to tell the different tracks apart. Maybe look at status messages? I see there are channels assigned to events too but in musescore for rickroll3.mid, DRUMS and bongo are on the same channel but different staffs/tracks.~~
  - ProgramChangeEvent is the event that lest you know there is an instrument change!
- Accuratly finding ranges for tracks.
  - (Most) MineCraft sounds can only play 2 octaves. I need to figure out a way to reliably find the range and adjust properly.
- Allow tempo changes
- Clean up my messy code lol

# Future Features

- In the future im going to beable to read the drum part and read pitches to determine which ones are hats, snares, and kicks like how midi programs do.
- Add a mixer to change track volumes.
- GUI practice at the very end.

# Considered Features
- Maybe add swing into the track to make it sound more human.
