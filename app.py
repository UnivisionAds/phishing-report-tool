import streamlit as st
import smtplib
from email.message import EmailMessage

# === Giao diện nhập liệu ===
st.set_page_config(page_title="Phishing Report Tool", page_icon="🛡️")
st.title("🛡️ Phishing Report Tool")

sender_email = st.text_input("📧 Nhập Gmail của bạn (dùng để gửi)")
password = st.text_input("🔑 Nhập App Password Gmail", type="password")
domain = st.text_input("🌐 Nhập tên miền vi phạm")
issue_type = st.selectbox("🚨 Chọn loại vi phạm", ["Copyright/DMCA", "Phishing", "Gambling"])

# === Khi nhấn nút Gửi báo cáo ===
if st.button("📤 Gửi báo cáo"):
        st.error("⚠️ Vui lòng nhập đầy đủ tất cả các trường bắt buộc!")
        st.stop()

    client = PoeClient(poe_token)

    # === Giả lập thông tin WHOIS để test UI ===
    registrar = "namecheap"  # hoặc thay bằng "godaddy" để test nhánh khác
    st.info(f"(Giả lập) 🔍 Tên miền {domain} được xử lý như: {registrar}")

    # === Xác định email đích phù hợp ===
    to_email = None
    if "namecheap" in registrar:
        to_email = "dmca@namecheap.com" if issue_type == "Copyright/DMCA" else "abuse@namecheap.com"
    elif "godaddy" in registrar:
        to_email = "copyrightcomplaints@godaddy.com"

    to_email = st.text_input("✉️ Xác nhận hoặc thay đổi email người nhận", to_email or "")

    # === Sinh nội dung email bằng GPT
    prompt = f"""
    Write a strong, professional email to report the domain {domain} for {issue_type}.
    Mention that the domain is impersonating a legitimate brand and request immediate takedown.
    Use legal language and urgency.
    """

    with st.spinner("🧠 Đang soạn nội dung email bằng ChatGPT..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            email_body = response.choices[0].message.content
        except Exception as e:
            st.stop()

    edited_body = st.text_area("📄 Chỉnh sửa nội dung email nếu cần", email_body, height=300)

    # === Gửi email qua Gmail SMTP ===
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