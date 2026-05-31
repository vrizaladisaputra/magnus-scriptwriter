import os
import requests
import time
import json

# ============================================================
# KONFIGURASI BOT MAGNUS + GEMINI AI
# ============================================================
MAGNUS_TOKEN = os.environ.get("MAGNUS_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MAGNUS_TOPIC_ID = 4
MEMORY_FILE = "/data/memory.json"

CURRENT_AGENT_DATA = {}
USER_STATE = {}

def load_memory():
    """Membaca ingatan masa lalu dari harddisk virtual"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(data_to_save):
    """Menyimpan skrip + feedback rating secara permanen"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    memory = load_memory()
    memory.append(data_to_save)
    # Membatasi ingatan hingga 15 skrip emas terakhir agar AI fokus pada pola terbaru
    if len(memory) > 15:
        memory = memory[-15:]
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

def generate_script_with_ai(title, channel, video_url):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # 1. BACA HISTORI + BOBOT RATING MASA LALU (EXPERIENCE LOOP)
    past_memory = load_memory()
    memory_context = ""
    if past_memory:
        memory_context = "\n⚠️ [PENTING] PELAJARI RIWAYAT PENGALAMAN & EVALUASI GAYA BAHASA SEBELUMNYA DI BAWAH INI:\n"
        for mem in past_memory:
            status = mem.get("status")
            script_content = mem.get("script", "")
            
            if status == "RATING_4":
                memory_context += f"👉 [RATING 4/4 - PERFECT STYLE (TIRU TOTAL)]: User menilai skrip ini 100% SANGAT SEMPURNA mencerminkan dirinya. Pelajari pilihan katanya, flow, hook, gaya santainya, dan REPLIKASI gaya bahasa ini secara utuh:\n\"\"\"{script_content}\"\"\"\n\n"
            elif status == "RATING_3":
                memory_context += f"👉 [RATING 3/4 - GREAT STYLE (IKUTI SEBAGIAN BESAR)]: Skrip ini hampir sempurna dan mendekati gaya asli user. Gunakan tone, struktur kalimat, dan ritme dari skrip ini sebagai acuan utama:\n\"\"\"{script_content}\"\"\"\n\n"
            elif status == "RATING_2":
                memory_context += f"👉 [RATING 2/4 - GOOD BUT NOT ME (CUKUP CATAT SEDIKIT)]: Skrip ini isinya bagus tapi gaya bahasanya kurang mencerminkan kepribadian user. Ambil poin solusinya saja, tetapi rombak total gayanya agar tidak terlalu kaku/baku seperti skrip ini:\n\"\"\"{script_content}\"\"\"\n\n"
            elif status == "REVISED":
                memory_context += f"👉 [KRITIK TEXTUAL USER]: Pada skrip lalu, user memberikan koreksi spesifik: \"{mem['feedback']}\". Perbaiki kekurangan ini sekarang!\n\n"

    # 2. PROMPT AGENT YANG DILENGKAPI OTAK PEMBOBOTAN
    prompt = f"""
    Kamu adalah Magnus, seorang AI Content Agent khusus TikTok ceruk Karir Korporat & Dunia Kerja Indonesia.
    Kamu adalah agen cerdas yang berevolusi dengan mempelajari tingkat rating kecocokan gaya bahasa dari user.
    
    Tugas kamu: Buat skrip TikTok 1 menit (~130-150 kata) dengan formula PAS (Problem, Agitate, Solution).
    Tone utama: Santai, blak-blakan anak kantor Jakarta (pake 'lo'/'gue'), relatable, tajam, tapi berbobot.
    
    Topik Konten Baru:
    Judul Inspirasi: "{title}" | Channel: {channel} ({video_url})
    {memory_context}
    
    Format Output Harus Mengikuti Struktur Ini:
    🧙‍♂️ <b>MAGNUS — AI Agent (Adaptive Memory Mode)</b>
    <i>Inspirasi Konten: {title}</i>
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    
    <b>[0-5s] HOOK:</b> "[Tulis kalimat hook]"
    <b>[5-20s] AGITATE:</b> "[Goreng masalahnya]"
    <b>[20-50s] SOLUTION:</b> "[Kasih solusi taktis korporat]"
    <b>[50-60s] CTA:</b> "[Ajakan interaksi debat/curhat di komen]"
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    💡 #tipskarir #korporat #duniakerja
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            if attempt == 2: return f"⚠️ Gemini API Error: {e}"
            time.sleep(2)

def send_script_with_rating_buttons(text, title):
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True, "message_thread_id": MAGNUS_TOPIC_ID,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "1️⃣ Acceptable", "callback_data": f"rat_1_{title[:20]}"},
                    {"text": "2️⃣ Good (Not Me)", "callback_data": f"rat_2_{title[:20]}"}
                ],
                [
                    {"text": "3️⃣ Great (Almost Me)", "callback_data": f"rat_3_{title[:20]}"},
                    {"text": "4️⃣ Perfect (It's Me)", "callback_data": f"rat_4_{title[:20]}"}
                ],
                [
                    {"text": "❌ Revise / Kritik Manual", "callback_data": f"rev_{title[:20]}"}
                ]
            ]
        }
    }
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def send_plain_message(text):
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "message_thread_id": MAGNUS_TOPIC_ID}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def listen_to_carl():
    offset = None
    global CURRENT_AGENT_DATA, USER_STATE
    print("🧙‍♂️ Magnus AI Agent standby dengan 4-Skala Pembobotan Rating...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/getUpdates"
            res = requests.get(url, params={"timeout": 30, "offset": offset}, timeout=35).json()
            for update in res.get("result", []):
                offset = update["update_id"] + 1
                
                # Handler Klik Tombol
                if "callback_query" in update:
                    cq = update["callback_query"]
                    cb_data = cq.get("data", "")
                    requests.post(f"https://api.telegram.org/bot{MAGNUS_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
                    
                    # Logic 4 Tingkat Rating
                    if cb_data.startswith("rat_"):
                        rating = int(cb_data.split("_")[1])
                        
                        labels = {
                            1: "1/4 - Acceptable (Gak disimpan ke Memori)",
                            2: "2/4 - Good, but doesn't sound like me (Dicatat Sedikit)",
                            3: "3/4 - Great, mostly sounds like me (Dicatat Sebagian Besar)",
                            4: "4/4 - Perfect, sounds like me (Standar Emas - Catat Total!)"
                        }
                        
                        if rating == 1:
                            send_plain_message("👌 <b>Noted:</b> Skrip dinilai <b>Acceptable</b>. Gak dimasukkan ke database memori biar gak menuh-menuhin otak Magnus.")
                        else:
                            save_memory({
                                "title": CURRENT_AGENT_DATA.get("title", "Konten"),
                                "status": f"RATING_{rating}",
                                "script": CURRENT_AGENT_DATA.get("script", ""),
                                "feedback": labels[rating]
                            })
                            send_plain_message(f"🧠 <b>Memori Diupdate:</b> Magnus mempelajari skrip dengan bobot <b>Rating {rating}/4</b>\n<i>({labels[rating]})</i>.")
                    
                    elif cb_data.startswith("rev_"):
                        USER_STATE[TELEGRAM_CHAT_ID] = "WAITING_REVISION"
                        send_plain_message("✍️ <b>Kritik Manual:</b> Bagian mana yang kurang oke, bro? Ketik koreksinya langsung di sini...")
                
                # Handler Pesan Teks
                message_obj = update.get("message") or update.get("edited_message")
                if message_obj and "text" in message_obj:
                    msg_text = message_obj["text"].strip()
                    
                    if USER_STATE.get(TELEGRAM_CHAT_ID) == "WAITING_REVISION":
                        save_memory({"title": CURRENT_AGENT_DATA.get("title", "Konten"), "status": "REVISED", "script": CURRENT_AGENT_DATA.get("script", ""), "feedback": msg_text})
                        send_plain_message(f"💡 <b>Memori Diupdate:</b> Evaluasi lo dicatat: <i>\"{msg_text}\"</i>.")
                        USER_STATE[TELEGRAM_CHAT_ID] = None
                        continue
                    
                    if "GENERATE_SCRIPT" in msg_text:
                        lines = msg_text.split("\n")
                        title, channel, video_url = "Konten Viral", "Anonim", ""
                        for line in lines:
                            if "TITLE:" in line: title = line.split("TITLE:")[-1].strip()
                            elif "CHANNEL:" in line: channel = line.split("CHANNEL:")[-1].strip()
                            elif "URL:" in line: video_url = line.split("URL:")[-1].strip()
                        
                        script = generate_script_with_ai(title, channel, video_url)
                        CURRENT_AGENT_DATA = {"title": title, "channel": channel, "video_url": video_url, "script": script}
                        send_script_with_rating_buttons(script, title)
        except: time.sleep(5)

if __name__ == "__main__":
    listen_to_carl()
