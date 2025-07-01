import streamlit as st
import requests
import datetime
import sqlite3

# === Config ===
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def translate_to_english(text):
    # Optionally use a translation API or model
    return text  # Placeholder: assume input is English

def generate_excuse(prompt):
    translated = translate_to_english(prompt)
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Generate a creative and believable excuse in 1-2 lines."},
            {"role": "user", "content": translated}
        ],
        "temperature": 0.8
    }
    res = requests.post(API_URL, headers=HEADERS, json=payload)
    res.raise_for_status()
    return res.json()['choices'][0]['message']['content'].strip()

def init_db():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        excuse TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_history(prompt, excuse):
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (prompt, excuse, timestamp) VALUES (?, ?, ?)", (prompt, excuse, timestamp))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, excuse, timestamp FROM history ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows

# === Streamlit App ===
st.set_page_config(page_title="Rutwik's Official Excuse Generator AI")
st.title("🤖 Rutwik's Official Excuse Generator AI")

init_db()

with st.form("excuse_form"):
    user_input = st.text_area("🌍 Enter your situation (in any language):", height=100)
    submitted = st.form_submit_button("Generate Excuse")

if submitted and user_input:
    with st.spinner("Thinking hard for you..."):
        try:
            excuse = generate_excuse(user_input)
            log_history(user_input, excuse)
            st.success("✅ Here's your excuse:")
            st.write(excuse)
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.subheader("📜 Excuse History")
for prompt, excuse, timestamp in get_history():
    st.markdown(f"**🕒 {timestamp}**\n- ❓ Prompt: {prompt}\n- 💬 Excuse: {excuse}")
