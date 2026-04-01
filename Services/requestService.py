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