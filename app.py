import whois
import smtplib
import openai
import getpass
from email.message import EmailMessage

# === Nhập cấu hình từ người dùng ===
sender_email = input("Nhập Gmail của bạn (dùng để gửi): ").strip()
password = getpass.getpass("Nhập App Password Gmail: ").strip()
openai.api_key = getpass.getpass("Nhập OpenAI API Key (sk-...): ").strip()

# === Nhập dữ liệu vi phạm ===
domain = input("Nhập tên miền vi phạm: ").strip()
print("Chọn lỗi vi phạm:")
print("1. Copyright/DMCA")
print("2. Phishing")
print("3. Gambling")
choice = input("Nhập số (1-3): ").strip()
issue_type = {"1": "Copyright/DMCA", "2": "Phishing", "3": "Gambling"}.get(choice, "Other")

# === Kiểm tra registrar qua WHOIS ===
try:
    w = whois.whois(domain)
    registrar = w.registrar.lower() if w.registrar else "unknown"
    print(f"🔍 Tên miền {domain} đăng ký tại: {registrar}")
except Exception as e:
    print("⚠️ Không lấy được thông tin whois:", e)
    registrar = "unknown"

# === Xác định email đích phù hợp ===
to_email = None
if "namecheap" in registrar:
    to_email = "dmca@namecheap.com" if issue_type == "Copyright/DMCA" else "abuse@namecheap.com"
elif "godaddy" in registrar:
    to_email = "copyrightcomplaints@godaddy.com"

print(f"📬 Email người nhận gợi ý: {to_email if to_email else 'Không xác định'}")

if not to_email:
    choice = input("⚠️ Không xác định được email tự động. Nhập email người nhận thủ công? (y/n): ").strip().lower()
    if choice == 'y':
        to_email = input("Nhập email người nhận: ").strip()
    else:
        print("⛔ Dừng lại vì không có email đích.")
        exit()
else:
    confirm = input(f"Bạn có muốn thay đổi email người nhận [{to_email}]? (y/n): ").strip().lower()
    if confirm == 'y':
        to_email = input("Nhập email người nhận mới: ").strip()

# === Sinh nội dung email bằng ChatGPT ===
prompt = f"""
Write a strong, professional email to report the domain {domain} for {issue_type}.
Mention that the domain is impersonating a legitimate brand and request immediate takedown.
Use legal language and urgency.
"""

print("🧠 Đang soạn email bằng ChatGPT...")
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
email_body = response['choices'][0]['message']['content']

print("\n📄 Nội dung email được tạo:\n")
print("=" * 50)
print(email_body)
print("=" * 50)

edit = input("✏️ Bạn có muốn chỉnh sửa nội dung email này không? (y/n): ").strip().lower()
if edit == 'y':
    print("➡️ Nhập nội dung mới. Kết thúc bằng một dòng trống (Enter 2 lần):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    email_body = "\n".join(lines)
    print("✅ Nội dung email đã được cập nhật.")

# === Gửi email thật qua Gmail SMTP ===
msg = EmailMessage()
msg['From'] = sender_email
msg['To'] = to_email
msg['Subject'] = f"Violation Report – {domain}"
msg.set_content(email_body)

print(f"📤 Đang gửi email tới {to_email}...")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        print("✅ Gửi email thành công!")
except Exception as e:
    print("❌ Lỗi khi gửi email:", e)