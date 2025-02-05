import numpy as np
import streamlit as st
from io import BytesIO
from scipy.io.wavfile import write

SAMPLE_RATE = 44100
MAX_DURATION_MINUTES = 120

def generate_signal(signal_type, base_freq, secondary_freq, duration, amplitude=0.1):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    if signal_type == "binaural":
        left = amplitude * np.sin(2 * np.pi * base_freq * t)
        right = amplitude * np.sin(2 * np.pi * (base_freq + secondary_freq) * t)
        return np.column_stack((left, right))
    elif signal_type == "isochronic":
        carrier = np.sin(2 * np.pi * base_freq * t)
        mod = (np.sin(2 * np.pi * secondary_freq * t) > 0).astype(float)
        signal = amplitude * carrier * mod
        return np.column_stack((signal, signal))
    elif signal_type == "choir":
        voices = []
        for i in range(8):
            freq = base_freq * (i + 1) * 0.5
            detune = 1 + (np.random.rand() * 0.02 - 0.01)
            vib_depth = 0.5 + i * 0.1
            vib_rate = 5 + i * 0.5
            vib = np.sin(2 * np.pi * vib_rate * t) * vib_depth
            env = np.linspace(0.8, 0.2, len(t))
            voice = (amplitude * 0.5 * env * 
                    (np.sin(2 * np.pi * (freq * detune + vib) * t) +
                     0.3 * np.sin(2 * np.pi * 2 * (freq * detune + vib) * t) +
                     0.1 * np.sin(2 * np.pi * 3 * (freq * detune + vib) * t)))
            voices.append(voice)
        signal = np.sum(voices, axis=0)
        return np.column_stack((signal * 0.8, signal * 0.8))

def create_audio_file(signal):
    audio_bytes = BytesIO()
    scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(audio_bytes, SAMPLE_RATE, scaled)
    return audio_bytes.getvalue()

PRESETS = {
    "Angelic Choir (A=220Hz)": {"type": "choir", "base": 220},
    "Celestial Harmonics (A=440Hz)": {"type": "choir", "base": 440},
    "Deep Meditation (7Hz Theta)": {"type": "binaural", "base": 200, "delta": 7},
    "Relaxation (10Hz Alpha)": {"type": "binaural", "base": 300, "delta": 10},
    "Focus (15Hz Beta)": {"type": "isochronic", "base": 432, "beat": 15},
    "Deep Sleep (4Hz Delta)": {"type": "binaural", "base": 150, "delta": 4},
    "Custom Configuration": {"type": "custom"}
}

st.set_page_config(page_title="Healing Frequency Generator", page_icon="🎵", layout="centered")
st.title("🎵 Healing Frequency Generator")
st.markdown("Generate therapeutic sounds including Binaural Beats, Isochronic Tones, Angelic Choirs, and Sleep Assistance")

with st.sidebar:
    st.header("⚙️ Settings")
    preset = st.selectbox("Choose Preset", list(PRESETS.keys()))
    duration = st.slider("Duration (minutes)", 1, MAX_DURATION_MINUTES, 15)

duration_seconds = min(duration * 60, MAX_DURATION_MINUTES * 60)

if PRESETS[preset]["type"] == "custom":
    with st.expander("🔧 Custom Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            custom_type = st.radio("Sound Type", ["Binaural", "Isochronic", "Choir"])
        with col2:
            base_freq = st.number_input("Base Frequency (Hz)", 50, 1000, 432 if custom_type != "Choir" else 220)
            if custom_type == "Binaural":
                delta_freq = st.number_input("Delta Frequency (Hz)", 1, 30, 7)
            elif custom_type == "Isochronic":
                beat_freq = st.number_input("Beat Frequency (Hz)", 0.1, 40.0, 10.0)

if st.button("✨ Generate Audio"):
    with st.spinner(f"Generating {duration} minute audio..."):
        try:
            config = PRESETS[preset] if PRESETS[preset]["type"] != "custom" else {"type": custom_type, "base": base_freq}
            signal_type = config["type"]
            if signal_type == "choir":
                signal = generate_signal(signal_type, config["base"], None, duration_seconds)
            else:
                secondary_freq = config.get("delta") or config.get("beat")
                signal = generate_signal(signal_type, config["base"], secondary_freq, duration_seconds)
            audio_bytes = create_audio_file(signal)
            st.audio(audio_bytes, format="audio/wav")
            st.download_button(label="⬇️ Download WAV File", data=audio_bytes, file_name=f"healing_{preset.replace(' ', '_')}.wav", mime="audio/wav")
            st.success(f"✅ Successfully generated {preset} ({duration} minutes)")
        except Exception as e:
            st.error(f"🚨 Generation failed: {str(e)}")

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
