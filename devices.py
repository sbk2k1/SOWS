# freeze input devices into a devices.txt using pyaudio

import pyaudio

p = pyaudio.PyAudio()

devices_list = []

for i in range(p.get_device_count()):
    # append only index and name if name contains "BEHRINGER" and has 2 channels
    if "BEHRINGER" in p.get_device_info_by_index(i)['name'] and p.get_device_info_by_index(i)['maxInputChannels'] == 2:
        devices_list.append([i, p.get_device_info_by_index(i)['name']])

with open('devices.txt', 'w') as f:
    for item in devices_list:
        f.write("%s\n" % item)