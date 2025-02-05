import numpy as np
import sounddevice as sd
import time

def generate_binaural_beat(base_freq, delta_freq, duration, amplitude=0.1, sr=44100):
    """Generate binaural beats"""
    t = np.linspace(0, duration, int(sr * duration))
    
    left = amplitude * np.sin(2 * np.pi * base_freq * t)
    right = amplitude * np.sin(2 * np.pi * (base_freq + delta_freq) * t)
    
    return np.column_stack((left, right))

def generate_isochronic(base_freq, beat_freq, duration, amplitude=0.3, sr=44100):
    """Generate isochronic tones"""
    t = np.linspace(0, duration, int(sr * duration))
    carrier = np.sin(2 * np.pi * base_freq * t)
    
    # Create amplitude modulation
    mod = (np.sin(2 * np.pi * beat_freq * t) > 0).astype(float)
    signal = amplitude * carrier * mod
    
    return np.column_stack((signal, signal))  # Stereo

# Common frequency combinations
presets = {
    "deep_meditation": {"type": "binaural", "base": 200, "delta": 7},
    "relaxation": {"type": "binaural", "base": 300, "delta": 10},
    "focus": {"type": "isochronic", "base": 432, "beat": 15},
    "sleep": {"type": "binaural", "base": 150, "delta": 4}
}

def play_frequency(preset_name, duration=60):
    config = presets.get(preset_name, presets["relaxation"])
    
    if config["type"] == "binaural":
        signal = generate_binaural_beat(config["base"], config["delta"], duration)
    else:
        signal = generate_isochronic(config["base"], config["beat"], duration)
    
    sd.play(signal, samplerate=44100)
    time.sleep(duration)
    sd.stop()

# Example usage
print("Available presets:", list(presets.keys()))
preset = input("Enter preset name: ")
duration = int(input("Enter duration in seconds: "))

play_frequency(preset.lower(), duration)
