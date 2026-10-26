import streamlit as st
from pathlib import Path

st.title("👋 My Bio")

# ---------- About me ----------
NAME = "Lifu Deng"
PROGRAM = "Data Science and Machine Learning | Minor in Computer Security"
INTRO = (
    "I’m studying data science and machine learning, with a minor in computer security. "
    "I’m interested in data visualization because it helps me present data clearly "
    "so audiences and clients can understand it and use it for its intended purpose."
)
FUN_FACTS = [
    "I enjoy cooking Asian, European, and North American food—from Cantonese and Sichuan dishes to Italian pasta and Mexican favorites.",
    "I try to make time for golf and hiking when I need a digital detox.",
    "I’m fascinated by AI and hope to build my own small AI system that runs smoothly on the hardware I already have.",
]


PHOTO_PATH = "lifu_deng.jpeg"  # Stored in streamlit_DSML/assets/


def find_photo(filename=PHOTO_PATH):
    # Try common locations for multipage apps
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()

    candidates = [
        script_dir / "assets" / filename,          # pages/assets/...
        script_dir.parent / "assets" / filename,   # root/assets/... (common)
        Path("assets") / filename,                 # cwd/assets/...
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

photo_src = find_photo(PHOTO_PATH)

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    if photo_src:
        st.image(photo_src, caption=NAME, use_container_width=True)
    else:
        st.info(
            "📷 Place `Your_Photo.jpg` inside an `assets/` folder at the app root "
            "or update the path in `find_photo()`."
        )
        
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("AI assistance was used for guided learning and coding support.")
