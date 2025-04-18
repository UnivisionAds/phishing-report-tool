import streamlit as st
import smtplib
from email.message import EmailMessage
import whois

# === Giao diện nhập liệu ===
st.set_page_config(page_title="Phishing Report Tool", page_icon="🛡️")
st.title("🛡️ Phishing Report Tool")

sender_email = st.text_input("📧 Nhập Gmail của bạn (dùng để gửi)")
password = st.text_input("🔑 Nhập App Password Gmail", type="password")
domain = st.text_input("🌐 Nhập tên miền vi phạm")
issue_type = st.selectbox("🚨 Chọn loại vi phạm", ["Copyright/DMCA", "Phishing", "Gambling"])

# === Khi nhấn nút Gửi báo cáo ===
if st.button("📤 Gửi báo cáo"):
    # Kiểm tra các trường bắt buộc
    if not all([sender_email, password, domain, issue_type]):
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

        to_email = st.text_input("✉️ Xác nhận hoặc thay đổi email người nhận", to_email or "")

        if not to_email:
            st.error("⚠️ Vui lòng nhập email người nhận!")
            st.stop()

        # Tạo nội dung email
        email_body = f"""
Dear Sir/Madam,

I am writing to report a serious violation involving the domain {domain}. This domain is engaging in {issue_type}, impersonating a legitimate brand, and causing significant harm.

I request the immediate takedown of this domain to prevent further damage. Please take urgent action as per applicable laws and regulations.

Sincerely,
[Your Name]
        """

        edited_body = st.text_area("📄 Chỉnh sửa nội dung email nếu cần", email_body, height=300)

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

            st.success(f"✅ Gửi email thành công tới {to_email}!")
        except Exception as e:
            st.error(f"❌ Lỗi khi gửi email: {e}")

# Lưu ý: Để bảo mật, nên cấu hình sender_email và password trong Streamlit secrets
