# PyAudio Documentation - Audio Recording and Playback

## Overview

PyAudio provides Python bindings for PortAudio, enabling cross-platform audio
recording and playback on Windows, macOS, and Linux.

## Installation

### Windows

```bash
pip install pyaudio
```

Includes precompiled PortAudio v19.7.0 with support for:

- Windows MME API
- DirectSound
- WASAPI
- WDM-KS

### macOS

```bash
brew install portaudio
pip install pyaudio
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install python3-pyaudio
```

## Basic Usage

### Initialization

```python
import pyaudio

# Create PyAudio instance
audio = pyaudio.PyAudio()

# Get device info
device_count = audio.get_device_count()
for i in range(device_count):
    device_info = audio.get_device_info_by_index(i)
    print(f"Device {i}: {device_info['name']}")
    print(f"  Input channels: {device_info['maxInputChannels']}")
    print(f"  Output channels: {device_info['maxOutputChannels']}")
```

### Audio Recording (Blocking Mode)

```python
import wave

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5

# Open stream
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Recording...")

frames = []

# Record audio
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording finished")

# Stop and close stream
stream.stop_stream()
stream.close()

# Save to WAV file
with wave.open('output.wav', 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

audio.terminate()
```

### Audio Recording (Callback Mode)

```python
def callback(in_data, frame_count, time_info, status):
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)

# Open stream with callback
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

frames = []
stream.start_stream()

# Wait for recording to finish
while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
audio.terminate()
```

### Audio Playback

```python
# Open WAV file
with wave.open('input.wav', 'rb') as wf:
    # Open output stream
    stream = audio.open(
        format=audio.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    # Read and play data
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

audio.terminate()
```

## Stream Parameters

### Format Constants

- `pyaudio.paInt8` - 8-bit signed integer
- `pyaudio.paInt16` - 16-bit signed integer
- `pyaudio.paInt24` - 24-bit signed integer
- `pyaudio.paInt32` - 32-bit signed integer
- `pyaudio.paFloat32` - 32-bit float

### Common Settings for Voice Recording

```python
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1              # Mono
RATE = 16000              # 16kHz sample rate
CHUNK = 1024              # Buffer size
```

## Device Management

### List Input Devices

```python
for i in range(audio.get_device_count()):
    device_info = audio.get_device_info_by_index(i)
    if device_info['maxInputChannels'] > 0:
        print(f"Input Device {i}: {device_info['name']}")
```

### Specify Input Device

```python
# Use specific input device
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=device_index,  # Specify device
    frames_per_buffer=CHUNK
)
```

## Error Handling

### Common Exceptions

```python
try:
    stream = audio.open(...)
except OSError as e:
    if e.errno == -9999:
        print("Invalid sample rate")
    elif e.errno == -9997:
        print("Invalid device")
    else:
        print(f"Audio error: {e}")
```

### Check Device Availability

```python
device_info = audio.get_device_info_by_index(device_index)
if device_info['maxInputChannels'] == 0:
    print("Selected device has no input channels")
```

## Best Practices

### Resource Management

```python
audio = pyaudio.PyAudio()
try:
    # Use audio
    stream = audio.open(...)
    # ... use stream ...
finally:
    if 'stream' in locals():
        stream.stop_stream()
        stream.close()
    audio.terminate()
```

### Buffer Size Considerations

- Smaller chunks: Lower latency, more CPU usage
- Larger chunks: Higher latency, less CPU usage
- Typical values: 512, 1024, 2048, 4096

### Sample Rate Selection

- Voice recording: 8000-16000 Hz
- Music recording: 44100-48000 Hz
- Higher rates require more storage and processing

## Platform-Specific Notes

### Windows

- WASAPI support for low-latency audio
- Multiple audio APIs available
- Good device enumeration support

### macOS

- CoreAudio integration
- Good performance with proper buffer sizes
- May require microphone permissions

### Linux

- ALSA/PulseAudio support
- May need additional system packages
- Device enumeration varies by distribution

## Troubleshooting

### "Invalid sample rate" Error

- Check if device supports the requested sample rate
- Try common rates: 8000, 16000, 22050, 44100, 48000

### No Audio Input

- Check microphone permissions
- Verify correct device index
- Test with different audio applications

### Buffer Overrun/Underrun

- Adjust chunk size
- Check CPU usage
- Consider callback mode for better performance

### Device Not Found

- List available devices first
- Check device indices
- Try different audio APIs (on Windows)
