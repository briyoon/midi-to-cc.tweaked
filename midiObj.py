class MidiEvent:
    def __init__(self, eventName, ticks, velocity=0, pitch=0):
        self.eventName = eventName
        self.velocity = velocity
        self.pitch = pitch
        self.ticks = ticks
