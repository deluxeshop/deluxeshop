import email
import imaplib
import re
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ================= GİRDİ ALANLARI =================
EMAIL_USER = "dshop2830@gmail.com"
EMAIL_PASS = "loopmnogiowzffgs"  # 16 haneli uygulama şifren
# ===================================================


def get_latest_code():
  try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    # Sadece okunmamış (yeni) mailleri tarıyoruz ki eski mailler/kodlar karışmasın
    status, messages = mail.search(None, "UNSEEN")
    if not messages[0]:
      return None

    mail_ids = messages[0].split()
    recent_ids = mail_ids[-1:][::-1]

    for latest_id in recent_ids:
      status, data = mail.fetch(latest_id, "(RFC822)")
      for response_part in data:
        if isinstance(response_part, tuple):
          msg = email.message_from_bytes(response_part[1])

          body = ""
          if msg.is_multipart():
            for part in msg.walk():
              if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    "utf-8", errors="ignore"
                )
          else:
            body = msg.get_payload(decode=True).decode(
                "utf-8", errors="ignore"
            )

          body_lower = body.lower()
          keywords = [
              "kod",
              "code",
              "dogrulama",
              "verification",
              "şifre",
              "pin",
              "onay",
          ]

          if any(kw in body_lower for kw in keywords):
            codes = re.findall(r"\b\d{4,6}\b", body)
            if codes:
              valid_codes = [c for c in codes if c != "2026"]
              if valid_codes:
                return valid_codes[0]

    return None
  except Exception as e:
    print("Hata:", e)
    return None


HTML_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeluxeShop - Otomatik Teslimat & Kod Paneli</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; justify-content: space-between; }
        nav { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid #1e293b; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 10; }
        .logo { font-size: 24px; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
        .badge-live { background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
        .badge-live::before { content: ''; width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .container { max-width: 550px; margin: 60px auto; padding: 0 20px; width: 100%; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 24px; padding: 40px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { font-size: 26px; font-weight: 700; margin-bottom: 8px; color: #fff; }
        .subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 30px; line-height: 1.5; }
        .input-group { margin-bottom: 24px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        .email-box { background: #0f172a; border: 1px solid #475569; border-radius: 12px; padding: 14px 18px; font-size: 15px; font-weight: 600; color: #38bdf8; word-break: break-all; display: flex; justify-content: space-between; align-items: center; }
        .btn-primary { width: 100%; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; padding: 16px; font-size: 16px; font-weight: 700; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }
        .btn-primary:hover { background: linear-gradient(135deg, #4f46e5, #4338ca); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6); }
        .result-container { margin-top: 30px; background: #0f172a; border: 1px solid #334155; border-radius: 16px; padding: 25px; text-align: center; }
        .result-title { font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; }
        #codeDisplay { font-size: 28px; font-weight: 800; color: #22c55e; letter-spacing: 3px; min-height: 48px; display: flex; align-items: center; justify-content: center; }
        footer { text-align: center; padding: 30px; color: #64748b; font-size: 13px; border-top: 1px solid #1e293b; }
    </style>
</head>
<body>
    <nav>
        <div class="logo">⚡ DeluxeShop</div>
        <div class="badge-live">Sistem Aktif</div>
    </nav>
    <div class="container">
        <div class="card">
            <h1>Hızlı Doğrulama Paneli</h1>
            <p class="subtitle">Aşağıdaki e-posta adresini ilgili platforma girin ve işlem sonrasında kodu almak için butona tıklayın.</p>
            <div class="input-group">
                <label>Kullanılacak E-Posta Adresi</label>
                <div class="email-box"><span>""" + EMAIL_USER + """</span></div>
            </div>
            <button class="btn-primary" onclick="getCode()">Kodu Otomatik Getir</button>
            <div class="result-container">
                <div class="result-title">Gelen Doğrulama Kodu</div>
                <div id="codeDisplay">-</div>
            </div>
        </div>
    </div>
    <footer>&copy; 2026 DeluxeShop - Tüm Hakları Saklıdır. Güvenli Altyapı.</footer>
<script>
    async function getCode() {
        const display = document.getElementById('codeDisplay');
        display.style.color = "#94a3b8";
        display.innerText = "Aranıyor...";
        try {
            let res = await fetch('/get-code');
            let data = await res.json();
            if (data.code) {
                display.style.color = "#22c55e";
                display.innerText = data.code;
            } else {
                display.style.color = "#f43f5e";
                display.innerText = "Kod Yok";
            }
        } catch (e) {
            display.style.color = "#f43f5e";
            display.innerText = "Bağlantı Hatası!";
        }
    }
</script>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML_PAGE)


@app.route("/get-code")
def api_get_code():
  code = get_latest_code()
  return jsonify({"code": code})


if __name__ == "__main__":
  app.run(debug=True, port=5000)