import os
import requests
import time
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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

    # 2. PROMPT AGENT YANG DILENGKAPI OTAK PEMBOBOTAN DAN ENGAGEMENT ENGINE
    prompt = f"""
    Kamu adalah Magnus, seorang AI Content Agent khusus TikTok ceruk Karir Korporat & Dunia Kerja Indonesia.
    Kamu adalah pembuat konten TikTok yang handal, sinis, realistis, dan benci basa-basi.
    Tugas kamu: Buat skrip TikTok durasi ~60 detik (130-150 kata) dengan gaya bicara santai, natural, mengalir, dan MEMICU ENGAGEMENT TINGGI.

    =========================================
    🚨 ATURAN BAHASA TUTUR (WAJIB DIPATUHI):
    =========================================
    1. JANGAN PERNAH gunakan kata-kata AI Klise ini: "Gawat!", "Bahaya!", "Tahukah kamu?", "Duh", "Yuk", "Nah", "Kalian".
    2. JANGAN PERNAH membuat daftar transisi kaku seperti: "Pertama...", "Kedua...", "Ketiga...". 
       Ganti dengan transisi kasual: "Mulai sekarang...", "Taktik paling aman itu...", "Satu lagi yang penting...", "Kuncinya ada di...".
    3. Gunakan bahasa gaul/slang kantoran Jakarta yang organik: "red flag", "lindungi diri", "silent treatment", "nyari aman", "capek batin", "drama", "gimmick", "curhat", "bos".
    4. Tulis skrip menggunakan tanda baca emosional seperti titik tiga (...) untuk jeda napas alami, atau HURUF KAPITAL untuk kata yang perlu ditekankan. Buat seakan-akan kamu sedang bicara langsung/curhat ke teman kerja.

    =========================================
    🔥 STRUKTUR SKRIP HIGH-ENGAGEMENT:
    =========================================
    - [HOOK (0-5s)]: Harus berupa pernyataan blunt, sindiran halus, atau situasi POV yang bikin orang berhenti scroll karena merasa disindir atau relate. Hindari kata seru dramatis.
      * Contoh Bagus: "Punya bos yang hobinya ngegosipin timnya sendiri tuh... bener-bener definisi capek batin."
    - [AGITATE (5-20s)]: Goreng masalahnya sampai terasa menyesakkan. Bikin penonton merasa "Gue banget!". Fokus pada emosi 'ketidakadilan di kantor'.
    - [SOLUTION (20-50s)]: Berikan taktik bertahan hidup (survival tactics) yang praktis, cerdas, sedikit licik tapi realistis. Bukan saran teori HRD yang naif.
    - [CTA (50-60s)]: JANGAN tanya "Menurut kalian gimana?". Pancing mereka untuk curhat colongan, berbagi drama, atau mengeluhkan bos mereka di kolom komentar.
      * Contoh Bagus: "Bos lo ada yang setipe kayak gini juga gak? Atau lo punya taktik yang lebih sosiopat buat ngadepinnya? Spill drama lo di bawah, mari kita gibah sehat."

    =========================================
    INPUT DATA:
    =========================================
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
    headers = {"Content-Type": "application/json"}
    
    # UPGRADE UTAMA: Gunakan model stabil publik (gemini-1.5-flash sebagai utama, gemini-1.5-pro sebagai cadangan)
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
    backoff_delays = [1, 2, 4]
    last_error_msg = ""
    
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(len(backoff_delays)):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                # DETEKSI BATASAN KUOTA & ERROR UTAMA (400, 403, 429)
                if response.status_code in [400, 403, 429]:
                    try:
                        err_json = response.json()
                        err_msg = err_json.get("error", {}).get("message", "API key issues or rate limit exceeded.")
                    except:
                        err_msg = response.text
                    
                    if response.status_code == 429:
                        return "⚠️ <b>Google Gemini API Error (429 - Rate Limit Exceeded):</b> Batas kuota gratis akun Anda sedang habis sementara.\n\n<i>Google membatasi akun Free Tier maksimal 15 kali request per menit. Silakan tunggu 1-2 menit lalu coba kembali, bos!</i>"
                    else:
                        return f"⚠️ <b>Google Gemini API Error ({response.status_code}):</b> {err_msg}\n\n<i>Bos, silakan periksa kembali GEMINI_API_KEY Anda di Railway. Pastikan kuncinya diawali dengan 'AIzaSy...' dan berstatus aktif!</i>"
                
                response.raise_for_status()
                res_data = response.json()
                ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
                return ai_text
            except Exception as e:
                last_error_msg = str(e)
                print(f"⚠️ Gagal mencoba model {model_name} pada percobaan ke-{attempt+1}: {e}")
            time.sleep(backoff_delays[attempt])
            
    return f"⚠️ <b>Gemini API Error:</b> Seluruh server Google Gemini sedang sibuk atau mengalami gangguan sementara.\n\nDetail error terakhir: <code>{last_error_msg}</code>\n\n<i>Silakan coba klik generate kembali beberapa saat lagi, bos!</i>"

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

# ============================================================
# LAYER KONEKSI HTTP SERVER (JALUR TOL INTERAL RAILWAY)
# ============================================================
class MagnusHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/generate":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            title = data.get("title", "Konten Viral")
            channel = data.get("channel", "Anonim")
            video_url = data.get("video_url", "")
            
            threading.Thread(target=process_internal_trigger, args=(title, channel, video_url)).start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def process_internal_trigger(title, channel, video_url):
    global CURRENT_AGENT_DATA
    send_plain_message(f"⚡ <b>Magnus AI Agent:</b> Menerima instruksi langsung dari Carl! Mulai memikirkan skrip untuk: <i>\"{title}\"</i>...")
    script = generate_script_with_ai(title, channel, video_url)
    
    # SMART FILTER: Jika output berupa error teks, kirim sebagai pesan biasa tanpa tombol rating
    if script.startswith("⚠️"):
        send_plain_message(script)
    else:
        CURRENT_AGENT_DATA = {"title": title, "channel": channel, "video_url": video_url, "script": script}
        send_script_with_rating_buttons(script, title)

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), MagnusHTTPHandler)
    print(f"🖥️ Magnus HTTP Server berjalan di port {port}...")
    server.serve_forever()

# ============================================================
# TELEGRAM POLLING LOOP
# ============================================================
def listen_to_carl():
    offset = None
    global CURRENT_AGENT_DATA, USER_STATE
    print("🧙‍♂️ Magnus AI Agent standby menangkap klik tombol rating Anda...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{MAGNUS_TOKEN}/getUpdates"
            res = requests.get(url, params={"timeout": 30, "offset": offset}, timeout=35).json()
            for update in res.get("result", []):
                offset = update["update_id"] + 1
                
                if "callback_query" in update:
                    cq = update["callback_query"]
                    cb_data = cq.get("data", "")
                    
                    requests.post(f"https://api.telegram.org/bot{MAGNUS_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
                    
                    if cb_data.startswith("rat_"):
                        rating = int(cb_data.split("_")[1])
                        labels = {
                            1: "1/4 - Acceptable (Abaikan dari Memori)",
                            2: "2/4 - Good (Dicatat Sedikit)",
                            3: "3/4 - Great (Dicatat Sebagian Besar)",
                            4: "4/4 - Perfect (Standar Emas - Replikasi Total!)"
                        }
                        
                        if rating == 1:
                            send_plain_message("👌 <b>Noted:</b> Skrip dinilai <b>Acceptable</b>. Tidak disimpan ke memori.")
                        else:
                            save_memory({
                                "title": CURRENT_AGENT_DATA.get("title", "Konten"),
                                "status": f"RATING_{rating}",
                                "script": CURRENT_AGENT_DATA.get("script", ""),
                                "feedback": labels[rating]
                            })
                            send_plain_message(f"🧠 <b>Memori Diupdate:</b> Magnus mempelajari gaya skrip ini dengan bobot <b>Rating {rating}/4</b>.")
                    
                    elif cb_data.startswith("rev_"):
                        USER_STATE[TELEGRAM_CHAT_ID] = "WAITING_REVISION"
                        send_plain_message("✍️ <b>Kritik Manual:</b> Bagian mana yang kurang oke, bos? Ketik koreksinya langsung di sini...")
                
                message_obj = update.get("message") or update.get("edited_message")
                if message_obj and "text" in message_obj:
                    msg_text = message_obj["text"].strip()
                    
                    if USER_STATE.get(TELEGRAM_CHAT_ID) == "WAITING_REVISION":
                        save_memory({"title": CURRENT_AGENT_DATA.get("title", "Konten"), "status": "REVISED", "script": CURRENT_AGENT_DATA.get("script", ""), "feedback": msg_text})
                        send_plain_message(f"💡 <b>Memori Diupdate:</b> Evaluasi Anda dicatat: <i>\"{msg_text}\"</i>.")
                        USER_STATE[TELEGRAM_CHAT_ID] = None
                        
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    listen_to_carl()
