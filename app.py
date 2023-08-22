import pyaudio
import wave
import numpy as np
import aubio  # Add this import for aubio
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

DETECTION_THRESHOLD = 8
DETECTION_WINDOW = 5

p = pyaudio.PyAudio()

# Use device number 2
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input_device_index=23,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize Aubio pitch detection
tolerance = 0.8
win_s = 4096
hop_s = CHUNK
samplerate = RATE
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

print("* recording")

frames = []
chunk_queue = []

# start an interval every 0.1s calling get_pitch

while True:
    try:
        chunk = stream.read(CHUNK)
        amplitude = np.max(np.abs(np.frombuffer(chunk, dtype=np.int16)))
        chunk_queue.append(amplitude)
        if len(chunk_queue) > DETECTION_WINDOW:
            chunk_queue.pop(0)
        if all(i > DETECTION_THRESHOLD for i in chunk_queue):
            # Use Aubio pitch detection
            signal = np.frombuffer(chunk, dtype=np.float32).astype(np.float32) / 32768.0
            pitch = pitch_o(signal)[0]
            confidence = pitch_o.get_confidence()

            print("Aubio Pitch: {} / Confidence: {}".format(pitch, confidence))


    except KeyboardInterrupt:
        print("* Ctrl+C pressed, exiting")
        break

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
