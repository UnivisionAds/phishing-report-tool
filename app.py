import streamlit as st
import smtplib
from email.message import EmailMessage
import whois
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(
    filename="email_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    filemode="a"
)
logger = logging.getLogger()

# === Giao diện nhập liệu ===
st.set_page_config(page_title="Phishing Report Tool", page_icon="🛡️")
st.title("🛡️ Phishing Report Tool")

# Lấy danh sách tài khoản từ secrets
accounts = {}
try:
    accounts = {
        st.secrets["gmail"]["account1"]["sender_email"]: st.secrets["gmail"]["account1"]["password"],
        st.secrets["gmail"]["account2"]["sender_email"]: st.secrets["gmail"]["account2"]["password"],
        st.secrets["gmail"]["account3"]["sender_email"]: st.secrets["gmail"]["account3"]["password"]
    }
except KeyError as e:
    st.warning(f"⚠️ Lỗi cấu hình secrets: {e}. Sử dụng nhập thủ công.")

# Chọn hoặc nhập sender_email
if accounts:
    sender_email = st.selectbox("📧 Chọn Gmail để gửi", list(accounts.keys()))
    password = accounts[sender_email]  # Lấy password tương ứng
else:
    sender_email = st.text_input("📧 Nhập Gmail của bạn")
    password = st.text_input("🔑 Nhập App Password", type="password")

domain = st.text_input("🌐 Nhập tên miền vi phạm")
original_brand = st.text_input("🏷️ Nhập tên brand chính gốc bị giả mạo")
issue_type = st.selectbox("🚨 Chọn loại vi phạm", ["Copyright/DMCA", "Phishing", "Gambling"])

# === Khi nhấn nút Tạo báo cáo ===
if st.button("📝 Tạo báo cáo"):
    # Kiểm tra các trường bắt buộc
    if not all([sender_email, password, domain, original_brand, issue_type]):
        st.error("⚠️ Vui lòng nhập đầy đủ tất cả các trường bắt buộc!")
    else:
        # Lấy thông tin WHOIS để xác định registrar
        try:
            w = whois.whois(domain)
            registrar = w.registrar.lower() if w.registrar else ""
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy thông tin WHOIS: {e}")
            st.stop()

        # Xác định email đích
        to_email = None
        if "namecheap" in registrar:
            to_email = "dmca@namecheap.com" if issue_type == "Copyright/DMCA" else "abuse@namecheap.com"
        elif "godaddy" in registrar:
            to_email = "copyrightcomplaints@godaddy.com"
        elif "bluehost" in registrar:
            to_email = "abuse@bluehost.com"
        elif "hostinger" in registrar:
            to_email = "abuse@hostinger.com"
        elif any(r in registrar for r in ["tucows", "opensrs"]):
            to_email = "abuse@tucows.com"
        elif "name.com" in registrar:
            to_email = "abuse@name.com"
        elif "dynadot" in registrar:
            to_email = "abuse@dynadot.com"
        else:
            to_email = "abuse@registrardomain"

        to_email = st.text_input("✉️ Xác nhận hoặc thay đổi email người nhận", to_email or "")

        if not to_email:
            st.error("⚠️ Vui lòng nhập email người nhận!")
            st.stop()

        # Tạo nội dung email
        email_body = f"""
Dear Sir/Madam,

I am writing to report a serious violation involving the domain {domain}. This domain is engaging in {issue_type}, impersonating {original_brand}, a legitimate and well-known brand, and causing significant harm.

I request the immediate takedown of this domain to prevent further damage. Please take urgent action as per applicable laws and regulations.

Sincerely,
[Your Name]
        """

        # Cho phép chỉnh sửa nội dung email
        edited_body = st.text_area("📄 Chỉnh sửa nội dung email", email_body, height=300)

        # Nút xác nhận gửi email
        if st.button("📤 Xác nhận và gửi email"):
            # Gửi email qua Gmail SMTP
            try:
                msg = EmailMessage()
                msg['From'] = sender_email
                msg['To'] = to_email
                msg['Subject'] = f"Violation Report – {domain}"
                msg.set_content(edited_body)

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.send_message(msg)

                # Ghi log email gửi
                log_message = (
                    f"Email sent: From={sender_email}, To={to_email}, "
                    f"Domain={domain}, Issue={issue_type}, Registrar={registrar}, "
                    f"OriginalBrand={original_brand}, Content=\n{edited_body}"
                )
                logger.info(log_message)

                st.success(f"✅ Gửi email thành công tới {to_email}!")
            except Exception as e:
                st.error(f"❌ Lỗi khi gửi email: {e}")
