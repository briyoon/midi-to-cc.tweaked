import midi


def getTempoMap(pattern, maxTick=None):
    # create a first tempo (default to 120, if there is no tempo event)
    tempoMap = [[0, .5 / pattern.resolution]]
    lastTick = 0
    for track in pattern:
        for event in track:
            if maxTick is not None and event.tick > maxTick:
                continue
            if isinstance(event, midi.SetTempoEvent):
                # set the first tempo event if tick=0
                if not event.tick:
                    tempoMap[0][1] = 60. / pattern.resolution / event.bpm
                # set duration of the previous tempo event
                else:
                    tempoMap[-1][0] = event.tick
                    tempoMap.append([0, 60. / pattern.resolution / event.bpm])
        lastTick = max(lastTick, event.tick)

    # set duration of last tempo change based on latest event tick
    tempoMap[-1][0] = lastTick
    return list(sorted(tempoMap, key=lambda e: e[0]))


# return timing of a single event, from a given the pattern,
# using the track and event number
def getEventTime(pattern, event, tempoMap):
    relative = pattern.tick_relative
    pattern.make_ticks_abs()
    maxTick = event.tick
    pattern.make_ticks_rel()

    tick = time = 0
    tempoMap = iter(tempoMap)
    nextTick, tickLength = next(tempoMap)

    while nextTick < maxTick:
        time += (nextTick - tick) * tickLength
        tick = nextTick
        nextTick, tickLength = next(tempoMap)

    # restore previous status
    if not relative:
        pattern.make_ticks_abs()
    # add remaining ticks
    return time + (maxTick - tick) * tickLength
