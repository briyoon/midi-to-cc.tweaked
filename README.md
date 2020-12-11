# midi-to-cc.tweaked

Used https://minecraft.gamepedia.com/Note_Block to find noteblock ranges and sound names!

# Problems
- Reliably finding tracks
  - I was using metacommand = 3 to find tracks however this is not it. musescore is able to tell the different tracks apart. Maybe look at status messages? I see there are channels assigned to events too but in musescore for rickroll3.mid, DRUMS and bongo are on the same channel but different staffs/tracks.
  - Maybe I can search for both metacommand and channel number?
- Accuratly finding ranges for tracks.
  - (Most) MineCraft sounds can only play 2 octaves. I need to figure out a way to reliably find the range and adjust properly.

# Future Features

- In the future im going to beable to read the drum part and read pitches to determine which ones are hats, snares, and kicks like how midi programs do.
- Add a mixer to change track volumes.
- GUI practice at the very end.

# Considered Features
- Maybe add swing into the track to make it sound more human.
