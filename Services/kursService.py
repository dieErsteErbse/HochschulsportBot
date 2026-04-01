import json

def scan_courses(start_id, end_id):
    url = "https://anmeldung.hochschulsport-koeln.de/inc/methods.php"
    found_courses = []

    print(f"Starte Scan von ID {start_id} bis {end_id}...")

    for course_id in range(start_id, end_id + 1):
        payload = {'state': 'getDetails', 'offer_course_id': str(course_id)}
        
        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Wenn ein kurs_name existiert, ist die ID gültig
                if data and "kurs_name" in data and data["kurs_name"]:
                    course_info = {
                        "id": data["sportangebote_kurse_id"],
                        "sport": data["sportangebot_name"],
                        "name": data["kurs_name"],
                        "tag": data["kurs_tag"],
                        "zeit": f"{data['kurs_zeit_start']} - {data['kurs_zeit_ende']}"
                    }
                    found_courses.append(course_info)
                    print(f"✅ Gefunden: {course_info['sport']} - {course_info['name']} (ID: {course_id})")
            
            # Kurze Pause, um den Server nicht zu stressen (Fair Play & Schutz vor Sperre)
            time.sleep(0.05) 
            
        except Exception:
            # Falls die ID nicht existiert oder kein JSON zurückkommt
            continue

    # Speichern als JSON
    with open('kurse_datenbank.json', 'w', encoding='utf-8') as f:
        json.dump(found_courses, f, ensure_ascii=False, indent=4)
    
    print(f"\nFertig! {len(found_courses)} Kurse wurden in 'kurse_datenbank.json' gespeichert.")

    import json

def lade_kurse(filepath='kurse_datenbank.json'):
    """
    Lädt die Kursdatenbank, strukturiert sie nach Sportarten 
    und gibt die sortierte Liste aller Sportarten zurück.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            kurs_daten = json.load(f)
    except FileNotFoundError:
        return []

    # --- DATEN STRUKTURIEREN ---
    sportarten_dict = {}
    for k in kurs_daten:
        sport = k['sport']
        if sport not in sportarten_dict:
            sportarten_dict[sport] = []
        sportarten_dict[sport].append(k)

    # Wir geben hier die sortierten Keys (Sportarten) zurück
    return sorted(sportarten_dict.keys())