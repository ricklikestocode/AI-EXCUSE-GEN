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

st.set_page_config(page_title="Excuse Generator", layout="centered")
st.title("🎭 AI Excuse Generator")
fake = Faker()

for k in ["excuses", "apologies", "emergencies", "feedback"]:
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
    c.drawString(50, 730, datetime.now().strftime('%d/%m/%Y'))
    for i, line in enumerate(text.splitlines()):
        c.drawString(50, 700 - i*20, line)
    c.save()
    return tmp.name

def clean(t, f):
    b = ["suicide", "murder", "sex", "alcohol", "drugs"]
    return not any(x in t.lower() for x in b) if f else True

@st.cache_resource
def load():
    tok = GPT2Tokenizer.from_pretrained("gpt2")
    tok.pad_token = tok.eos_token
    g = lambda n: pipeline("text-generation", model=GPT2LMHeadModel.from_pretrained(n), tokenizer=tok)
    return g("rutwikvadali/gpt2-finetuned-excuses"), g("rutwikvadali/gpt2-finetuned-apologies"), g("rutwikvadali/gpt2-finetuned-emergency")

e_gen, a_gen, em_gen = load()

p_lock = st.sidebar.checkbox("Parental Filter", value=True)
mode = st.selectbox("Mode", ["Excuse", "Apology", "Emergency"])
langs = {"English": "en", "Hindi": "hi", "French": "fr", "Spanish": "es"}
lang = st.selectbox("Language", list(langs.keys()))
code = langs[lang]

def gen(p, g):
    o = g(p, max_length=40)[0]['generated_text']
    return o[len(p):].split('.')[0] + '.'

if mode == "Excuse":
    sc = st.text_input("Scenario | Urgency | Believability", "work | high | high")
    rs = st.text_input("Reason", "Late submission")
    if st.button("Generate"):
        p = f"{sc} :"
        t = gen(p, e_gen)
        if not clean(t, p_lock):
            st.error("🚫 Blocked")
        else:
            out = GoogleTranslator(source='auto', target=code).translate(t) if code != 'en' else t
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(t, "Excuse"), "rb") as f:
                st.download_button("Download PDF", f, "excuse.pdf")
            st.session_state.excuses.append({"time": datetime.now(), "text": t})

elif mode == "Apology":
    style = st.selectbox("Type", ["emotional", "professional"])
    if st.button("Generate"):
        t = gen(f"{style} :", a_gen)
        if not clean(t, p_lock):
            st.error("🚫 Blocked")
        else:
            out = GoogleTranslator(source='auto', target=code).translate(t) if code != 'en' else t
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(t, "Apology"), "rb") as f:
                st.download_button("Download PDF", f, "apology.pdf")
            st.session_state.apologies.append({"time": datetime.now(), "text": t})

elif mode == "Emergency":
    s = st.selectbox("Type", ["work", "family", "school"])
    if st.button("Generate"):
        t = gen(f"{s} :", em_gen)
        if not clean(t, p_lock):
            st.error("🚫 Blocked")
        else:
            out = GoogleTranslator(source='auto', target=code).translate(t) if code != 'en' else t
            st.success(out)
            st.audio(speak(out, code))
            with open(pdf(t, "Emergency"), "rb") as f:
                st.download_button("Download PDF", f, "emergency.pdf")
            st.session_state.emergencies.append({"time": datetime.now(), "text": t})
