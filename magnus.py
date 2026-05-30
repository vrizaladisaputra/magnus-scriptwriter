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

def generate_script_with_ai(title, channel, video_url, keywords_str):
    """Menggunakan Gemini AI untuk generate script TikTok yang dinamis"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
    <i>Inspirasi Konten: [Judul Video] ([Nama Channel])</i>
    🔗 [Link Video URL]
    ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═
    
    ⏱ <b>Durasi Target:</b> ~60 Detik
    🎯 <b>Rumpun Topik:</b> #[Tentukan topik contoh: gaji/promosi/resign]
    
    <b>[0-5s] HOOK (Bikin hook yang out-of-the-box, langsung nembak keresahan penonton):</b>
    🎙 <i>(Tatap kamera, ekspresi serius/penasaran)</i>
    "[Tulis kalimat hook di sini, jangan gunakan template standar]"
    
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
    #tipskarir #korporat #kantor #duniakerja #[tambah hashtag relevan]
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        res_data = response.json()
        ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
        
        # Selipkan info asli ke output jika belum ter-replace otomatis
        ai_text = ai_text.replace("[Judul Video]", title).replace("[Nama Channel]", channel).replace("[Link Video URL]", video_url)
        return ai_text
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return f"⚠️ Magnus gagal mikir pake AI. Detail error: {e}"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Magnus gagal kirim chat: {e}")

def listen_to_carl():
    offset = None
    url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/getUpdates"
    print("🧙‍♂️ Magnus AI standby 24/7 menerima rekues script dinamis dari Carl...")
    
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            
            response = requests.get(url, params=params, timeout=35)
            updates = response.json().get("result", [])
            
            for update in updates:
                offset = update["update_id"] + 1
                if "callback_query" in update:
                    continue
                    
                if "message" in update and "text" in update["message"]:
                    msg_text = update["message"]["text"]
                    
                    if msg_text.startswith("GENERATE_SCRIPT"):
                        print("⚡ Magnus menerima sinyal! Sedang memproses ide dengan Gemini AI...")
                        lines = msg_text.split("\n")
                        
                        title = lines[1].replace("TITLE:", "") if len(lines) > 1 else "Konten Viral"
                        channel = lines[2].replace("CHANNEL:", "") if len(lines) > 2 else "Anonim"
                        video_url = lines[3].replace("URL:", "") if len(lines) > 3 else ""
                        keywords = lines[4].replace("KEYWORDS:", "") if len(lines) > 4 else "default"
                        
                        script = generate_script_with_ai(title, channel, video_url, keywords)
                        send_to_telegram(script)
                        
        except Exception as e:
            print(f"Magnus Polling Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    listen_to_carl()
