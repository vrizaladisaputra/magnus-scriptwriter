import os
import requests
import time
import json

MAGNUS_TOKEN = os.environ.get("MAGNUS_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ID TOPIK SPESIFIK MAGNUS
MAGNUS_TOPIC_ID = 4

def generate_script_with_ai(title, channel, video_url, keywords_str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Kamu adalah Magnus, seorang Script Writer TikTok profesional ceruk Karir Korporat Indonesia.
    Buat skrip Short Video TikTok 1 menit (~130-150 kata) berdasarkan topik:
    Judul: "{title}" | Channel: {channel} | Keywords: {keywords_str}
    
    Formula: PAS (Problem, Agitate, Solution) + CTA.
    Tone: Santai, blak-blakan (pake 'lo', 'gue', 'kantor', 'bos'), relatable banget. Jangan kaku!
    
    Format Output Wajib Mengikuti Struktur Ini:
    🧙‍♂️ <b>MAGNUS — TikTok Script Writer</b>
    <i>Inspirasi Konten: {title} ({channel})</i>
    🔗 {video_url}
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    
    ⏱ <b>Durasi Target:</b> ~60 Detik
    🎯 <b>Rumpun Topik:</b> #karir
    
    <b>[0-5s] HOOK:</b>
    🎙 <i>(Tatap kamera, ekspresi serius)</i>
    "[Kalimat hook]"
    
    <b>[5-20s] AGITATE:</b>
    🎙 <i>(Nada empati)</i>
    "[Bagian agitate]"
    
    <b>[20-50s] SOLUTION:</b>
    🎙 <i>(Nada tegas, kasih daging)</i>
    "[Solusi praktis kantor]"
    
    <b>[50-60s] CTA:</b>
    🎙 <i>(Ajak interaksi/debat di komen)</i>
    "[Kalimat CTA]"
    
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    💡 #tipskarir #korporat #duniakerja
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"⚠️ Gemini AI Error: {e}"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML", 
        "disable_web_page_preview": True,
        "message_thread_id": MAGNUS_TOPIC_ID # FIX: Kirim naskah khusus ke topik Magnus
    }
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def listen_to_carl():
    offset = None
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/getUpdates"
    print("🧙‍♂️ Magnus AI standby di forum grup...")
    while True:
        try:
            params = {"timeout": 30}
            if offset: params["offset"] = offset
            response = requests.get(url, params=params, timeout=35).json()
            updates = response.get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                # Mengambil pesan teks dari chat pribadi bot maupun dari grup
                message_obj = update.get("message") or update.get("edited_message")
                if message_obj and "text" in message_obj:
                    msg_text = message_obj["text"]
                    if msg_text.startswith("GENERATE_SCRIPT"):
                        lines = msg_text.split("\n")
                        title, channel, video_url, keywords = "Konten Viral", "Anonim", "", "default"
                        for line in lines:
                            if line.startswith("TITLE:"): title = line.replace("TITLE:", "").strip()
                            elif line.startswith("CHANNEL:"): channel = line.replace("CHANNEL:", "").strip()
                            elif line.startswith("URL:"): video_url = line.replace("URL:", "").strip()
                            elif line.startswith("KEYWORDS:"): keywords = line.replace("KEYWORDS:", "").strip()
                        script = generate_script_with_ai(title, channel, video_url, keywords)
                        send_to_telegram(script)
        except: time.sleep(5)

if __name__ == "__main__":
    listen_to_carl()
