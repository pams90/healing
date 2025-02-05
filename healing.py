# app.py
import numpy as np
import streamlit as st
from io import BytesIO
from scipy.io.wavfile import write

def generate_binaural_beat(base_freq, delta_freq, duration, amplitude=0.1, sr=44100):
    """Generate binaural beats audio signal"""
    t = np.linspace(0, duration, int(sr * duration))
    left = amplitude * np.sin(2 * np.pi * base_freq * t)
    right = amplitude * np.sin(2 * np.pi * (base_freq + delta_freq) * t)
    return np.column_stack((left, right))

def generate_isochronic(base_freq, beat_freq, duration, amplitude=0.3, sr=44100):
    """Generate isochronic tones audio signal"""
    t = np.linspace(0, duration, int(sr * duration))
    carrier = np.sin(2 * np.pi * base_freq * t)
    mod = (np.sin(2 * np.pi * beat_freq * t) > 0).astype(float)
    signal = amplitude * carrier * mod
    return np.column_stack((signal, signal))

def create_audio_file(signal, sr=44100):
    """Convert numpy array to WAV bytes"""
    audio_bytes = BytesIO()
    scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(audio_bytes, sr, scaled)
    return audio_bytes.getvalue()

# Preset configurations
PRESETS = {
    "Deep Meditation (7Hz)": {"type": "binaural", "base": 200, "delta": 7},
    "Relaxation (Alpha)": {"type": "binaural", "base": 300, "delta": 10},
    "Focus (Beta)": {"type": "isochronic", "base": 432, "beat": 15},
    "Deep Sleep (Delta)": {"type": "binaural", "base": 150, "delta": 4},
    "Custom": {"type": "custom"}
}

# Streamlit UI
st.title("🧘 Healing Frequency Generator")
st.markdown("Generate binaural beats and isochronic tones for meditation, focus, and relaxation")

with st.sidebar:
    st.header("Settings")
    preset = st.selectbox("Choose Preset", list(PRESETS.keys()))
    duration = st.slider("Duration (minutes)", 1, 60, 15)

# Convert minutes to seconds
duration_seconds = duration * 60

if PRESETS[preset]["type"] == "custom":
    with st.expander("Custom Settings"):
        col1, col2 = st.columns(2)
        with col1:
            freq_type = st.radio("Type", ["Binaural", "Isochronic"])
        with col2:
            base_freq = st.number_input("Base Frequency (Hz)", 50, 1000, 432)
            if freq_type == "Binaural":
                delta_freq = st.number_input("Delta Frequency (Hz)", 1, 30, 7)
            else:
                beat_freq = st.number_input("Beat Frequency (Hz)", 0.1, 40.0, 10.0)

if st.button("✨ Generate Audio"):
    if PRESETS[preset]["type"] != "custom":
        config = PRESETS[preset]
        if config["type"] == "binaural":
            signal = generate_binaural_beat(config["base"], config["delta"], duration_seconds)
        else:
            signal = generate_isochronic(config["base"], config["beat"], duration_seconds)
    else:
        if freq_type == "Binaural":
            signal = generate_binaural_beat(base_freq, delta_freq, duration_seconds)
        else:
            signal = generate_isochronic(base_freq, beat_freq, duration_seconds)
    
    # Generate and display audio
    audio_bytes = create_audio_file(signal)
    st.audio(audio_bytes, format="audio/wav")
    
    # Download button
    st.download_button(
        label="Download WAV File",
        data=audio_bytes,
        file_name=f"healing_frequency_{preset.replace(' ', '_')}.wav",
        mime="audio/wav"
    )
    
    st.success(f"Successfully generated {preset} frequency ({duration} minutes)")

st.markdown("---")
st.info("🔈 Use headphones for best results with binaural beats. Keep volume at comfortable levels.")
