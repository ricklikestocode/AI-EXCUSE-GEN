import streamlit as st
import pandas as pd
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
from gtts import gTTS
from io import BytesIO
from faker import Faker
from datetime import datetime
from deep_translator import GoogleTranslator
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from huggingface_hub import login

login("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")

st.set_page_config(page_title="Excuse Generator", layout="centered")
st.title("🎭 AI Excuse Generator")
fake = Faker()

for k in ["excuses", "apologies", "emergencies"]:
    if k not in st.session_state:
        st.session_state[k] = []

def speak(text, lang='en'):
    f = BytesIO()
    gTTS(text, lang=lang).write_to_fp(f)
    f.seek(0)
    return f

def pdf(text, title="Generated"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=LETTER)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, title)
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    for i, line in enumerate(text.splitlines()):
        c.drawString(50, 700 - i*20, line)
    c.save()
    return tmp.name

def clean(t, f):
    banned = ["suicide", "murder", "sex", "alcohol", "drugs"]
    return not any(x in t.lower() for x in banned) if f else True

@st.cache_resource
def load():
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    def make_pipeline(model_name):
        return pipeline(
            "text-generation",
            model=GPT2LMHeadModel.from_pretrained(model_name),
            tokenizer=tokenizer
        )

    return (
        make_pipeline("rutwikvadali/gpt2-finetuned-excuses"),
        make_pipeline("rutwikvadali/gpt2-finetuned-apologies"),
        make_pipeline("rutwikvadali/gpt2-finetuned-emergency"),
    )

e_gen, a_gen, em_gen = load()

p_lock = st.sidebar.checkbox("Parental Filter", value=True)
mode = st.selectbox("Mode", ["Excuse", "Apology", "Emergency"])
langs = {"English": "en", "Hindi": "hi", "French": "fr", "Spanish": "es"}
lang = st.selectbox("Language", list(langs.keys()))
code = langs[lang]

def gen(prompt, generator):
    result = generator(prompt, max_length=50, do_sample=True, top_k=50, top_p=0.95)[0]["generated_text"]
    text = result[len(prompt):].strip().split(".")[0] + "."
    return text

def safe_display(t):
    if not t or any(c in t for c in "|{}[]#@"):
        st.error("⚠️ Sorry, that didn't work. Try again.")
        return False
    return True

if mode == "Excuse":
    sc = st.text_input("Scenario | Urgency | Believability", "work | high | high")
    rs = st.text_input("Reason", "Late to school")
    if st.button("Generate"):
        prompt = f"Excuse: {rs}. Scenario: {sc}."
        text = gen(prompt, e_gen)
        if clean(text, p_lock) and safe_display(text):
            out = GoogleTranslator(source="auto", target=code).translate(text) if code != "en" else text
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(text, "Excuse"), "rb") as f:
                st.download_button("Download PDF", f, "excuse.pdf")
            st.session_state.excuses.append({"time": datetime.now(), "text": text})

elif mode == "Apology":
    style = st.selectbox("Type", ["emotional", "professional"])
    if st.button("Generate"):
        prompt = f"{style} apology:"
        text = gen(prompt, a_gen)
        if clean(text, p_lock) and safe_display(text):
            out = GoogleTranslator(source="auto", target=code).translate(text) if code != "en" else text
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(text, "Apology"), "rb") as f:
                st.download_button("Download PDF", f, "apology.pdf")
            st.session_state.apologies.append({"time": datetime.now(), "text": text})

elif mode == "Emergency":
    kind = st.selectbox("Type", ["work", "family", "school"])
    if st.button("Generate"):
        prompt = f"{kind} emergency:"
        text = gen(prompt, em_gen)
        if clean(text, p_lock) and safe_display(text):
            out = GoogleTranslator(source="auto", target=code).translate(text) if code != "en" else text
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(text, "Emergency"), "rb") as f:
                st.download_button("Download PDF", f, "emergency.pdf")
            st.session_state.emergencies.append({"time": datetime.now(), "text": text})
