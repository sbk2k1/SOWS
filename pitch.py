#! /usr/bin/env python

# Use pyaudio to open the microphone and run aubio.pitch on the stream of
# incoming samples. If a filename is given as the first argument, it will
# record 5 seconds of audio to this location. Otherwise, the script will
# run until Ctrl+C is pressed.

# Examples:
#    $ ./python/demos/demo_pyaudio.py
#    $ ./python/demos/demo_pyaudio.py /tmp/recording.wav

import pyaudio
import sys
import numpy as np
import aubio

# initialise pyaudio
p = pyaudio.PyAudio()

# open stream
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 48000
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

if len(sys.argv) > 1:
    # record 5 seconds
    output_filename = sys.argv[1]
    record_duration = 5 # exit 1
    outputsink = aubio.sink(sys.argv[1], samplerate)
    total_frames = 0
else:
    # run forever
    outputsink = None
    record_duration = None

# setup pitch
tolerance = 0.9
win_s = 8192 # fft size
hop_s = buffer_size # hop size
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

print("*** starting recording")
while True:
    try:
        audiobuffer = stream.read(buffer_size)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        pitch = pitch_o(signal)[0]

        if pitch > 0:
         # print floor pitch
         pitch = int(round(pitch))

         # now we need to get musical notes based on pitch

         # C at 130Hz is 48
         # C# at 138.59Hz is 49
         # D at 146.83Hz is 50
         # D# at 155.56Hz is 51
         # E at 164.81Hz is 52
         # F at 174.61Hz is 53
         # F# at 185Hz is 54
         # G at 196Hz is 55
         # G# at 207.65Hz is 56
         # A at 220Hz is 57
         # A# at 233.08Hz is 58
         # B at 246.94Hz is 59
         # C at 261.63Hz is 60
         # C# at 277.18Hz is 61
         # D at 293.66Hz is 62
         # D# at 311.13Hz is 63

         # the lowest note we can play is E at around 82 Hz number 40

         # the highest note is number 86 so it is a D

         notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#",
                  "B"]

         # Calculate the octave and note
         octave = (pitch // 12) - 2  # Adjusted octave calculation
         note_index = pitch % 12
         note = notes[note_index]

         # Calculate the frequency
         frequency = 82.41 * (2 ** (note_index / 12)) * (2 ** octave)  # Use reference frequency of E2 (82.41 Hz)

         print("Aubio Pitch: {} / {} / {} / {}".format(pitch, note, octave, frequency))




        if outputsink:
            outputsink(signal, len(signal))

        if record_duration:
            total_frames += len(signal)
            if record_duration * samplerate < total_frames:
                break
    except KeyboardInterrupt:
        print("*** Ctrl+C pressed, exiting")
        break

print("*** done recording")
stream.stop_stream()
stream.close()
p.terminate()