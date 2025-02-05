# app.py
import numpy as np
import streamlit as st
from io import BytesIO
from scipy.io.wavfile import write

# --- Configuration ---
APP_VERSION = "1.2.1"
SAMPLE_RATE = 44100
MAX_DURATION_MINUTES = 120

# --- Cache Busting Initialization ---
st.experimental_singleton.clear()
st.experimental_memo.clear()

try:
    # --- Audio Generation Functions ---
    def generate_binaural_beat(base_freq, delta_freq, duration, amplitude=0.1):
        """Generate binaural beats audio signal"""
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        left = amplitude * np.sin(2 * np.pi * base_freq * t)
        right = amplitude * np.sin(2 * np.pi * (base_freq + delta_freq) * t)
        return np.column_stack((left, right))

    def generate_isochronic(base_freq, beat_freq, duration, amplitude=0.3):
        """Generate isochronic tones audio signal"""
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        carrier = np.sin(2 * np.pi * base_freq * t)
        mod = (np.sin(2 * np.pi * beat_freq * t) > 0).astype(float)
        signal = amplitude * carrier * mod
        return np.column_stack((signal, signal))

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

    def create_audio_file(signal):
        """Convert numpy array to WAV bytes"""
        audio_bytes = BytesIO()
        scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
        write(audio_bytes, SAMPLE_RATE, scaled)
        return audio_bytes.getvalue()

    # --- Preset Configurations ---
    PRESETS = {
        "Angelic Choir (A=220Hz)": {"type": "choir", "base": 220},
        "Celestial Harmonics (A=440Hz)": {"type": "choir", "base": 440},
        "Deep Meditation (7Hz Theta)": {"type": "binaural", "base": 200, "delta": 7},
        "Relaxation (10Hz Alpha)": {"type": "binaural", "base": 300, "delta": 10},
        "Focus (15Hz Beta)": {"type": "isochronic", "base": 432, "beat": 15},
        "Deep Sleep (4Hz Delta)": {"type": "binaural", "base": 150, "delta": 4},
        "Custom Configuration": {"type": "custom"}
    }

    # --- Streamlit UI ---
    st.set_page_config(
        page_title="Healing Frequency Generator",
        page_icon="🎵",
        layout="centered"
    )

    # Header Section
    st.title("🎵 Healing Frequency Generator")
    st.markdown("""
        Generate therapeutic sounds including:
        - 🧘 Binaural Beats
        - 🎯 Isochronic Tones
        - 👼 Angelic Choirs
        - 💤 Sleep Assistance
    """)

    with st.sidebar:
        st.header("⚙️ Settings")
        preset = st.selectbox("Choose Preset", list(PRESETS.keys()))
        duration = st.slider("Duration (minutes)", 1, MAX_DURATION_MINUTES, 15)

    # Convert minutes to seconds with safety check
    duration_seconds = min(duration * 60, MAX_DURATION_MINUTES * 60)

    # Custom Settings
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
                else:
                    custom_config["base"] = st.number_input("Base Frequency (Hz)", 
                        50, 1000, 432)
                    if custom_config["type"] == "Binaural":
                        custom_config["delta"] = st.number_input("Delta Frequency (Hz)", 
                            1, 30, 7)
                    else:
                        custom_config["beat"] = st.number_input("Beat Frequency (Hz)", 
                            0.1, 40.0, 10.0)

    # Generation Section
    if st.button("✨ Generate Audio", type="primary"):
        with st.spinner(f"Generating {duration} minute audio..."):
            try:
                # Select configuration
                if PRESETS[preset]["type"] != "custom":
                    config = PRESETS[preset]
                else:
                    config = custom_config

                # Generate audio
                if config["type"].lower() == "choir":
                    signal = generate_choir(duration_seconds, base_freq=config.get("base", 220))
                elif config["type"].lower() == "binaural":
                    signal = generate_binaural_beat(
                        config["base"], config.get("delta", 7), duration_seconds)
                else:
                    signal = generate_isochronic(
                        config["base"], config.get("beat", 10), duration_seconds)

                # Create and display audio
                audio_bytes = create_audio_file(signal)
                st.audio(audio_bytes, format="audio/wav")

                # Download button
                st.download_button(
                    label="⬇️ Download WAV File",
                    data=audio_bytes,
                    file_name=f"healing_{preset.replace(' ', '_')}.wav",
                    mime="audio/wav"
                )

                st.success(f"✅ Successfully generated {preset} ({duration} minutes)")

            except Exception as e:
                st.error(f"🚨 Generation failed: {str(e)}")

    # --- Information Section ---
    st.markdown("---")
    with st.expander("ℹ️ Usage Instructions"):
        st.markdown("""
        **How to use:**
        1. Select a preset from the sidebar
        2. Adjust duration (1-120 minutes)
        3. Click "Generate Audio"
        4. Play directly or download the WAV file

        **Recommendations:**
        - Use headphones for spatial effects
        - Start with 15-30 minute sessions
        - Keep volume at comfortable levels
        - Combine with meditation practices
        """)

    st.markdown("---")
    st.caption(f"✨ App version {APP_VERSION} | ⚠️ Not a medical treatment")

except Exception as e:  # Properly indented error handler
    # Global Error Handling
    st.error(f"""
    🚨 Critical Application Error
    {str(e)}
    
    The page will automatically reload...
    """)
    
    # Auto-reload script with version cache busting
    st.markdown(f"""
    <script>
    setTimeout(function(){{
        window.location.href = window.location.href.split('?')[0] + '?v={APP_VERSION}';
    }}, 3000);
    </script>
    """, unsafe_allow_html=True)
