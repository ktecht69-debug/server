# test_resend.py
# import resend

# resend.api_key = "re_GJb9L7od_M8zTzqupbudxUWgvNrfbkPZ1"

# LICENSE_KEY = "RPOS-TEST-1234-ABCD"
# PLAN_LABEL = "6-Month Plan"
# EXP_DISPLAY = "02 December 2026"
# TO_EMAIL = "kennartecht@gmail.com"

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

# params: resend.Emails.SendParams = {
#     "from": "Kennartech RetailersPOS <onboarding@resend.dev>",
#     "to": [TO_EMAIL],
#     "subject": "TEST — Your RetailersPOS License Key",
#     "html": html,
# }

# try:
#     email = resend.Emails.send(params)
#     print(f" Resend success! Email ID: {email['id']}")
# except Exception as e:
#     print(f" Resend failed: {e}")


# ====== THIS IS FOR SQLIGHT NOTE ======================
# license_server/main.py
# import os
# import hmac
# import hashlib
# import secrets
# import asyncio
# import sqlite3
# import httpx
# from pydantic import BaseModel
# from fastapi.responses import JSONResponse
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Request, HTTPException


# app = FastAPI(title="Kennartech License Server")

# DB_PATH = "licenses.db"

# # ── CONFIG — all from Railway environment variables ──────────
# PAYSTACK_SECRET = os.getenv(
#     key="PAYSTACK_SECRET_KEY",
#     default="sk_test_aff26a6f4826ff42199f415d261478071ab220db",
# )
# RESEND_API_KEY = os.getenv(
#     key="RESEND_API_KEY", default="re_GJb9L7od_M8zTzqupbudxUWgvNrfbkPZ1"
# )

# # From address — change to your own domain once you verify one on Resend
# # For now onboarding@resend.dev works for testing
# RESEND_FROM = "Kennartech RetailersPOS <onboarding@resend.dev>"


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
#     """Generates RPOS-XXXX-XXXX-XXXX (19 chars, 4 groups)"""
#     parts = [secrets.token_hex(2).upper() for _ in range(3)]
#     return "RPOS-" + "-".join(parts)


# def plan_to_days(plan: str) -> int:
#     return 365 if plan == "1YEAR" else 183


# # ── EMAIL via Resend HTTP API ────────────────────────────────
# async def send_license_email(
#     to_email: str,
#     license_key: str,
#     plan: str,
#     expires_at: str,
# ) -> bool:
#     """
#     Sends license key email via Resend API (HTTPS — Railway never blocks this).
#     Runs as a background task — never blocks the webhook response.
#     """
#     print(f"[EMAIL] Sending to {to_email} via Resend...")

#     if not RESEND_API_KEY:
#         print("[EMAIL] RESEND_API_KEY not set — skipping email.")
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

#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.post(
#                 "https://api.resend.com/emails",
#                 headers={
#                     "Authorization": f"Bearer {RESEND_API_KEY}",
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "from": RESEND_FROM,
#                     "to": [to_email],
#                     "subject": "Your RetailersPOS License Key",
#                     "html": html,
#                 },
#             )

#         if response.status_code == 200:
#             data = response.json()
#             print(f"[EMAIL] Sent to {to_email} — ID: {data.get('id')}")
#             return True
#         else:
#             print(f"[EMAIL] Resend error {response.status_code}: {response.text}")
#             return False

#     except Exception as e:
#         print(f"[EMAIL] Failed: {e}")
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
#     """Called by desktop app to check if a license key is valid."""
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
#     """
#     Manually create a license key.
#     You call this yourself after confirming payment outside Paystack webhook.
#     Protected by ADMIN_SECRET.
#     """
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
#     """
#     Paystack calls this automatically after a successful payment.
#     Generates a license key, saves it, then emails it to the client.
#     Email runs as a background task so it never delays the webhook response.
#     """
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

#         # Save license to database
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

#         # Send email in background — doesn't block the webhook response
#         asyncio.create_task(
#             send_license_email(
#                 to_email=customer_email,
#                 license_key=key,
#                 plan=plan,
#                 expires_at=expires_at,
#             )
#         )

#     return JSONResponse({"status": "ok"})


# ==================== For testing fast API locally NOTE ===============
# license_server.py
# import os
# import hmac
# import hashlib
# import secrets
# import asyncio
# import sqlite3
# import httpx
# import uvicorn
# from pydantic import BaseModel
# from fastapi.responses import JSONResponse
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Request, HTTPException


# app = FastAPI(title="Kennartech License Server")

# DB_PATH = "licenses.db"
# PAYSTACK_SECRET = os.getenv(
#     key="PAYSTACK_SECRET_KEY",
#     default="sk_test_aff26a6f4826ff42199f415d261478071ab220db",
# )

# # ── RESEND CONFIG ─────────────────────────────────────────────
# RESEND_API_KEY = os.getenv(
#     key="RESEND_API_KEY", default="re_ZY59J82a_Dd1pzSPVcnXVq6h2ETCWpm1c"
# )
# RESEND_FROM = (
#     "Kennartech RetailersPOS <onboarding@resend.dev>"  # use this until you add a domain
# )


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


# # ── EMAIL (async with Resend HTTP API) ───────────────────────
# async def send_license_email(
#     to_email: str, license_key: str, plan: str, expires_at: str
# ) -> bool:
#     print(f"[EMAIL] Sending to {to_email} via Resend...")

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

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "https://api.resend.com/emails",
#                 headers={
#                     "Authorization": f"Bearer {RESEND_API_KEY}",
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "from": RESEND_FROM,
#                     "to": [to_email],
#                     "subject": "Your RetailersPOS License Key",
#                     "html": html,
#                 },
#                 timeout=10.0,
#             )

#         if response.status_code == 200:
#             print(f"[EMAIL] Sent to {to_email}")
#             return True
#         else:
#             print(f"[EMAIL] Resend error {response.status_code}: {response.text}")
#             return False

#     except Exception as e:
#         print(f"[EMAIL] Failed: {e}")
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

#         asyncio.create_task(
#             send_license_email(
#                 to_email=customer_email,
#                 license_key=key,
#                 plan=plan,
#                 expires_at=expires_at,
#             )
#         )

#     return JSONResponse({"status": "ok"})


# if __name__ == "__main__":
#     uvicorn.run("license_server:app", host="127.0.0.1", port=8000, reload=True)


# http://127.0.0.1:8000/docs
