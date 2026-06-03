# test_email.py
# ═══════════════════════════════════════════════════════════
# PUT THIS IN YOUR PROJECT ROOT
# Run it from terminal:  python test_email.py
#
# This tests if Gmail SMTP works from YOUR machine.
# If it works locally but not on Railway = Railway is blocking.
# If it fails locally too = Google is blocking.
# ═══════════════════════════════════════════════════════════

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # ── CONFIG — same as your config.py ────────────────────────
# MAIL_SERVER = "smtp.gmail.com"
# MAIL_PORT = 465
# MAIL_USERNAME = "kennartecht@gmail.com"
# MAIL_PASSWORD = "hwnuujafaayqkohj"  # no spaces
# MAIL_USE_SSL = True

# # ── TEST: send to yourself ──────────────────────────────────
# TO_EMAIL = "kennartecht@gmail.com"
# LICENSE_KEY = "RPOS-TEST-1234-ABCD"
# PLAN_LABEL = "6-Month Plan"
# EXP_DISPLAY = "02 December 2026"

# html = f"""
# <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
#   <div style="background: #1a1d35; padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
#     <h1 style="color: #818cf8; margin: 0; font-size: 24px;">RetailersPOS</h1>
#     <p style="color: #7b82a8; margin: 8px 0 0;">Powered by Kennartech</p>
#   </div>
#   <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 12px 12px;">
#     <h2 style="color: #1a1d35; margin-top: 0;">Your License Key is Ready! 🎉</h2>
#     <div style="background: #1a1d35; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
#       <p style="color: #7b82a8; font-size: 12px; margin: 0 0 8px;">YOUR LICENSE KEY</p>
#       <p style="color: #818cf8; font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; letter-spacing: 2px;">
#         {LICENSE_KEY}
#       </p>
#     </div>
#     <p>Plan: <strong>{PLAN_LABEL}</strong></p>
#     <p>Valid Until: <strong>{EXP_DISPLAY}</strong></p>
#     <p style="color: #6b7280; font-size: 13px;">
#       Go to Settings → Subscription → paste the key → click Activate
#     </p>
#   </div>
# </div>
# """

# plain = f"""
# Your RetailersPOS License Key
# License Key : {LICENSE_KEY}
# Plan        : {PLAN_LABEL}
# Valid Until : {EXP_DISPLAY}
# Go to Settings → Subscription → paste the key → Activate
# """.strip()

# print(f"Sending test email to {TO_EMAIL}...")
# print(f"Using: {MAIL_USERNAME} via {MAIL_SERVER}:{MAIL_PORT}")

# try:
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = "TEST — Your RetailersPOS License Key 🔑"
#     msg["From"] = f"Kennartech RetailersPOS <{MAIL_USERNAME}>"
#     msg["To"] = TO_EMAIL

#     msg.attach(MIMEText(plain, "plain"))
#     msg.attach(MIMEText(html, "html"))

#     with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
#         print("Connecting to Gmail...")
#         server.login(MAIL_USERNAME, MAIL_PASSWORD)
#         print("Login successful!")
#         server.sendmail(MAIL_USERNAME, TO_EMAIL, msg.as_string())

#     print()
#     print(" Email sent successfully! Check your inbox.")
#     print("   If you got the email = Gmail SMTP works locally.")
#     print("   The problem is Railway blocking outbound port 465.")

# except Exception as e:
#     print()
#     print(f" Failed: {e}")
#     print()
#     print("This means Gmail/Google is blocking the request.")
#     print("Solution: switch to Resend.com API instead of SMTP.")



# = Current Version: 1.0.0 which is the latest version
# import asyncio
# from email.message import EmailMessage
# import aiosmtplib

# # ── CONFIG ────────────────────────────────────────────────
# MAIL_SERVER = "smtp.gmail.com"
# MAIL_PORT = 465
# MAIL_USERNAME = "kennartecht@gmail.com"
# MAIL_PASSWORD = "hwnuujafaayqkohj"
# MAIL_USE_SSL = True

# # ── TEST DATA ─────────────────────────────────────────────
# TO_EMAIL = "kennartecht@gmail.com"
# LICENSE_KEY = "RPOS-TEST-1234-ABCD"
# PLAN_LABEL = "6-Month Plan"
# EXP_DISPLAY = "02 December 2026"

# html = f"""
# <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
#   <div style="background: #1a1d35; padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
#     <h1 style="color: #818cf8; margin: 0; font-size: 24px;">RetailersPOS</h1>
#     <p style="color: #7b82a8; margin: 8px 0 0;">Powered by Kennartech</p>
#   </div>
#   <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 12px 12px;">
#     <h2 style="color: #1a1d35; margin-top: 0;">Your License Key is Ready! 🎉</h2>
#     <div style="background: #1a1d35; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
#       <p style="color: #7b82a8; font-size: 12px; margin: 0 0 8px;">YOUR LICENSE KEY</p>
#       <p style="color: #818cf8; font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; letter-spacing: 2px;">
#         {LICENSE_KEY}
#       </p>
#     </div>
#     <p>Plan: <strong>{PLAN_LABEL}</strong></p>
#     <p>Valid Until: <strong>{EXP_DISPLAY}</strong></p>
#     <p style="color: #6b7280; font-size: 13px;">
#       Go to Settings → Subscription → paste the key → click Activate
#     </p>
#   </div>
# </div>
# """

# plain = f"""
# Your RetailersPOS License Key
# License Key : {LICENSE_KEY}
# Plan        : {PLAN_LABEL}
# Valid Until : {EXP_DISPLAY}
# Go to Settings → Subscription → paste the key → Activate
# """.strip()


# async def send_email():
#     msg = EmailMessage()
#     msg["Subject"] = "TEST — Your RetailersPOS License Key 🔑"
#     msg["From"] = f"Kennartech RetailersPOS <{MAIL_USERNAME}>"
#     msg["To"] = TO_EMAIL
#     msg.set_content(plain)  # plain-text fallback
#     msg.add_alternative(html, subtype="html")  # HTML version

#     print(f"Sending to {TO_EMAIL} via {MAIL_SERVER}:{MAIL_PORT} ...")
#     try:
#         await aiosmtplib.send(
#             msg,
#             hostname=MAIL_SERVER,
#             port=MAIL_PORT,
#             username=MAIL_USERNAME,
#             password=MAIL_PASSWORD,
#             use_tls=True,  # SSL on port 465
#         )
#         print(" Email sent successfully!")
#     except Exception as e:
#         print(f" Failed: {e}")


# # ── Entry point for a plain script ───────────────────────
# if __name__ == "__main__":
#     asyncio.run(send_email())
