import streamlit as st
import requests
import json
import time
from datetime import datetime
import os

# 1. Daten laden
def load_courses():
    try:
        with open('kurse_datenbank.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

kurs_daten = load_courses()

# --- DATEN STRUKTURIEREN ---
sportarten_dict = {}
for k in kurs_daten:
    sport = k['sport']
    if sport not in sportarten_dict:
        sportarten_dict[sport] = []
    sportarten_dict[sport].append(k)

alle_sportarten = sorted(sportarten_dict.keys())

# --- LOGIK: Die Sende-Funktion ---
def send_request(user_data):
    url = "https://anmeldung.hochschulsport-koeln.de/inc/methods.php"
    payload = {
        'state': 'studentAnmelden',
        'type': user_data['status'],
        'offerCourseID': user_data['course_id'],
        'vorname': user_data['vorname'],
        'nachname': user_data['nachname'],
        'telefon': user_data['telefon'],
        'matrikel': user_data['matrikel'] if user_data['matrikel'] else '000000',
        'email': user_data['email'],
        'hochschulen': user_data['hochschule'] if user_data['hochschule'] else '0',
        'hochschulenextern': 'null',
        'office': 'null'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://anmeldung.hochschulsport-koeln.de/'
    }
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        return response
    except Exception as e:
        return 500, str(e)

# --- UI SETTINGS ---
st.set_page_config(page_title="HSP Köln Master-Bot", layout="wide")
st.title("🏆 HSP Köln - Anmeldung v2.0")

if 'users' not in st.session_state:
    st.session_state.users = []

# --- SIDEBAR: NUTZER & KURS ---
with st.sidebar:
    st.header("👤 Nutzer & Kurs hinzufügen")
    
    # Hierarchische Auswahl (NICHT im Form, damit es sich sofort aktualisiert)
    selected_sport = st.selectbox("1. Sportart wählen", ["Bitte wählen..."] + alle_sportarten)
    
    kurs_options_gefiltert = []
    if selected_sport != "Bitte wählen...":
        kurs_options_gefiltert = [f"{k['name']} (Zeit: {k['tag']} {k['zeit']} ID: {k['id']})" for k in sportarten_dict[selected_sport]]
    
    selected_details = st.selectbox("2. Kurs/Zeit wählen", kurs_options_gefiltert)

    with st.form("user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        vorname = col1.text_input("Vorname")
        nachname = col2.text_input("Nachname")
        email = st.text_input("E-Mail")
        telefon = st.text_input("Telefon")
        status = st.selectbox("Status", ["student", "extern", "mitarbeiter"])
        matrikel = st.text_input("Matrikelnummer")
        hochschule = st.text_input("Hochschule (ID)")
        
        if st.form_submit_button("➕ Nutzer hinzufügen"):
            if selected_sport == "Bitte wählen..." or not selected_details:
                st.error("Bitte Sportart und Kurs wählen!")
            else:
                c_id = selected_details.split("ID: ")[-1].replace(")", "").strip()
                print(c_id)
                st.session_state.users.append({
                    "vorname": vorname, "nachname": nachname, "email": email,
                    "telefon": telefon, "status": status, "matrikel": matrikel, 
                    "hochschule": hochschule, "course_id": c_id, 
                    "course_name": f"{selected_sport}: {selected_details}"
                })
                st.rerun()

    st.divider()
    st.header("💾 Daten-Management")
    if st.button("📥 Liste speichern"):
        with open('nutzer_vorlage.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.users, f, indent=4)
        st.success("Gespeichert in nutzer_vorlage.json")
    
    if st.button("📤 Liste laden"):
        if os.path.exists('nutzer_vorlage.json'):
            with open('nutzer_vorlage.json', 'r', encoding='utf-8') as f:
                st.session_state.users = json.load(f)
            st.success("Liste erfolgreich geladen!")
            st.rerun()
        else:
            st.error("Keine Vorlage gefunden!")

# --- HAUPTBEREICH: WARTESCHLANGE ---
st.subheader("📋 Warteschlange für Montag")
if st.session_state.users:
    st.table(st.session_state.users)
    
    if st.button("🗑️ Liste komplett löschen"):
        st.session_state.users = []
        st.rerun()

    st.divider()
    col_t1, col_t2 = st.columns(2)
    target_date = col_t1.date_input("Tag", value=datetime.now())
    target_time_str = col_t2.text_input("Uhrzeit", value="15:00:00")

    # Buttons zum Starten
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        if st.button("⏰ GEPLANTE ANMELDUNG", type="primary", use_container_width=True):
            target_dt = datetime.strptime(f"{target_date} {target_time_str}", "%Y-%m-%d %H:%M:%S")
            status_box = st.empty()
            while datetime.now() < target_dt:
                diff = target_dt - datetime.now()
                status_box.warning(f"⏳ Countdown: {str(diff).split('.')[0]}")
                time.sleep(0.1)
            
            status_box.success("🔥 Feuer frei!")
            for user in st.session_state.users:
                response = send_request(user)
                if response.status_code == 200 and "Error" not in response.text:
                    st.success(f"✅ {user['vorname']} angemeldet!  {response.text}")
                    st.info(response)
                else:
                    st.error(f"❌ {user['vorname']} fehlgeschlagen: {response.text}")
                    st.info(response)

    with col_b2:
        if st.button("🚀 JETZT SOFORT ANMELDEN", use_container_width=True):
            for user in st.session_state.users:
                response = send_request(user)
                if response.status_code == 200 and "Error" not in response.text:
                    st.success(f"✅ {user['vorname']} angemeldet!  {response.text}")
                    st.info(response.json)
                else:
                    st.error(f"❌ {user['vorname']} fehlgeschlagen: {response.text}")
                    st.info(response)
else:
    st.info("Füge links Nutzer und ihre gewünschten Kurse hinzu oder lade eine Vorlage.")