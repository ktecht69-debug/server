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

import os
import hmac
import hashlib
import secrets
import sqlite3
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, HTTPException


app = FastAPI(title="Kennartech License Server")

DB_PATH = "licenses.db"
SERVER_SECRET = os.getenv("LICENSE_SERVER_SECRET", "change-this-secret-in-production")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY", "")


# ──------- DB SETUP ────────────────────────────────────────────
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


# ── HELPERS ──────────────────────────────────────────────────────
def generate_license_key() -> str:
    """Generate a random license key like: RPOS-XXXX-XXXX-XXXX"""
    parts = [secrets.token_hex(2).upper() for _ in range(4)]
    return "RPOS-" + "-".join(parts)


def plan_to_days(plan: str) -> int:
    return 365 if plan == "1YEAR" else 183


# ── MODELS ─────────────────────────────────────────
class VerifyRequest(BaseModel):
    license_key: str
    tenant_id: int


class CreateLicenseRequest(BaseModel):
    tenant_id: int
    plan: str = "6MONTHS"
    paystack_reference: str | None = None
    admin_secret: str  # your own admin password to create keys manually


# ── ROUTES ────────────────────────────────────────


@app.post(rule="/api/verify-license")
async def verify_license(body: VerifyRequest):
    """
    Called by the desktop app to check if a license key is valid.
    Returns: {"valid": bool, "message": str, "plan": str, "expires_at": str}
    """
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

    if now > expires_at + timedelta(days=3):  # 3-day grace
        return {"valid": False, "message": "License has expired. Please renew."}

    return {
        "valid": True,
        "message": "License is valid.",
        "plan": row["plan"],
        "expires_at": row["expires_at"],
        "paystack_reference": row["paystack_reference"],
    }


@app.post(rule="/api/create-license")
async def create_license(body: CreateLicenseRequest):
    """
    YOU call this endpoint manually (or after Paystack webhook confirms payment)
    to generate and store a new license key.
    Protected by your admin_secret.
    """
    if body.admin_secret != os.getenv(key="ADMIN_SECRET", default="my-admin-secret"):
        raise HTTPException(status_code=403, detail="Forbidden")

    key = generate_license_key()
    days = plan_to_days(body.plan)
    expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=days)).isoformat()

    conn = get_db()
    conn.execute(
        """INSERT INTO licenses (license_key, tenant_id, plan, expires_at, paystack_reference)
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


@app.post(rule="/paystack/webhook")
async def paystack_webhook(request: Request):
    """
    Paystack calls this automatically when a payment completes.
    We auto-generate a license key and (in production) email it to the customer.
    """
    body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    # Verify webhook signature
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

        # Generate license key
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

        # TODO: Send email with key to customer_email
        # e.g. send_license_email(customer_email, key, expires_at)
        print(
            f"[LICENSE] Generated {key} for tenant={tenant_id} email={customer_email}"
        )

    return JSONResponse({"status": "ok"})


@app.get(rule="/")
def root():
    return {"service": "Kennartech License Server", "status": "running"}
