import pyaudio
import wave
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

DETECTION_THRESHOLD = 8  # Adjust this threshold based on your input signal
DETECTION_WINDOW = 5  # Number of consecutive chunks for detection

p = pyaudio.PyAudio()

# use device number 2

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input_device_index=23,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
chunk_queue = []

while(True):
    # signal is only detected if it is above the threshold for all samples for DETECTION_WINDOW chunks
    
    # get chunks
    chunk = stream.read(CHUNK)
    amplitude = np.max(np.abs(np.frombuffer(chunk, dtype=np.int16)))
    print(amplitude)
    chunk_queue.append(amplitude)
    if(len(chunk_queue) > DETECTION_WINDOW):
        chunk_queue.pop(0)
    if all(i > DETECTION_THRESHOLD for i in chunk_queue):
        print("Note detected")
    

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
