# # license_server/main.py
# import os
# import json
# import hmac
# import httpx
# import hashlib
# import secrets
# import asyncio
# import psycopg2
# from pydantic import BaseModel
# from psycopg2.extras import RealDictCursor
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import JSONResponse, HTMLResponse
# from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded


# app = FastAPI(title="Kennartech License Server")


# # ── Rate limiter — IP-based, in-memory (fine for a single Railway instance) ──
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# PAYSTACK_SECRET = os.getenv(key="PAYSTACK_SECRET_KEY", default="")
# RESEND_API_KEY = os.getenv(key="RESEND_API_KEY", default="")
# DATABASE_URL = os.getenv(key="DATABASE_URL", default="")
# RESEND_FROM = "Kennartech RetailersPOS <onboarding@resend.dev>"


# # ── Ed25519 signing key — proves a license row was issued by THIS server ──
# SIGNING_PRIVATE_KEY_HEX = os.getenv(key="LICENSE_SIGNING_PRIVATE_KEY", default="")
# if not SIGNING_PRIVATE_KEY_HEX:
#     raise RuntimeError("LICENSE_SIGNING_PRIVATE_KEY env var is not set!")

# _signing_key = Ed25519PrivateKey.from_private_bytes(
#     bytes.fromhex(SIGNING_PRIVATE_KEY_HEX)
# )


# def sign_license(
#     tenant_id: int, license_key: str, plan: str, expires_at: datetime, is_active: bool
# ) -> str:
#     """Signs the license fields so the client can detect local tampering."""
#     message = f"{tenant_id}|{license_key}|{plan}|{int(expires_at.timestamp())}|{1 if is_active else 0}"
#     signature = _signing_key.sign(message.encode())
#     return signature.hex()


# def get_db():
#     return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# def init_db():
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute(
#         query="""
#         CREATE TABLE IF NOT EXISTS licenses (
#             id                 SERIAL PRIMARY KEY,
#             license_key        TEXT UNIQUE NOT NULL,
#             tenant_id          INTEGER,
#             plan               TEXT DEFAULT '6MONTHS',
#             expires_at         TIMESTAMPTZ NOT NULL,
#             is_active          INTEGER DEFAULT 1,
#             paystack_reference TEXT,
#             created_at         TIMESTAMPTZ DEFAULT NOW()
#         )
#     """
#     )
#     # ── Tracks which hardware devices have already used their free trial ──
#     cur.execute(
#         query="""
#         CREATE TABLE IF NOT EXISTS trial_devices (
#             id          SERIAL PRIMARY KEY,
#             fingerprint TEXT UNIQUE NOT NULL,
#             tenant_id   INTEGER,
#             license_key TEXT,
#             created_at  TIMESTAMPTZ DEFAULT NOW()
#         )
#     """
#     )
#     conn.commit()
#     cur.close()
#     conn.close()


# init_db()


# def generate_license_key() -> str:
#     """Generates RPOS-XXXX-XXXX-XXXX (19 chars, 4 groups)"""
#     parts = [secrets.token_hex(2).upper() for _ in range(3)]
#     return "RPOS-" + "-".join(parts)


# def plan_to_days(plan: str) -> int:
#     if plan == "1YEAR":
#         return 365
#     if plan == "TRIAL":
#         return 30
#     return 183


# # ────── Email via Resend http API ─────────────
# async def send_license_email(
#     to_email: str, license_key: str, plan: str, expires_at: str
# ) -> bool:
#     if not RESEND_API_KEY:
#         print("[EMAIL] RESEND_API_KEY not set — skipping.")
#         return False

#     plan_label = "1-Year Plan" if plan == "1YEAR" else "6-Month Plan"
#     try:
#         exp_display = datetime.fromisoformat(expires_at).strftime("%d %B %Y")
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
#         <p style="color: #444;">Thank you for subscribing to RetailersPOS.</p>
#         <div style="background: #1a1d35; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
#           <p style="color: #7b82a8; font-size: 12px; margin: 0 0 8px;">YOUR LICENSE KEY</p>
#           <p style="color: #818cf8; font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; letter-spacing: 2px;">
#             {license_key}
#           </p>
#         </div>
#         <p>Plan: <strong>{plan_label}</strong></p>
#         <p>Valid Until: <strong>{exp_display}</strong></p>
#         <div style="background: #eff6ff; border-left: 4px solid #818cf8; padding: 14px 16px; border-radius: 4px; margin: 20px 0;">
#           <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.6;">
#             <strong>How to activate:</strong><br>
#             1. Open RetailersPOS<br>
#             2. Go to <strong>Settings → Subscription</strong><br>
#             3. Paste the key and click <strong>Activate</strong>
#           </p>
#         </div>
#         <p style="color: #6b7280; font-size: 13px;">
#           Need help? Contact <strong>Kennartech</strong> — kennartecht@gmail.com
#         </p>
#       </div>
#     </div>
#     """
#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             resp = await client.post(
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
#         if resp.status_code == 200:
#             print(f"[EMAIL] Sent to {to_email}")
#             return True
#         return False
#     except Exception as e:
#         print(f"[EMAIL] {e}")
#         return False


# # ──────── Models ─────────────
# class VerifyRequest(BaseModel):
#     license_key: str
#     tenant_id: int


# class CreateLicenseRequest(BaseModel):
#     tenant_id: int
#     plan: str = "6MONTHS"
#     paystack_reference: str | None = None
#     admin_secret: str


# class StartTrialRequest(BaseModel):
#     tenant_id: int
#     fingerprint: str


# @app.get(path="/")
# def root():
#     return {"service": "Kennartech License Server", "status": "running"}


# # ── Rate limited: 10 requests per minute per IP ─────────────────
# # Stops someone from scripting license-key guesses against this endpoint.
# # A legitimate client only calls this on activation + once every 7 days
# # for the soft re-verify, so 10/minute is generous for real usage but
# # tight enough to make brute-forcing keys impractical.
# @app.post(path="/api/verify-license")
# @limiter.limit("10/minute")
# async def verify_license(request: Request, body: VerifyRequest):
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT * FROM licenses WHERE license_key = %s", (body.license_key.upper(),)
#     )
#     row = cur.fetchone()

#     if not row:
#         cur.close()
#         conn.close()
#         return {"valid": False, "message": "License key not found."}

#     if not row["is_active"]:
#         cur.close()
#         conn.close()
#         return {"valid": False, "message": "License key has been deactivated."}

#     # ───────── Key already claimed by another tenant ───────────────
#     if row["tenant_id"] is not None and row["tenant_id"] != body.tenant_id:
#         cur.close()
#         conn.close()
#         return {
#             "valid": False,
#             "message": "This key is already activated on another account.",
#         }

#     # ───── First time activation - bind key to this tenant ─────
#     if row["tenant_id"] is None:
#         cur.execute(
#             "UPDATE licenses SET tenant_id = %s WHERE license_key = %s",
#             (body.tenant_id, body.license_key.upper()),
#         )
#         conn.commit()

#     cur.close()
#     conn.close()

#     expires_at = row["expires_at"]
#     if expires_at.tzinfo is None:
#         expires_at = expires_at.replace(tzinfo=timezone.utc)
#     now = datetime.now(tz=timezone.utc)

#     if now > expires_at + timedelta(days=3):
#         return {"valid": False, "message": "License has expired. Please renew."}

#     # ── Sign the response so the client can detect local tampering ──
#     signature = sign_license(
#         tenant_id=body.tenant_id,
#         license_key=row["license_key"],
#         plan=row["plan"],
#         expires_at=expires_at,
#         is_active=bool(row["is_active"]),
#     )

#     return {
#         "valid": True,
#         "message": "License is valid.",
#         "plan": row["plan"],
#         "expires_at": row["expires_at"].isoformat(),
#         "paystack_reference": row["paystack_reference"],
#         "signature": signature,
#     }


# # ── Rate limited: 20 requests per minute per IP ─────────────────
# # Already gated by admin_secret, but this adds a second layer so
# # someone can't hammer this endpoint trying to brute-force that secret.
# @app.post(path="/api/create-license")
# @limiter.limit("20/minute")
# async def create_license(request: Request, body: CreateLicenseRequest):
#     if body.admin_secret != os.getenv(key="ADMIN_SECRET", default="my-admin-secret"):
#         raise HTTPException(status_code=403, detail="Forbidden")

#     key = generate_license_key()
#     expires_at = datetime.now(tz=timezone.utc) + timedelta(days=plan_to_days(body.plan))

#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute(
#         """INSERT INTO licenses (license_key, tenant_id, plan, expires_at, paystack_reference)
#            VALUES (%s, %s, %s, %s, %s)""",
#         (key, body.tenant_id, body.plan, expires_at, body.paystack_reference),
#     )
#     conn.commit()
#     cur.close()
#     conn.close()

#     return {
#         "success": True,
#         "license_key": key,
#         "plan": body.plan,
#         "expires_at": expires_at.isoformat(),
#     }


# # ── Rate limited: 5 requests per minute per IP ──────────────────
# # Stops someone spamming fake trial requests, especially since each
# # successful call writes a new row to trial_devices/licenses in Postgres.
# @app.post(path="/api/start-trial")
# @limiter.limit("5/minute")
# async def start_trial(request: Request, body: StartTrialRequest):
#     """
#     Called by the desktop app on first launch.
#     Checks this device's hardware fingerprint against every device that's
#     ever had a free trial. One trial per device, no matter how many times
#     the app is reinstalled or how many tenant IDs get created on it.
#     """
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         "SELECT * FROM trial_devices WHERE fingerprint = %s", (body.fingerprint,)
#     )
#     existing = cur.fetchone()

#     if existing:
#         cur.close()
#         conn.close()
#         return {
#             "success": False,
#             "message": "This device has already used its free trial.",
#         }

#     key = generate_license_key()
#     expires_at = datetime.now(tz=timezone.utc) + timedelta(days=plan_to_days("TRIAL"))

#     cur.execute(
#         """INSERT INTO licenses (license_key, tenant_id, plan, expires_at)
#            VALUES (%s, %s, %s, %s)""",
#         (key, body.tenant_id, "TRIAL", expires_at),
#     )
#     cur.execute(
#         """INSERT INTO trial_devices (fingerprint, tenant_id, license_key)
#            VALUES (%s, %s, %s)""",
#         (body.fingerprint, body.tenant_id, key),
#     )
#     conn.commit()
#     cur.close()
#     conn.close()

#     # ── Sign this response too ──
#     signature = sign_license(
#         tenant_id=body.tenant_id,
#         license_key=key,
#         plan="TRIAL",
#         expires_at=expires_at,
#         is_active=True,
#     )

#     return {
#         "success": True,
#         "license_key": key,
#         "plan": "TRIAL",
#         "expires_at": expires_at.isoformat(),
#         "signature": signature,
#     }


# # ── NOT rate limited: Paystack's own servers call this endpoint ──
# # Limiting it risks silently dropping legitimate payment notifications.
# # It's already protected by HMAC signature verification below, which is
# # a stronger guarantee than a rate limit — an attacker without your
# # Paystack secret can't produce a valid signature no matter how many
# # requests they send.
# @app.post(path="/paystack/webhook")
# async def paystack_webhook(request: Request):
#     body = await request.body()
#     signature_header = request.headers.get("x-paystack-signature", "")
#     expected = hmac.new(PAYSTACK_SECRET.encode(), body, hashlib.sha512).hexdigest()

#     if not hmac.compare_digest(expected, signature_header):
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     data = json.loads(body)

#     if data.get("event") == "charge.success":
#         meta = data["data"].get("metadata", {})
#         tenant_id = meta.get("tenant_id")
#         plan = meta.get("plan", "6MONTHS")
#         reference = data["data"]["reference"]
#         customer_email = data["data"]["customer"]["email"]

#         conn = get_db()
#         cur = conn.cursor()

#         # ── Gap 2: Idempotency — skip if this payment was already processed ──
#         cur.execute(
#             "SELECT id FROM licenses WHERE paystack_reference = %s", (reference,)
#         )
#         if cur.fetchone():
#             cur.close()
#             conn.close()
#             print(f"[WEBHOOK] Duplicate reference {reference} — skipping.")
#             return JSONResponse({"status": "ok"})

#         # ── Gap 1: Extend from current expiry if subscription still active ──
#         base_date = datetime.now(tz=timezone.utc)
#         if tenant_id:
#             cur.execute(
#                 """
#                 SELECT expires_at FROM licenses
#                 WHERE tenant_id = %s AND is_active = 1
#                 ORDER BY expires_at DESC
#                 LIMIT 1
#                 """,
#                 (tenant_id,),
#             )
#             existing = cur.fetchone()
#             if existing:
#                 current_expiry = existing["expires_at"]
#                 if current_expiry.tzinfo is None:
#                     current_expiry = current_expiry.replace(tzinfo=timezone.utc)
#                 if current_expiry > base_date:
#                     base_date = current_expiry  # extend from current expiry
#                     print(
#                         f"[LICENSE] Extending from {current_expiry.date()} for tenant={tenant_id}"
#                     )

#         expires_at = base_date + timedelta(days=plan_to_days(plan=plan))

#         key = generate_license_key()
#         cur.execute(
#             """INSERT INTO licenses (license_key, tenant_id, plan, expires_at, paystack_reference)
#                VALUES (%s, %s, %s, %s, %s)
#                ON CONFLICT (license_key) DO NOTHING""",
#             (key, tenant_id, plan, expires_at, reference),
#         )
#         conn.commit()
#         cur.close()
#         conn.close()

#         print(
#             f"[LICENSE] Generated {key} for tenant={tenant_id} email={customer_email} expires={expires_at.date()}"
#         )

#         asyncio.create_task(
#             send_license_email(
#                 to_email=customer_email,
#                 license_key=key,
#                 plan=plan,
#                 expires_at=expires_at.isoformat(),
#             )
#         )

#     return JSONResponse({"status": "ok"})


# @app.get(path="/licensing/paystack/callback")
# async def paystack_callback(request: Request):
#     reference = request.query_params.get("trxref") or request.query_params.get(
#         "reference"
#     )
#     local_port = request.query_params.get("local_port", "")

#     if local_port:
#         redirect_target = f"http://127.0.0.1:{local_port}/licensing/subscription"
#     else:
#         redirect_target = ""

#     return HTMLResponse(
#         content=f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#   <meta charset="UTF-8">
#   <title>Payment Successful</title>
#   <style>
#     ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
#     ::-webkit-scrollbar-track {{ background: transparent; }}
#     ::-webkit-scrollbar-thumb {{ background: rgba(46,204,113,0.3); border-radius: 10px; }}
#     ::-webkit-scrollbar-thumb:hover {{ background: rgba(46,204,113,1.0); }}

#     * {{ box-sizing: border-box; margin: 0; padding: 0; }}

#     body {{
#       font-family: Arial, sans-serif;
#       background: #d4edda;
#       min-height: 100vh;
#       display: flex;
#       align-items: center;
#       justify-content: center;
#       padding: 16px;
#     }}

#     .card {{
#       background: white;
#       border-radius: 12px;
#       padding: 28px 24px;
#       max-width: 380px;
#       width: 100%;
#       box-shadow: 0 4px 20px rgba(0,0,0,0.08);
#       text-align: center;
#     }}

#     .icon {{ font-size: 40px; margin-bottom: 8px; }}

#     h2 {{
#       color: #1a1d35;
#       font-size: 18px;
#       margin-bottom: 6px;
#     }}

#     .sub {{
#       color: #6b7280;
#       font-size: 12px;
#       line-height: 1.5;
#       margin-bottom: 10px;
#     }}

#     .ref {{
#       display: inline-block;
#       background: #f1f5f9;
#       padding: 4px 12px;
#       border-radius: 6px;
#       font-family: monospace;
#       font-size: 11px;
#       color: #475569;
#       margin-bottom: 12px;
#     }}

#     .steps {{
#       background: #eff6ff;
#       border-left: 3px solid #818cf8;
#       border-radius: 4px;
#       padding: 10px 12px;
#       text-align: left;
#       margin-bottom: 14px;
#     }}

#     .steps p {{
#       color: #1e40af;
#       font-size: 11px;
#       line-height: 1.7;
#       margin: 0;
#     }}

#     .btn {{
#       width: 100%;
#       padding: 11px;
#       background: #1a7a4a;
#       color: white;
#       border: none;
#       border-radius: 8px;
#       font-size: 13px;
#       font-weight: bold;
#       cursor: pointer;
#       margin-bottom: 8px;
#     }}

#     .btn:hover {{ background: #155f3a; }}

#     .timer {{
#       font-size: 11px;
#       color: #9ca3af;
#       margin-bottom: 10px;
#     }}

#     .footer {{
#       font-size: 10px;
#       color: #d1d5db;
#       margin-top: 6px;
#     }}
#   </style>
# </head>
# <body>
#   <div class="card">
#     <div class="icon"></div>
#     <h2>Payment Successful!</h2>
#     <p class="sub">
#       Your license key has been sent to your email.<br>
#       Check your <strong>inbox</strong> and <strong>spam folder</strong>.
#     </p>
#     <p style="color: #dc2626; font-size: 11px; margin-top: 8px;">
#       ⚠️ If you don't see the email, check your <strong>Spam</strong> and <strong>Promotions</strong> folders.
#     </p>

#     <div class="ref">Ref: {reference or 'N/A'}</div>

#     <div class="steps">
#       <p>
#         <strong>Next steps:</strong><br>
#         1. Check your email for the license key<br>
#         2. Copy the key (RPOS-XXXX-XXXX-XXXX)<br>
#         3. Go to RetailersPOS → Subscription<br>
#         4. Paste the key and click <strong>Activate</strong>
#       </p>
#     </div>

#     {"" if not redirect_target else f'''
#     <button class="btn" onclick="goToApp()">➜ Go to Subscription Page</button>
#     <p class="timer">Redirecting in <span id="count">10</span> seconds...</p>
#     '''}

#     <p class="footer">Powered by Kennartech</p>
#   </div>

#   {"" if not redirect_target else f'''
#   <script>
#     var seconds = 10;
#     var target = "{redirect_target}";
#     var interval = setInterval(function() {{
#       seconds--;
#       var el = document.getElementById("count");
#       if (el) el.textContent = seconds;
#       if (seconds <= 0) {{ clearInterval(interval); goToApp(); }}
#     }}, 1000);
#     function goToApp() {{ window.location.href = target; }}
#   </script>
#   '''}
# </body>
# </html>
# """
#     )