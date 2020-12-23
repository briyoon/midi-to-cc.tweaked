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

Recently added a sample album to see how this could be implemented. Unfortunately floppy disks are too small to put these files onto
# Tips
- Use Musescore to find midi tracks
  - The "cleaner" the midi file the better
  - Less instruments are better
  - I know rolled chords and complicated bass chords sound cool, but it really hurts the sound quality in game
# Features
- Find tracks (instruments) using the Program Change Event
- Creates a tempo map of the song to allow tempo changes throughout midi file
- Notes have different volumes depending on the midi velocity value
- Simple logging
# ToDo
- Finish drum track support (easy)
  - Have to find each precussion sound manually
  - 16/46 sounds done (most common drum sounds first)
    - Havn't tuned the sounds to their final point
    - Might experiment with double sounds
- Fix tempo change loops to cut down on conversion time (???)
  - Might not be possible, right now it takes a full minute to convert through the fire and flames
- Redo finding track ranges (???)
- Add error messages when typing in wrong tracks (easy)
- Clean up my messy code lol (hard :P)
# Future Features
- Add a mixer to change track volumes
- Maybe add swing into the track to make it sound more human
- GUI practice at the very end
