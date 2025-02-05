# app.py
import numpy as np
import streamlit as st
from io import BytesIO
from scipy.io.wavfile import write

# --- Configuration ---
APP_VERSION = "1.2.0"
SAMPLE_RATE = 44100
MAX_DURATION_MINUTES = 120

# --- Cache Busting Initialization ---
st.experimental_singleton.clear()
st.experimental_memo.clear()

try:
    # --- Audio Generation Functions ---
    def generate_choir(duration, base_freq=220.0, amplitude=0.2):
        """Generate angelic choir-like sound using additive synthesis"""
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        
        # Create multiple voice layers
        voices = []
        for i in range(8):  # Number of harmonic voices
            freq = base_freq * (i + 1) * 0.5
            detune = 1 + (np.random.rand() * 0.02 - 0.01)  # Slight detuning
            vib_depth = 0.5 + i*0.1  # Vibrato depth
            vib_rate = 5 + i*0.5  # Vibrato rate
            
            # Add vibrato and amplitude envelope
            vib = np.sin(2 * np.pi * vib_rate * t) * vib_depth
            env = np.linspace(0.8, 0.2, len(t))  # Decaying envelope
            
            voice = (amplitude * 0.5 * env * 
                    (np.sin(2 * np.pi * (freq * detune + vib) * t) +
                     0.3 * np.sin(2 * np.pi * 2 * (freq * detune + vib) * t) +
                     0.1 * np.sin(2 * np.pi * 3 * (freq * detune + vib) * t)))
            
            voices.append(voice)
        
        # Mix voices and create stereo effect
        signal = np.sum(voices, axis=0)
        return np.column_stack((signal * 0.8, signal * 0.8))  # Wide stereo

    # Modified presets
    PRESETS = {
        "Angelic Choir (A=220Hz)": {"type": "choir", "base": 220},
        "Celestial Harmonics (A=440Hz)": {"type": "choir", "base": 440},
        "Deep Meditation (7Hz Theta)": {"type": "binaural", "base": 200, "delta": 7},
        "Relaxation (10Hz Alpha)": {"type": "binaural", "base": 300, "delta": 10},
        "Focus (15Hz Beta)": {"type": "isochronic", "base": 432, "beat": 15},
        "Deep Sleep (4Hz Delta)": {"type": "binaural", "base": 150, "delta": 4},
        "Custom Configuration": {"type": "custom"}
    }

    # --- Existing Functions Remain Unchanged ---
    # (Keep previous generate_binaural_beat, generate_isochronic, create_audio_file functions)

    # --- Modified UI Section ---
    with st.sidebar:
        st.header("⚙️ Settings")
        preset = st.selectbox("Choose Preset", list(PRESETS.keys()))
        duration = st.slider("Duration (minutes)", 1, MAX_DURATION_MINUTES, 15)

    duration_seconds = min(duration * 60, MAX_DURATION_MINUTES * 60)

    # Modified Custom Settings
    custom_config = {}
    if PRESETS[preset]["type"] == "custom":
        with st.expander("🔧 Custom Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                custom_config["type"] = st.radio("Sound Type", 
                    ["Binaural", "Isochronic", "Choir"])
            with col2:
                if custom_config["type"] == "Choir":
                    custom_config["base"] = st.number_input("Base Frequency (Hz)", 
                        110, 880, 220)
                    custom_config["vibrato"] = st.slider("Vibrato Depth", 0.1, 2.0, 0.8)
                else:
                    custom_config["base"] = st.number_input("Base Frequency (Hz)", 
                        50, 1000, 432)
                    if custom_config["type"] == "Binaural":
                        custom_config["delta"] = st.number_input("Delta Frequency (Hz)", 
                            1, 30, 7)
                    else:
                        custom_config["beat"] = st.number_input("Beat Frequency (Hz)", 
                            0.1, 40.0, 10.0)

    # Modified Generation Section
    if st.button("✨ Generate Audio", type="primary"):
        with st.spinner(f"Generating {duration} minute audio..."):
            try:
                if PRESETS[preset]["type"] != "custom":
                    config = PRESETS[preset]
                else:
                    config = custom_config

                # Add choir generation
                if config["type"].lower() == "choir":
                    base_freq = config.get("base", 220)
                    signal = generate_choir(duration_seconds, base_freq=base_freq)
                elif config["type"].lower() == "binaural":
                    signal = generate_binaural_beat(
                        config["base"], config.get("delta", 7), duration_seconds)
                else:
                    signal = generate_isochronic(
                        config["base"], config.get("beat", 10), duration_seconds)

                # Rest of audio handling remains the same
                audio_bytes = create_audio_file(signal)
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    label="⬇️ Download WAV File",
                    data=audio_bytes,
                    file_name=f"healing_{preset.replace(' ', '_')}.wav",
                    mime="audio/wav"
                )
                st.success(f"✅ Successfully generated {preset} ({duration} minutes)")

            except Exception as e:
                st.error(f"🚨 Generation failed: {str(e)}")

    # --- Rest of the code remains unchanged ---

except Exception as e:
    # Error handling code remains unchanged
