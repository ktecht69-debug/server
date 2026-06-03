# license_server.py
# import os
# import hmac
# import hashlib
# import secrets
# import asyncio
# import sqlite3
# from email.message import EmailMessage
# import aiosmtplib
# from pydantic import BaseModel
# from fastapi.responses import JSONResponse
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Request, HTTPException


# app = FastAPI(title="Kennartech License Server")

# DB_PATH = "licenses.db"
# PAYSTACK_SECRET = os.getenv(key="PAYSTACK_SECRET_KEY", default="")

# # ── EMAIL CONFIG ─────────────────────────────────────────────
# GMAIL_SENDER = os.getenv(key="GMAIL_SENDER", default="kennartecht@gmail.com")
# GMAIL_APP_PASSWORD = os.getenv(key="GMAIL_APP_PASSWORD", default="hwnu ujaf aayq kohj")


# # ── DB SETUP ─────────────────────────────────────────────────
# def get_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# def init_db():
#     conn = get_db()
#     conn.execute(
#         """
#         CREATE TABLE IF NOT EXISTS licenses (
#             id INTEGER PRIMARY KEY,
#             license_key TEXT UNIQUE NOT NULL,
#             tenant_id INTEGER,
#             plan TEXT DEFAULT '6MONTHS',
#             expires_at TEXT NOT NULL,
#             is_active INTEGER DEFAULT 1,
#             paystack_reference TEXT,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP
#         )
#     """
#     )
#     conn.commit()
#     conn.close()


# init_db()


# # ── HELPERS ──────────────────────────────────────────────────
# def generate_license_key() -> str:
#     parts = [secrets.token_hex(2).upper() for _ in range(3)]
#     return "RPOS-" + "-".join(parts)


# def plan_to_days(plan: str) -> int:
#     return 365 if plan == "1YEAR" else 183


# # ── EMAIL (async with aiosmtplib) ────────────────────────────
# async def send_license_email(
#     to_email: str, license_key: str, plan: str, expires_at: str
# ) -> bool:
#     print(
#         f"[EMAIL] Attempting to send to {to_email}, sender={GMAIL_SENDER}, has_password={bool(GMAIL_APP_PASSWORD)}"
#     )

#     if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
#         print("[EMAIL] Gmail credentials not configured — skipping email.")
#         return False

#     plan_label = "1-Year Plan" if plan == "1YEAR" else "6-Month Plan"

#     try:
#         exp_dt = datetime.fromisoformat(expires_at)
#         exp_display = exp_dt.strftime("%d %B %Y")
#     except Exception:
#         exp_display = expires_at[:10]

#     html = f"""
#     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
#       <div style="background: #1a1d35; padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
#         <h1 style="color: #818cf8; margin: 0; font-size: 24px;">RetailersPOS</h1>
#         <p style="color: #7b82a8; margin: 8px 0 0;">Powered by Kennartech</p>
#       </div>
#       <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 12px 12px;">
#         <h2 style="color: #1a1d35; margin-top: 0;">Your License Key is Ready! 🎉</h2>
#         <p style="color: #444; line-height: 1.6;">
#           Thank you for subscribing to RetailersPOS. Your payment was received
#           and your license key has been generated below.
#         </p>
#         <div style="background: #1a1d35; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
#           <p style="color: #7b82a8; font-size: 12px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 1px;">
#             Your License Key
#           </p>
#           <p style="color: #818cf8; font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; letter-spacing: 2px;">
#             {license_key}
#           </p>
#         </div>
#         <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
#           <tr style="border-bottom: 1px solid #e5e7eb;">
#             <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Plan</td>
#             <td style="padding: 10px 0; color: #1a1d35; font-weight: 600; text-align: right;">{plan_label}</td>
#           </tr>
#           <tr>
#             <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Valid Until</td>
#             <td style="padding: 10px 0; color: #1a1d35; font-weight: 600; text-align: right;">{exp_display}</td>
#           </tr>
#         </table>
#         <div style="background: #eff6ff; border-left: 4px solid #818cf8; padding: 14px 16px; border-radius: 4px; margin: 20px 0;">
#           <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.6;">
#             <strong>How to activate:</strong><br>
#             1. Open RetailersPOS on your computer<br>
#             2. Go to <strong>Settings → Subscription</strong><br>
#             3. Paste the key above and click <strong>Activate</strong>
#           </p>
#         </div>
#         <p style="color: #6b7280; font-size: 13px; line-height: 1.6;">
#           Need help? Contact us on WhatsApp or reply to this email.<br>
#           <strong>Kennartech</strong> — kennartecht@gmail.com
#         </p>
#       </div>
#     </div>
#     """

#     plain = f"""
# Your RetailersPOS License Key

# License Key : {license_key}
# Plan        : {plan_label}
# Valid Until : {exp_display}

# To activate:
# 1. Open RetailersPOS
# 2. Go to Settings → Subscription
# 3. Enter the key above and click Activate

# Need help? Contact Kennartech: kennartecht@gmail.com
#     """.strip()

#     try:
#         msg = EmailMessage()
#         msg["Subject"] = "Your RetailersPOS License Key 🔑"
#         msg["From"] = f"Kennartech RetailersPOS <{GMAIL_SENDER}>"
#         msg["To"] = to_email
#         msg.set_content(plain)  # plain-text fallback
#         msg.add_alternative(html, subtype="html")  # HTML version

#         await aiosmtplib.send(
#             msg,
#             hostname="smtp.gmail.com",
#             port=465,
#             username=GMAIL_SENDER,
#             password=GMAIL_APP_PASSWORD,
#             use_tls=True,  # SSL on port 465
#         )

#         print(f"[EMAIL] License key sent to {to_email}")
#         return True

#     except Exception as e:
#         print(f"[EMAIL] Failed to send email to {to_email}: {e}")
#         return False


# # ── MODELS ───────────────────────────────────────────────────
# class VerifyRequest(BaseModel):
#     license_key: str
#     tenant_id: int


# class CreateLicenseRequest(BaseModel):
#     tenant_id: int
#     plan: str = "6MONTHS"
#     paystack_reference: str | None = None
#     admin_secret: str


# # ── ROUTES ───────────────────────────────────────────────────
# @app.get("/")
# def root():
#     return {"service": "Kennartech License Server", "status": "running"}


# @app.post("/api/verify-license")
# async def verify_license(body: VerifyRequest):
#     conn = get_db()
#     row = conn.execute(
#         "SELECT * FROM licenses WHERE license_key = ?", (body.license_key.upper(),)
#     ).fetchone()
#     conn.close()

#     if not row:
#         return {"valid": False, "message": "License key not found."}
#     if not row["is_active"]:
#         return {"valid": False, "message": "License key has been deactivated."}

#     expires_at = datetime.fromisoformat(row["expires_at"])
#     now = datetime.now(tz=timezone.utc)

#     if now > expires_at + timedelta(days=3):
#         return {"valid": False, "message": "License has expired. Please renew."}

#     return {
#         "valid": True,
#         "message": "License is valid.",
#         "plan": row["plan"],
#         "expires_at": row["expires_at"],
#         "paystack_reference": row["paystack_reference"],
#     }


# @app.post("/api/create-license")
# async def create_license(body: CreateLicenseRequest):
#     if body.admin_secret != os.getenv(key="ADMIN_SECRET", default="my-admin-secret"):
#         raise HTTPException(status_code=403, detail="Forbidden")

#     key = generate_license_key()
#     days = plan_to_days(body.plan)
#     expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

#     conn = get_db()
#     conn.execute(
#         """INSERT INTO licenses
#            (license_key, tenant_id, plan, expires_at, paystack_reference)
#            VALUES (?, ?, ?, ?, ?)""",
#         (key, body.tenant_id, body.plan, expires_at, body.paystack_reference),
#     )
#     conn.commit()
#     conn.close()

#     return {
#         "success": True,
#         "license_key": key,
#         "plan": body.plan,
#         "expires_at": expires_at,
#     }


# @app.post("/paystack/webhook")
# async def paystack_webhook(request: Request):
#     body = await request.body()
#     signature = request.headers.get("x-paystack-signature", "")

#     expected = hmac.new(PAYSTACK_SECRET.encode(), body, hashlib.sha512).hexdigest()

#     if not hmac.compare_digest(expected, signature):
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     import json

#     data = json.loads(body)

#     if data.get("event") == "charge.success":
#         meta = data["data"].get("metadata", {})
#         tenant_id = meta.get("tenant_id")
#         plan = meta.get("plan", "6MONTHS")
#         reference = data["data"]["reference"]
#         customer_email = data["data"]["customer"]["email"]

#         key = generate_license_key()
#         days = plan_to_days(plan)
#         expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

#         conn = get_db()
#         conn.execute(
#             """INSERT OR REPLACE INTO licenses
#                (license_key, tenant_id, plan, expires_at, paystack_reference)
#                VALUES (?, ?, ?, ?, ?)""",
#             (key, tenant_id, plan, expires_at, reference),
#         )
#         conn.commit()
#         conn.close()

#         print(
#             f"[LICENSE] Generated {key} for tenant={tenant_id} email={customer_email}"
#         )

#         # ── Non-blocking: send email without holding up the webhook response ──
#         asyncio.create_task(
#             send_license_email(
#                 to_email=customer_email,
#                 license_key=key,
#                 plan=plan,
#                 expires_at=expires_at,
#             )
#         )

#     return JSONResponse({"status": "ok"})
