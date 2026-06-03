# license_server/main.py
# ═══════════════════════════════════════════════════════════════
# YOUR ONLINE LICENSE SERVER
# Host this separately on Railway.app.com, Render.com, or any VPS.
# This is NOT part of the desktop app bundle.
# It's a tiny FastAPI app that holds the master license key DB.
#
# Install: pip install fastapi uvicorn sqlmodel paystack
# Run:     uvicorn main:app --host 0.0.0.0 --port 8000
# ═══════════════════════════════════════════════════

# import os
# import hmac
# import hashlib
# import secrets
# import sqlite3
# from pydantic import BaseModel
# from fastapi.responses import JSONResponse
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Request, HTTPException


# app = FastAPI(title="Kennartech License Server")

# DB_PATH = "licenses.db"
# SERVER_SECRET = os.getenv(
#     "LICENSE_SERVER_SECRET", "yk55srf&7q^i@mi+f*tw_%ll$^w@=fwa6&8tr^2qwv1pp"
# )
# PAYSTACK_SECRET = os.getenv(
#     "PAYSTACK_SECRET_KEY", "sk_test_aff26a6f4826ff42199f415d261478071ab220db"
# )


# # ──------- DB SETUP ────────────────────────────────────────────
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


# # ── HELPERS ──────────────────────────────────────────────────────
# def generate_license_key() -> str:
#     """Generate a random license key like: RPOS-XXXX-XXXX-XXXX"""
#     parts = [secrets.token_hex(2).upper() for _ in range(4)]
#     return "RPOS-" + "-".join(parts)


# def plan_to_days(plan: str) -> int:
#     return 365 if plan == "1YEAR" else 183


# # ── MODELS ─────────────────────────────────────────
# class VerifyRequest(BaseModel):
#     license_key: str
#     tenant_id: int


# class CreateLicenseRequest(BaseModel):
#     tenant_id: int
#     plan: str = "6MONTHS"
#     paystack_reference: str | None = None
#     admin_secret: str  # your own admin password to create keys manually


# # ── ROUTES ────────────────────────────────────────


# @app.post("/api/verify-license")
# async def verify_license(body: VerifyRequest):
#     """
#     Called by the desktop app to check if a license key is valid.
#     Returns: {"valid": bool, "message": str, "plan": str, "expires_at": str}
#     """
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

#     if now > expires_at + timedelta(days=3):  # 3-day grace
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
#     YOU call this endpoint manually (or after Paystack webhook confirms payment)
#     to generate and store a new license key.
#     Protected by your admin_secret.
#     """
#     if body.admin_secret != os.getenv(key="ADMIN_SECRET", default="my-admin-secret"):
#         raise HTTPException(status_code=403, detail="Forbidden")

#     key = generate_license_key()
#     days = plan_to_days(body.plan)
#     expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

#     conn = get_db()
#     conn.execute(
#         """INSERT INTO licenses (license_key, tenant_id, plan, expires_at, paystack_reference)
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
#     Paystack calls this automatically when a payment completes.
#     We auto-generate a license key and (in production) email it to the customer.
#     """
#     body = await request.body()
#     signature = request.headers.get("x-paystack-signature", "")

#     # Verify webhook signature
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

#         # Generate license key
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

#         # TODO: Send email with key to customer_email
#         # e.g. send_license_email(customer_email, key, expires_at)
#         print(
#             f"[LICENSE] Generated {key} for tenant={tenant_id} email={customer_email}"
#         )

#     return JSONResponse({"status": "ok"})


# @app.get("/")
# def root():
#     return {"service": "Kennartech License Server", "status": "running"}


# license_server.py
# ═══════════════════════════════════════════════════════════════
# YOUR ONLINE LICENSE SERVER — with email sending
# Host on Railway.app, Render.com, or any VPS.
#
# New environment variables needed on Railway:
#   GMAIL_SENDER     = your Gmail address (e.g. kennartecht@gmail.com)
#   GMAIL_APP_PASSWORD = your Gmail App Password (NOT your normal password)
#
# How to get Gmail App Password:
#   1. Go to myaccount.google.com
#   2. Security → 2-Step Verification (must be ON)
#   3. Security → App passwords
#   4. Select "Mail" and "Windows Computer"
#   5. Copy the 16-character password → paste as GMAIL_APP_PASSWORD
# ═══════════════════════════════════════════════════════════════


# license_server.py
import os
import hmac
import hashlib
import secrets
import asyncio
import sqlite3
import httpx
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, HTTPException


app = FastAPI(title="Kennartech License Server")

DB_PATH = "licenses.db"
PAYSTACK_SECRET = os.getenv(
    key="PAYSTACK_SECRET_KEY",
    default="sk_test_aff26a6f4826ff42199f415d261478071ab220db",
)

# ── RESEND CONFIG ─────────────────────────────────────────────
RESEND_API_KEY = os.getenv(
    key="RESEND_API_KEY", default="re_ZY59J82a_Dd1pzSPVcnXVq6h2ETCWpm1c"
)
RESEND_FROM = (
    "Kennartech RetailersPOS <onboarding@resend.dev>"  # use this until you add a domain
)


# ── DB SETUP ─────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY,
            license_key TEXT UNIQUE NOT NULL,
            tenant_id INTEGER,
            plan TEXT DEFAULT '6MONTHS',
            expires_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            paystack_reference TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# ── HELPERS ──────────────────────────────────────────────────
def generate_license_key() -> str:
    parts = [secrets.token_hex(2).upper() for _ in range(3)]
    return "RPOS-" + "-".join(parts)


def plan_to_days(plan: str) -> int:
    return 365 if plan == "1YEAR" else 183


# ── EMAIL (async with Resend HTTP API) ───────────────────────
async def send_license_email(
    to_email: str, license_key: str, plan: str, expires_at: str
) -> bool:
    print(f"[EMAIL] Sending to {to_email} via Resend...")

    plan_label = "1-Year Plan" if plan == "1YEAR" else "6-Month Plan"

    try:
        exp_dt = datetime.fromisoformat(expires_at)
        exp_display = exp_dt.strftime("%d %B %Y")
    except Exception:
        exp_display = expires_at[:10]

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #1a1d35; padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: #818cf8; margin: 0; font-size: 24px;">RetailersPOS</h1>
        <p style="color: #7b82a8; margin: 8px 0 0;">Powered by Kennartech</p>
      </div>
      <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 12px 12px;">
        <h2 style="color: #1a1d35; margin-top: 0;">Your License Key is Ready! 🎉</h2>
        <p style="color: #444; line-height: 1.6;">
          Thank you for subscribing to RetailersPOS. Your payment was received
          and your license key has been generated below.
        </p>
        <div style="background: #1a1d35; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
          <p style="color: #7b82a8; font-size: 12px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 1px;">
            Your License Key
          </p>
          <p style="color: #818cf8; font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; letter-spacing: 2px;">
            {license_key}
          </p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
          <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Plan</td>
            <td style="padding: 10px 0; color: #1a1d35; font-weight: 600; text-align: right;">{plan_label}</td>
          </tr>
          <tr>
            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Valid Until</td>
            <td style="padding: 10px 0; color: #1a1d35; font-weight: 600; text-align: right;">{exp_display}</td>
          </tr>
        </table>
        <div style="background: #eff6ff; border-left: 4px solid #818cf8; padding: 14px 16px; border-radius: 4px; margin: 20px 0;">
          <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.6;">
            <strong>How to activate:</strong><br>
            1. Open RetailersPOS on your computer<br>
            2. Go to <strong>Settings → Subscription</strong><br>
            3. Paste the key above and click <strong>Activate</strong>
          </p>
        </div>
        <p style="color: #6b7280; font-size: 13px; line-height: 1.6;">
          Need help? Contact us on WhatsApp or reply to this email.<br>
          <strong>Kennartech</strong> — kennartecht@gmail.com
        </p>
      </div>
    </div>
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": RESEND_FROM,
                    "to": [to_email],
                    "subject": "Your RetailersPOS License Key 🔑",
                    "html": html,
                },
                timeout=10.0,
            )

        if response.status_code == 200:
            print(f"[EMAIL] ✅ Sent to {to_email}")
            return True
        else:
            print(f"[EMAIL] ❌ Resend error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"[EMAIL] ❌ Failed: {e}")
        return False


# ── MODELS ───────────────────────────────────────────────────
class VerifyRequest(BaseModel):
    license_key: str
    tenant_id: int


class CreateLicenseRequest(BaseModel):
    tenant_id: int
    plan: str = "6MONTHS"
    paystack_reference: str | None = None
    admin_secret: str


# ── ROUTES ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {"service": "Kennartech License Server", "status": "running"}


@app.post("/api/verify-license")
async def verify_license(body: VerifyRequest):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM licenses WHERE license_key = ?", (body.license_key.upper(),)
    ).fetchone()
    conn.close()

    if not row:
        return {"valid": False, "message": "License key not found."}
    if not row["is_active"]:
        return {"valid": False, "message": "License key has been deactivated."}

    expires_at = datetime.fromisoformat(row["expires_at"])
    now = datetime.now(tz=timezone.utc)

    if now > expires_at + timedelta(days=3):
        return {"valid": False, "message": "License has expired. Please renew."}

    return {
        "valid": True,
        "message": "License is valid.",
        "plan": row["plan"],
        "expires_at": row["expires_at"],
        "paystack_reference": row["paystack_reference"],
    }


@app.post("/api/create-license")
async def create_license(body: CreateLicenseRequest):
    if body.admin_secret != os.getenv(key="ADMIN_SECRET", default="my-admin-secret"):
        raise HTTPException(status_code=403, detail="Forbidden")

    key = generate_license_key()
    days = plan_to_days(body.plan)
    expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

    conn = get_db()
    conn.execute(
        """INSERT INTO licenses
           (license_key, tenant_id, plan, expires_at, paystack_reference)
           VALUES (?, ?, ?, ?, ?)""",
        (key, body.tenant_id, body.plan, expires_at, body.paystack_reference),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "license_key": key,
        "plan": body.plan,
        "expires_at": expires_at,
    }


@app.post("/paystack/webhook")
async def paystack_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    expected = hmac.new(PAYSTACK_SECRET.encode(), body, hashlib.sha512).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json

    data = json.loads(body)

    if data.get("event") == "charge.success":
        meta = data["data"].get("metadata", {})
        tenant_id = meta.get("tenant_id")
        plan = meta.get("plan", "6MONTHS")
        reference = data["data"]["reference"]
        customer_email = data["data"]["customer"]["email"]

        key = generate_license_key()
        days = plan_to_days(plan)
        expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

        conn = get_db()
        conn.execute(
            """INSERT OR REPLACE INTO licenses
               (license_key, tenant_id, plan, expires_at, paystack_reference)
               VALUES (?, ?, ?, ?, ?)""",
            (key, tenant_id, plan, expires_at, reference),
        )
        conn.commit()
        conn.close()

        print(
            f"[LICENSE] Generated {key} for tenant={tenant_id} email={customer_email}"
        )

        asyncio.create_task(
            send_license_email(
                to_email=customer_email,
                license_key=key,
                plan=plan,
                expires_at=expires_at,
            )
        )

    return JSONResponse({"status": "ok"})


# import os
# import hmac
# import smtplib
# import hashlib
# import secrets
# import sqlite3
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
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


# def send_license_email(to_email: str, license_key: str, plan: str, expires_at: str,) -> bool:
#     print(f"[EMAIL] Attempting to send to {to_email}, sender={GMAIL_SENDER}, has_password={bool(GMAIL_APP_PASSWORD)}")
#     """
#     Sends the license key to the client's email via Gmail SMTP.
#     Returns True if sent successfully, False if failed.
#     """
#     if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
#         print("[EMAIL] Gmail credentials not configured — skipping email.")
#         return False

#     plan_label = "1-Year Plan" if plan == "1YEAR" else "6-Month Plan"

#     # Parse expiry date for display
#     try:
#         exp_dt = datetime.fromisoformat(expires_at)
#         exp_display = exp_dt.strftime("%d %B %Y")
#     except Exception:
#         exp_display = expires_at[:10]

#     # ── Email HTML body ──────────────────────────────────────
#     html = f"""
#     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

#       <div style="background: #1a1d35; padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
#         <h1 style="color: #818cf8; margin: 0; font-size: 24px;">RetailersPOS</h1>
#         <p style="color: #7b82a8; margin: 8px 0 0;">Powered by Kennartech</p>
#       </div>

#       <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 12px 12px;">

#         <h2 style="color: #1a1d35; margin-top: 0;">Your License Key is Ready! </h2>

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

#     # Plain text fallback
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

#     # ── Build and send the email ─────────────────────────────
#     try:
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = "Your RetailersPOS License Key"
#         msg["From"] = f"Kennartech RetailersPOS <{GMAIL_SENDER}>"
#         msg["To"] = to_email

#         msg.attach(MIMEText(plain, "plain"))
#         msg.attach(MIMEText(html, "html"))

#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
#             server.sendmail(GMAIL_SENDER, to_email, msg.as_string())

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
#     """Manually create a license key — protected by admin_secret."""
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
#     Paystack calls this after a successful payment.
#     Generates a license key and emails it to the client.
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

#         # Save to database
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

#         # ── Send the key to the client's email ──────────────
#         send_license_email(
#             to_email=customer_email,
#             license_key=key,
#             plan=plan,
#             expires_at=expires_at,
#         )

#     return JSONResponse({"status": "ok"})
