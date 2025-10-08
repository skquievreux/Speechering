#!/usr/bin/env python3
"""
Generiert kleine Test-Audio-Dateien für Unit-Tests.
Erstellt synthetische WAV-Dateien mit verschiedenen Eigenschaften.
"""

import math
import wave
from pathlib import Path

import numpy as np


def generate_sine_wave(frequency, duration, sample_rate=16000, amplitude=0.5):
    """Generiert eine Sinuswelle"""
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return (wave_data * 32767).astype(np.int16)

def generate_test_audio_files():
    """Generiert verschiedene Test-Audio-Dateien"""

    output_dir = Path(__file__).parent / "audio"
    output_dir.mkdir(exist_ok=True)

    sample_rate = 16000

    # Test 1: Stille (1 Sekunde)
    silent_samples = np.zeros(sample_rate, dtype=np.int16)
    with wave.open(str(output_dir / "silent_1s.wav"), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(silent_samples.tobytes())
    print("✓ Erstellt: silent_1s.wav")

    # Test 2: Ton (440Hz, 1 Sekunde)
    tone_samples = generate_sine_wave(440, 1.0, sample_rate)
    with wave.open(str(output_dir / "tone_440hz_1s.wav"), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(tone_samples.tobytes())
    print("✓ Erstellt: tone_440hz_1s.wav")

    # Test 3: Sprach-ähnlicher Ton (mehrere Frequenzen, 2 Sekunden)
    speech_samples = np.array([], dtype=np.int16)
    frequencies = [300, 800, 1200, 2000, 2500]

    for freq in frequencies:
        tone = generate_sine_wave(freq, 0.4, sample_rate, 0.3)  # 400ms, leisere Amplitude
        speech_samples = np.concatenate([speech_samples, tone])

    with wave.open(str(output_dir / "speech_like_2s.wav"), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(speech_samples.tobytes())
    print("✓ Erstellt: speech_like_2s.wav")

    # Test 4: Langer Ton für Komprimierungstest (5 Sekunden)
    long_tone_samples = generate_sine_wave(1000, 5.0, sample_rate)
    with wave.open(str(output_dir / "long_tone_5s.wav"), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(long_tone_samples.tobytes())
    print("✓ Erstellt: long_tone_5s.wav")

    # Test 5: Weißes Rauschen (1 Sekunde) - für Robustheitstests
    noise_samples = np.random.normal(0, 0.1, sample_rate)
    noise_samples = np.clip(noise_samples, -1, 1)
    noise_samples = (noise_samples * 32767).astype(np.int16)

    with wave.open(str(output_dir / "noise_1s.wav"), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(noise_samples.tobytes())
    print("✓ Erstellt: noise_1s.wav")

    print(f"\nAlle Test-Audio-Dateien erstellt in: {output_dir}")
    print("Dateigrößen:")
    for wav_file in output_dir.glob("*.wav"):
        size_kb = wav_file.stat().st_size / 1024
        print(".1f")

if __name__ == "__main__":
    generate_test_audio_files()