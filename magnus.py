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

# ID TOPIK SPESIFIK MAGNUS
MAGNUS_TOPIC_ID = 4

def generate_script_with_ai(title, channel, video_url, keywords_str):
    """Menggunakan Gemini AI untuk generate script TikTok yang dinamis"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Kamu adalah Magnus, seorang Script Writer TikTok profesional dan Content Strategist spesialis ceruk Karir Korporat & Dunia Kerja di Indonesia.
    Tugas kamu adalah membuat skrip Short Video TikTok berdurasi 1 menit (~130-150 kata) berdasarkan topik video viral berikut:
    
    Judul Video Viral: "{title}"
    Channel / Kreator: {channel}
    Kata Kunci Terkait: {keywords_str}
    
    Gunakan formula psikologi konten: PAS (Problem, Agitate, Solution) + CTA.
    Tone: Santai, relatable, blak-blakan (pake kata 'lo', 'gue', 'kantor', 'bos'), kayak lagi ngobrol/curhat sama temen kerja tapi tetep berbobot (berisi fakta keras dunia kerja). Jangan pake bahasa baku atau kaku!
    
    Format Output Harus Mengikuti Struktur Ini:
    🧙‍♂️ <b>MAGNUS — TikTok Script Writer</b>
    <i>Inspirasi Konten: {title} ({channel})</i>
    🔗 {video_url}
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    
    ⏱ <b>Durasi Target:</b> ~60 Detik
    🎯 <b>Rumpun Topik:</b> #karir
    
    <b>[0-5s] HOOK (Bikin hook yang out-of-the-box, langsung nembak keresahan penonton):</b>
    🎙 <i>(Tatap kamera, ekspresi serius/penasaran)</i>
    "[Tulis kalimat hook di sini]"
    
    <b>[5-20s] AGITATE (Goreng masalahnya sampai penonton ngerasa nyesek/relate):</b>
    🎙 <i>(Nada empati, kayak curhat antar temen)</i>
    "[Tulis bagian agitate di sini]"
    
    <b>[20-50s] SOLUTION (Kasih 1-2 taktik konkret atau mind-blowing yang bisa langsung dicoba di kantor):</b>
    🎙 <i>(Nada tegas, ngasih daging/insight)</i>
    "[Tulis solusi praktis di sini]"
    
    <b>[50-60s] CTA (Ajakan interaksi yang memancing orang buat debat atau curhat di komen):</b>
    🎙 <i>(Senyum, ajak interaksi ringan)</i>
    "[Tulis kalimat CTA unik di sini]"
    
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    💡 <b>Rekomendasi Hashtag:</b>
    #tipskarir #korporat #kantor #duniakerja
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        res_data = response.json()
        ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
        return ai_text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return f"⚠️ Magnus gagal mikir pake AI. Detail error: {e}"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML", 
        "disable_web_page_preview": True,
        "message_thread_id": MAGNUS_TOPIC_ID  # Kirim naskah khusus ke topik Magnus
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Magnus gagal kirim chat: {e}")

def listen_to_carl():
    offset = None
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/getUpdates"
    print("🧙‍♂️ Magnus AI standby di Forum Topics grup...")
    
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            
            response = requests.get(url, params=params, timeout=35).json()
            updates = response.get("result", [])
            
            for update in updates:
                offset = update["update_id"] + 1
                
                # FIX STRUKTUR TOPICS: Ekstrak message dari berbagai jenis update di Telegram Group Forum
                message_obj = update.get("message") or update.get("edited_message") or update.get("channel_post")
                
                if message_obj and "text" in message_obj:
                    msg_text = message_obj["text"].strip()
                    
                    # Cek apakah chat mengandung kata kunci GENERATE_SCRIPT (baik di-tag maupun tidak)
                    if "GENERATE_SCRIPT" in msg_text:
                        print("⚡ Magnus mendeteksi rekues naskah di forum! Memproses...")
                        lines = msg_text.split("\n")
                        
                        title = "Konten Viral"
                        channel = "Anonim"
                        video_url = ""
                        keywords = "default"
                        
                        for line in lines:
                            if "TITLE:" in line:
                                title = line.split("TITLE:")[-1].strip()
                            elif "CHANNEL:" in line:
                                channel = line.split("CHANNEL:")[-1].strip()
                            elif "URL:" in line:
                                video_url = line.split("URL:")[-1].strip()
                            elif "KEYWORDS:" in line:
                                keywords = line.split("KEYWORDS:")[-1].strip()
                        
                        script = generate_script_with_ai(title, channel, video_url, keywords)
                        send_to_telegram(script)
                        
        except Exception as e:
            print(f"Magnus Topics Polling Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    listen_to_carl()
