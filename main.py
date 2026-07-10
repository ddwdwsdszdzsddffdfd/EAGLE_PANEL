import asyncio
import json
import os
import hashlib
import secrets
import time
import aiofiles
import psutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote
from collections import deque, defaultdict
from pathlib import Path
import socket
import base64

from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import logging

# ─── تنظیمات ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Eagle-Gateway")

IRAN_TZ = ZoneInfo("Asia/Tehran")

# ─── کانفیگ ──────────────────────────────────────────────────────────────────
CONFIG = {
    "port": int(os.environ.get("PORT", 8000)),
    "secret": os.environ.get("SECRET_KEY", secrets.token_urlsafe(32)),
    "host": os.environ.get("RAILWAY_PUBLIC_DOMAIN", os.environ.get("RENDER_EXTERNAL_URL", "localhost")),
    "admin_password": os.environ.get("ADMIN_PASSWORD", "123456"),
}

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="🪐 Eagle Gateway", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── State ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("/data") if os.environ.get("RAILWAY_ENVIRONMENT") else Path("./data")
DATA_FILE = DATA_DIR / "eagle_state.json"
SAVE_LOCK = asyncio.Lock()

# ─── In-Memory State ─────────────────────────────────────────────────────────
LINKS: dict = {}
LINKS_LOCK = asyncio.Lock()
SUBS: dict = {}
SUBS_LOCK = asyncio.Lock()
connections: dict = {}
stats = {
    "total_bytes": 0,
    "total_requests": 0,
    "total_errors": 0,
    "start_time": time.time(),
}
error_logs: deque = deque(maxlen=50)
activity_logs: deque = deque(maxlen=200)
hourly_traffic: dict = defaultdict(int)
device_connections: dict = {}
DEVICE_CONNECTIONS_LOCK = asyncio.Lock()
http_client: httpx.AsyncClient | None = None

# ─── Auth ──────────────────────────────────────────────────────────────────────
SESSION_COOKIE = "eagle_session"
SESSION_TTL = 60 * 60 * 24 * 7
AUTH = {"password_hash": hashlib.sha256(f"{CONFIG['admin_password']}{CONFIG['secret']}".encode()).hexdigest()}
SESSIONS: dict = {}
SESSIONS_LOCK = asyncio.Lock()

# ─── Settings ──────────────────────────────────────────────────────────────────
SETTINGS: dict = {
    "rgb_mode": False,
    "default_protocol": "vless-ws",
    "default_port": 443,
    "inbound_port": 443,
    "language": "fa",
}

PROTOCOLS = ("vless-ws", "xhttp-packet-up", "xhttp-stream-up", "xhttp-stream-one")
DEFAULT_PROTOCOL = "vless-ws"

# ─── لیست فینگرپرینت‌ها ──────────────────────────────────────────────────────
FINGERPRINTS = {
    "chrome": "🌐 Chrome",
    "firefox": "🦊 Firefox",
    "safari": "🧭 Safari",
    "edge": "🌊 Edge",
    "ios": "📱 iOS",
    "android": "🤖 Android",
    "safari_ios": "🍏 Safari iOS",
    "random": "🎲 Random",
    "none": "🚫 None"
}

# ─── ترجمه ──────────────────────────────────────────────────────────────────
T = {
    "fa": {
        "app_name": "پنل عقاب",
        "app_sub": "مدیریت کاربران",
        "welcome": "خوش آمدید",
        "login_sub": "وارد حساب کاربری خود شوید",
        "username": "نام کاربری یا ایمیل",
        "password": "رمز عبور",
        "remember": "مرا به خاطر بسپار",
        "login": "ورود",
        "or": "یا",
        "connect": "اتصال با یک کلیک",
        "signup": "حساب کاربری ندارید؟",
        "signup_link": "ثبت نام",
        "logout": "خروج",
        "save": "ذخیره",
        "cancel": "انصراف",
        "edit": "ویرایش",
        "delete": "حذف",
        "copy": "کپی",
        "copied": "کپی شد",
        "error": "خطا",
        "success": "موفق",
        "loading": "در حال بارگذاری...",
        "settings": "تنظیمات",
        "backup": "بکاپ",
        "logs": "لاگ‌ها",
        "inbound": "اینباند",
        "connections": "اتصالات",
        "users": "کاربران",
        "dashboard": "خانه",
        "language": "زبان پنل",
        "current_lang": "زبان فعلی",
        "persian": "فارسی",
        "english": "English",
        "online": "آنلاین",
        "offline": "آفلاین",
        "active": "فعال",
        "inactive": "غیرفعال",
        "expired": "منقضی",
        "never": "—",
        "unlimited": "نامحدود",
        "gb": "گیگابایت",
        "day": "روز",
        "days": "روز",
        "device": "دستگاه",
        "devices": "دستگاه‌ها",
        "quota": "سهمیه",
        "usage": "مصرف",
        "traffic": "ترافیک",
        "requests": "درخواست‌ها",
        "uptime": "آپتایم",
        "disk": "فضای دیسک",
        "speed": "سرعت",
        "users_count": "کاربران",
        "last_update": "بروزرسانی",
        "recent_users": "کاربران اخیر",
        "no_users": "هیچ کاربری وجود ندارد",
        "no_connections": "هیچ اتصالی وجود ندارد",
        "no_logs": "هیچ لاگی وجود ندارد",
        "new_user": "کاربر جدید",
        "create_user": "ساخت کاربر جدید",
        "edit_user": "ویرایش کاربر",
        "delete_user": "حذف کاربر",
        "username_label": "نام کاربری",
        "quota_label": "حجم (GB)",
        "expiry_label": "انقضا (روز)",
        "devices_label": "تعداد دستگاه",
        "fingerprint_label": "فینگرپرینت",
        "password_label": "رمز (اختیاری)",
        "status_label": "وضعیت",
        "fingerprint_hint": "فینگرپرینت مناسب دستگاه خود را انتخاب کنید",
        "protocol": "پروتکل",
        "port": "پورت",
        "host": "هاست",
        "status": "وضعیت",
        "active_connections": "اتصالات فعال",
        "last_seen": "آخرین اتصال",
        "change_password": "تغییر رمز",
        "old_password": "رمز فعلی",
        "new_password": "رمز جدید",
        "confirm_password": "تکرار رمز",
        "rgb_mode": "تم RGB",
        "inbound_settings": "تنظیمات اینباند",
        "backup_download": "دانلود بکاپ",
        "backup_restore": "بازیابی بکاپ",
        "user_not_found": "کاربر یافت نشد",
        "invalid_link": "لینک ساب‌لینک معتبر نیست یا کاربر حذف شده است.",
        "subscription_info": "اطلاعات اشتراک",
        "config_link": "لینک کانفیگ",
        "qr_code": "QR",
        "copy_config": "کپی کانفیگ",
        "copy_sub": "کپی ساب",
        "sub_url": "ساب‌لینک",
        "reset_usage": "ریست مصرف",
        "usage_percent": "میزان مصرف",
        "fingerprint": "فینگرپرینت",
        "connected_devices": "دستگاه‌های متصل",
        "no_active_connections": "بدون اتصال فعال",
        "last_connected": "آخرین اتصال",
        "remaining": "باقیمانده",
        "copy_uuid": "کپی UUID",
        "config_copied": "لینک کانفیگ کپی شد",
        "sub_copied": "ساب‌لینک کپی شد",
        "uuid_copied": "UUID کپی شد",
        "user_created": "کاربر ساخته شد",
        "user_updated": "کاربر ویرایش شد",
        "user_deleted": "کاربر حذف شد",
        "usage_reset": "مصرف ریست شد",
        "password_changed": "رمز تغییر کرد",
        "backup_created": "بکاپ ساخته شد",
        "backup_restored": "بکاپ بازیابی شد",
        "settings_saved": "تنظیمات ذخیره شد",
        "connection_error": "خطا در ارتباط با سرور",
        "wrong_password": "رمز عبور اشتباه است",
        "password_mismatch": "رمزها مطابقت ندارند",
        "password_too_short": "رمز حداقل ۴ کاراکتر",
        "invalid_port": "پورت نامعتبر",
        "delete_password_required": "برای حذف رمز را وارد کنید",
        "edit_password_required": "برای ویرایش رمز را وارد کنید",
        "multiple_ports": "پورت‌های چندگانه",
        "select_ports": "پورت‌های مورد نظر را انتخاب کنید",
        "port_selection_hint": "حداقل یک پورت انتخاب کنید",
        "configs_created": "کانفیگ‌ها ساخته شدند",
        "group_sub_link": "لینک گروهی",
        "copy_group_sub": "کپی لینک گروهی",
        "group_sub_copied": "لینک گروهی کپی شد",
        "select_all": "انتخاب همه",
        "deselect_all": "لغو همه",
    },
    "en": {
        "app_name": "Eagle Panel",
        "app_sub": "User Management",
        "welcome": "Welcome Back",
        "login_sub": "Login to your account",
        "username": "Username or Email",
        "password": "Password",
        "remember": "Remember me",
        "login": "Login",
        "or": "OR",
        "connect": "Connect with One Click",
        "signup": "Don't have an account?",
        "signup_link": "Sign up",
        "logout": "Logout",
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "copy": "Copy",
        "copied": "Copied",
        "error": "Error",
        "success": "Success",
        "loading": "Loading...",
        "settings": "Settings",
        "backup": "Backup",
        "logs": "Logs",
        "inbound": "Inbound",
        "connections": "Connections",
        "users": "Users",
        "dashboard": "Dashboard",
        "language": "Panel Language",
        "current_lang": "Current Language",
        "persian": "Persian",
        "english": "English",
        "online": "Online",
        "offline": "Offline",
        "active": "Active",
        "inactive": "Inactive",
        "expired": "Expired",
        "never": "—",
        "unlimited": "Unlimited",
        "gb": "GB",
        "day": "Day",
        "days": "Days",
        "device": "Device",
        "devices": "Devices",
        "quota": "Quota",
        "usage": "Usage",
        "traffic": "Traffic",
        "requests": "Requests",
        "uptime": "Uptime",
        "disk": "Disk Space",
        "speed": "Speed",
        "users_count": "Users",
        "last_update": "Last Update",
        "recent_users": "Recent Users",
        "no_users": "No users found",
        "no_connections": "No active connections",
        "no_logs": "No logs available",
        "new_user": "New User",
        "create_user": "Create New User",
        "edit_user": "Edit User",
        "delete_user": "Delete User",
        "username_label": "Username",
        "quota_label": "Quota (GB)",
        "expiry_label": "Expiry (Days)",
        "devices_label": "Devices",
        "fingerprint_label": "Fingerprint",
        "password_label": "Password (Optional)",
        "status_label": "Status",
        "fingerprint_hint": "Select fingerprint for your device",
        "protocol": "Protocol",
        "port": "Port",
        "host": "Host",
        "status": "Status",
        "active_connections": "Active Connections",
        "last_seen": "Last Seen",
        "change_password": "Change Password",
        "old_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "rgb_mode": "RGB Mode",
        "inbound_settings": "Inbound Settings",
        "backup_download": "Download Backup",
        "backup_restore": "Restore Backup",
        "user_not_found": "User Not Found",
        "invalid_link": "Subscription link is invalid or user has been deleted.",
        "subscription_info": "Subscription Info",
        "config_link": "Config Link",
        "qr_code": "QR",
        "copy_config": "Copy Config",
        "copy_sub": "Copy Sub",
        "sub_url": "Subscription URL",
        "reset_usage": "Reset Usage",
        "usage_percent": "Usage",
        "fingerprint": "Fingerprint",
        "connected_devices": "Connected Devices",
        "no_active_connections": "No active connections",
        "last_connected": "Last Connected",
        "remaining": "Remaining",
        "copy_uuid": "Copy UUID",
        "config_copied": "Config link copied",
        "sub_copied": "Sub link copied",
        "uuid_copied": "UUID copied",
        "user_created": "User created",
        "user_updated": "User updated",
        "user_deleted": "User deleted",
        "usage_reset": "Usage reset",
        "password_changed": "Password changed",
        "backup_created": "Backup created",
        "backup_restored": "Backup restored",
        "settings_saved": "Settings saved",
        "connection_error": "Connection error",
        "wrong_password": "Wrong password",
        "password_mismatch": "Passwords do not match",
        "password_too_short": "Password must be at least 4 characters",
        "invalid_port": "Invalid port",
        "delete_password_required": "Enter password to delete",
        "edit_password_required": "Enter password to edit",
        "multiple_ports": "Multiple Ports",
        "select_ports": "Select ports",
        "port_selection_hint": "Select at least one port",
        "configs_created": "Configs created",
        "group_sub_link": "Group Link",
        "copy_group_sub": "Copy Group Link",
        "group_sub_copied": "Group link copied",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
    }
}

def tr(key: str, lang: str = "fa") -> str:
    if lang not in T:
        lang = "fa"
    return T[lang].get(key, key)

# ─── Functions ─────────────────────────────────────────────────────────────────

def now_ir() -> datetime:
    return datetime.now(IRAN_TZ)

def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()

def generate_uuid() -> str:
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

def get_host() -> str:
    host = os.environ.get("RAILWAY_PUBLIC_DOMAIN", os.environ.get("RENDER_EXTERNAL_URL", CONFIG["host"]))
    # حذف http:// یا https:// از ابتدا
    host = host.replace("https://", "").replace("http://", "").split("/")[0]
    return host

def fmt_bytes(b: int) -> str:
    if not b or b == 0:
        return "0 B"
    if b < 1024:
        return f"{b} B"
    if b < 1024**2:
        return f"{b/1024:.1f} KB"
    if b < 1024**3:
        return f"{b/1024**2:.2f} MB"
    if b < 1024**4:
        return f"{b/1024**3:.2f} GB"
    return f"{b/1024**4:.2f} TB"

def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "Unknown"

def uptime() -> str:
    secs = int(time.time() - stats["start_time"])
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_size_to_bytes(value: float, unit: str) -> int:
    unit = unit.upper()
    if unit == "GB":
        return int(value * 1024 ** 3)
    if unit == "MB":
        return int(value * 1024 ** 2)
    if unit == "KB":
        return int(value * 1024)
    return int(value)

def is_link_expired(link: dict) -> bool:
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(exp)
    except Exception:
        return False

def is_link_allowed(link: dict | None) -> bool:
    if link is None:
        return False
    if not link.get("active", True):
        return False
    if is_link_expired(link):
        return False
    lb = link.get("limit_bytes", 0)
    if lb > 0 and link.get("used_bytes", 0) >= lb:
        return False
    return True

def generate_vless_link(uuid: str, host: str, remark: str = "", protocol: str = DEFAULT_PROTOCOL, 
                        fingerprint: str = "chrome", port: int = 443, 
                        sni: str = None) -> str:
    if not remark:
        remark = "Eagle"
    
    if not sni:
        sni = host
    
    if protocol == "vless-ws":
        path = f"/ws/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "ws",
            "host": host,
            "path": path,
            "sni": sni,
            "fp": fingerprint,
            "alpn": "h2,http/1.1",
        }
    else:
        mode = protocol.replace("xhttp-", "")
        path = f"/xhttp-siz10/{mode}/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "xhttp",
            "mode": mode,
            "host": host,
            "path": path,
            "sni": sni,
            "fp": fingerprint,
            "alpn": "h2,http/1.1",
        }
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    return f"vless://{uuid}@{host}:{port}?{query}#{quote(remark)}"

def log_activity(kind: str, message: str, level: str = "info"):
    activity_logs.append({
        "kind": kind,
        "level": level,
        "message": message,
        "time": datetime.now().isoformat(),
    })

async def remove_device_connection(uuid: str, client_ip: str):
    async with DEVICE_CONNECTIONS_LOCK:
        if uuid in device_connections:
            if client_ip in device_connections[uuid]:
                device_connections[uuid].remove(client_ip)
                if not device_connections[uuid]:
                    del device_connections[uuid]

# ─── Session Functions ──────────────────────────────────────────────────────

async def create_session() -> str:
    token = secrets.token_urlsafe(32)
    async with SESSIONS_LOCK:
        SESSIONS[token] = time.time() + SESSION_TTL
    return token

async def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    async with SESSIONS_LOCK:
        exp = SESSIONS.get(token)
        if exp is None:
            return False
        if exp < time.time():
            SESSIONS.pop(token, None)
            return False
        return True

async def destroy_session(token: str | None):
    if not token:
        return
    async with SESSIONS_LOCK:
        SESSIONS.pop(token, None)

async def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not await is_valid_session(token):
        raise HTTPException(status_code=401, detail="unauthorized")
    return token

# ─── State Persistence ──────────────────────────────────────────────────────

async def load_state():
    global LINKS, SUBS, AUTH, SETTINGS
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = await f.read()
            data = json.loads(raw)
            LINKS.update(data.get("links", {}))
            SUBS.update(data.get("subs", {}))
            if "password_hash" in data:
                AUTH["password_hash"] = data["password_hash"]
            if "settings" in data:
                SETTINGS.update(data["settings"])
            logger.info(f"📂 State loaded: {len(LINKS)} links, {len(SUBS)} subs")
    except Exception as e:
        logger.warning(f"Could not load state: {e}")

async def save_state():
    async with SAVE_LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "links": dict(LINKS),
                "subs": dict(SUBS),
                "password_hash": AUTH["password_hash"],
                "settings": SETTINGS,
                "saved_at": datetime.now().isoformat(),
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(DATA_FILE)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")

# ─── Startup / Shutdown ─────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    global http_client
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    http_client = httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True)
    await load_state()
    log_activity("system", "🪐 Eagle Gateway راه‌اندازی شد", "ok")
    logger.info(f"🪐 Eagle Gateway started on port {CONFIG['port']}")

@app.on_event("shutdown")
async def shutdown():
    await save_state()
    if http_client:
        await http_client.aclose()

# ─── API: Language ──────────────────────────────────────────────────────────

@app.post("/api/settings/language")
async def set_language(request: Request, _=Depends(require_auth)):
    body = await request.json()
    lang = body.get("language", "fa")
    if lang in ["fa", "en"]:
        SETTINGS["language"] = lang
        await save_state()
        return {"ok": True, "language": lang}
    raise HTTPException(status_code=400, detail="Invalid language")

@app.get("/api/language")
async def get_language():
    return {"language": SETTINGS.get("language", "fa")}

# ─── API: Change Password ──────────────────────────────────────────────────

@app.post("/api/change-password")
async def change_password(request: Request, _=Depends(require_auth)):
    body = await request.json()
    old = body.get("old_password", "").strip()
    new = body.get("new_password", "").strip()
    
    if not old or not new or len(new) < 4:
        raise HTTPException(400, "New password must be at least 4 characters")
    
    if hash_password(old) != AUTH["password_hash"]:
        raise HTTPException(403, "Current password is wrong")
    
    AUTH["password_hash"] = hash_password(new)
    CONFIG["admin_password"] = new
    os.environ["ADMIN_PASSWORD"] = new
    
    await save_state()
    log_activity("settings", "Panel password changed", "ok")
    return {"ok": True}

# ─── API: Settings ──────────────────────────────────────────────────────────

@app.get("/api/settings")
async def get_settings(_=Depends(require_auth)):
    return SETTINGS

@app.post("/api/settings/rgb")
async def toggle_rgb(request: Request, _=Depends(require_auth)):
    body = await request.json()
    SETTINGS["rgb_mode"] = bool(body.get("enabled", False))
    await save_state()
    return {"rgb_mode": SETTINGS["rgb_mode"]}

# ─── API: Dashboard Stats ──────────────────────────────────────────────────

@app.get("/api/dashboard/stats")
async def dashboard_stats(_=Depends(require_auth)):
    disk_usage = psutil.disk_usage('/')
    
    if len(hourly_traffic) > 0:
        last_hour = sum(list(hourly_traffic.values())[-6:])
        speed = last_hour / 21600
    else:
        speed = 0
    
    return {
        "traffic": {
            "total": stats["total_bytes"],
            "total_fmt": fmt_bytes(stats["total_bytes"]),
            "today": sum(hourly_traffic.values()),
            "today_fmt": fmt_bytes(sum(hourly_traffic.values()))
        },
        "requests": stats["total_requests"],
        "uptime": uptime(),
        "disk": {
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "total_fmt": fmt_bytes(disk_usage.total),
            "used_fmt": fmt_bytes(disk_usage.used),
            "free_fmt": fmt_bytes(disk_usage.free),
            "percent": disk_usage.percent
        },
        "connections": len(connections),
        "speed": {
            "download": speed,
            "download_fmt": fmt_bytes(speed) + "/s" if speed > 0 else "0 B/s"
        },
        "links_count": len(LINKS),
        "active_links": sum(1 for l in LINKS.values() if is_link_allowed(l))
    }

# ─── API: Inbound ────────────────────────────────────────────────────────────

@app.get("/api/inbound")
async def get_inbound(_=Depends(require_auth)):
    return {
        "port": SETTINGS.get("inbound_port", 443),
        "protocol": SETTINGS.get("default_protocol", "vless"),
        "host": get_host(),
        "is_active": True
    }

@app.post("/api/inbound")
async def update_inbound(request: Request, _=Depends(require_auth)):
    body = await request.json()
    port = body.get("port", 443)
    if port < 1 or port > 65535:
        raise HTTPException(status_code=400, detail="Invalid port")
    SETTINGS["inbound_port"] = port
    await save_state()
    return {"ok": True, "port": port}

# ─── API: Links ─────────────────────────────────────────────────────────────

@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    body = await request.json()
    label = (body.get("label") or "New Link").strip()[:60]
    lv = float(body.get("limit_value") or 0)
    lu = body.get("limit_unit") or "GB"
    limit_bytes = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
    exp_days = int(body.get("expires_days") or 0)
    expires_at = (datetime.now() + timedelta(days=exp_days)).isoformat() if exp_days > 0 else None
    note = (body.get("note") or "").strip()[:200]
    sub_id = body.get("sub_id") or None
    protocol = body.get("protocol") or DEFAULT_PROTOCOL
    if protocol not in PROTOCOLS:
        protocol = DEFAULT_PROTOCOL
    max_devices = int(body.get("max_devices", 0))
    fingerprint = body.get("fingerprint", "chrome")
    if fingerprint not in FINGERPRINTS:
        fingerprint = "chrome"
    config_password = body.get("password", "").strip()
    password_hash = hash_password(config_password) if config_password else None
    
    ports = body.get("ports", [443])
    if not ports or not isinstance(ports, list):
        ports = [443]
    ports = [p for p in ports if isinstance(p, int) and 1 <= p <= 65535]
    if not ports:
        ports = [443]

    group_id = body.get("group_id") or f"group_{label}_{int(time.time())}"
    created_uuids = []
    async with LINKS_LOCK:
        for port in ports:
            uid = generate_uuid()
            created_uuids.append(uid)
            LINKS[uid] = {
                "label": label,
                "limit_bytes": limit_bytes,
                "used_bytes": 0,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "expires_at": expires_at,
                "note": note,
                "is_default": False,
                "sub_id": sub_id,
                "protocol": protocol,
                "max_devices": max_devices,
                "fingerprint": fingerprint,
                "password_hash": password_hash,
                "port": port,
                "group_id": group_id,
            }

    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].setdefault("link_ids", [])
                for uid in created_uuids:
                    if uid not in ids:
                        ids.append(uid)

    asyncio.create_task(save_state())
    log_activity("link", f"Configs for «{label}» created ({len(created_uuids)} ports)", "ok")
    
    host = get_host()
    remark = f"Eagle-{label}"
    
    links_data = []
    for uid in created_uuids:
        link = LINKS[uid]
        port = link.get("port", 443)
        main_link = generate_vless_link(uid, host, remark=remark, protocol=protocol, fingerprint=fingerprint, port=port)
        links_data.append({
            "uuid": uid,
            **link,
            "has_password": password_hash is not None,
            "vless_link": main_link,
            "sub_url": f"https://{host}/sub/{uid}",
        })
    
    group_sub_url = f"https://{host}/sub-group/{group_id}" if created_uuids else None
    
    return {
        "links": links_data,
        "count": len(links_data),
        "group_sub_url": group_sub_url,
        "group_id": group_id,
        "message": f"{len(links_data)} configs created"
    }

@app.get("/api/links")
async def list_links(_=Depends(require_auth)):
    host = get_host()
    async with LINKS_LOCK:
        snap = dict(LINKS)
    
    result = []
    for uid, d in snap.items():
        proto = d.get("protocol", DEFAULT_PROTOCOL)
        fp = d.get("fingerprint", "chrome")
        port = d.get("port", 443)
        label = d.get("label", "User")
        remark = f"Eagle-{label}"
        
        last_connected = None
        for c in connections.values():
            if c.get("uuid") == uid:
                if not last_connected or c.get("connected_at") > last_connected:
                    last_connected = c.get("connected_at")
        
        active = d.get("active", True) and not is_link_expired(d)
        
        result.append({
            "uuid": uid,
            **d,
            "protocol": proto,
            "fingerprint": fp,
            "max_devices": d.get("max_devices", 0),
            "expired": is_link_expired(d),
            "has_password": d.get("password_hash") is not None,
            "port": port,
            "last_connected_at": last_connected,
            "vless_link": generate_vless_link(uid, host, remark=remark, protocol=proto, fingerprint=fp, port=port),
            "sub_url": f"https://{host}/sub/{uid}",
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"links": result}

@app.patch("/api/links/{uid}")
async def update_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        
        if link.get("password_hash"):
            password = body.get("password", "").strip()
            if not password:
                raise HTTPException(status_code=403, detail="Password required to edit")
            if hash_password(password) != link["password_hash"]:
                raise HTTPException(status_code=403, detail="Wrong config password")
        
        old_sub = link.get("sub_id")
        
        if "active" in body:
            link["active"] = bool(body["active"])
        if "label" in body:
            link["label"] = str(body["label"])[:60]
        if "note" in body:
            link["note"] = str(body["note"])[:200]
        if "reset_usage" in body and body["reset_usage"]:
            link["used_bytes"] = 0
        if "limit_value" in body:
            lv = float(body.get("limit_value") or 0)
            lu = body.get("limit_unit") or "GB"
            link["limit_bytes"] = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
        if "expires_days" in body:
            ed = int(body["expires_days"] or 0)
            link["expires_at"] = (datetime.now() + timedelta(days=ed)).isoformat() if ed > 0 else None
        if "max_devices" in body:
            link["max_devices"] = int(body["max_devices"])
        if "fingerprint" in body and body["fingerprint"] in FINGERPRINTS:
            link["fingerprint"] = body["fingerprint"]
        if "protocol" in body and body["protocol"] in PROTOCOLS:
            link["protocol"] = body["protocol"]
        if "port" in body:
            port = int(body["port"])
            if 1 <= port <= 65535:
                link["port"] = port
        new_sub = body.get("sub_id", "UNCHANGED")
        if new_sub != "UNCHANGED":
            link["sub_id"] = new_sub or None

    if new_sub != "UNCHANGED":
        async with SUBS_LOCK:
            if old_sub and old_sub in SUBS:
                ids = SUBS[old_sub].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
            if new_sub and new_sub in SUBS:
                ids = SUBS[new_sub].setdefault("link_ids", [])
                if uid not in ids:
                    ids.append(uid)

    asyncio.create_task(save_state())
    log_activity("link", f"Config «{link['label']}» edited", "info")
    return {"ok": True}

@app.delete("/api/links/{uid}")
async def delete_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    password = body.get("password", "").strip()
    
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        
        if link.get("password_hash"):
            if not password:
                raise HTTPException(status_code=403, detail="Password required to delete")
            if hash_password(password) != link["password_hash"]:
                raise HTTPException(status_code=403, detail="Wrong config password")
        
        label = link.get("label", uid)
        sub_id = link.get("sub_id")
        del LINKS[uid]
    
    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
    
    asyncio.create_task(save_state())
    log_activity("link", f"Config «{label}» deleted", "err")
    return {"ok": True, "deleted": uid}

# ─── API: Stats ──────────────────────────────────────────────────────────────

@app.get("/stats")
async def get_stats(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    
    top_user = None
    top_usage = 0
    for uid, link in snap.items():
        used = link.get("used_bytes", 0)
        if used > top_usage:
            top_usage = used
            top_user = {
                "uuid": uid,
                "label": link.get("label", "Unknown"),
                "used_bytes": used,
                "used_fmt": fmt_bytes(used)
            }
    
    return {
        "active_connections": len(connections),
        "total_traffic_mb": round(stats["total_bytes"] / (1024 ** 2), 2),
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "uptime": uptime(),
        "timestamp": datetime.now().isoformat(),
        "hourly": dict(hourly_traffic),
        "recent_errors": list(error_logs)[-10:],
        "links_count": len(snap),
        "active_links": sum(1 for l in snap.values() if is_link_allowed(l)),
        "expired_links": sum(1 for l in snap.values() if is_link_expired(l)),
        "subs_count": len(SUBS),
        "top_user": top_user,
    }

@app.get("/api/connections")
async def get_connections(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)

    grouped: dict[str, dict] = {}
    for conn_id, c in connections.items():
        ip = c.get("ip", "Unknown")
        link = snap.get(c.get("uuid"))
        label = link.get("label") if link else "Unknown"
        g = grouped.get(ip)
        if g is None:
            g = {
                "ip": ip,
                "sessions": 0,
                "bytes": 0,
                "labels": set(),
                "transports": set(),
                "first_connected_at": c.get("connected_at"),
                "last_connected_at": c.get("connected_at"),
            }
            grouped[ip] = g
        g["sessions"] += 1
        g["bytes"] += c.get("bytes", 0)
        g["labels"].add(label)
        g["transports"].add(c.get("transport", "vless-ws"))
        ca = c.get("connected_at")
        if ca:
            if not g["first_connected_at"] or ca < g["first_connected_at"]:
                g["first_connected_at"] = ca
            if not g["last_connected_at"] or ca > g["last_connected_at"]:
                g["last_connected_at"] = ca

    result = []
    for ip, g in grouped.items():
        result.append({
            "ip": ip,
            "sessions": g["sessions"],
            "labels": sorted(g["labels"]),
            "label": " · ".join(sorted(g["labels"])) if g["labels"] else "Unknown",
            "transports": sorted(g["transports"]),
            "bytes": g["bytes"],
            "bytes_fmt": fmt_bytes(g["bytes"]),
            "connected_at": g["first_connected_at"],
            "last_connected_at": g["last_connected_at"],
        })
    result.sort(key=lambda x: x.get("last_connected_at") or "", reverse=True)

    return {
        "connections": result,
        "count": len(result),
        "raw_count": len(connections),
    }

# ─── Auth Endpoints ────────────────────────────────────────────────────────

@app.post("/api/login")
async def api_login(request: Request):
    body = await request.json()
    ip = client_ip(request)
    password = body.get("password", "")
    remember = body.get("remember", False)
    
    if hash_password(str(password)) != AUTH["password_hash"]:
        log_activity("auth", f"Failed login attempt from {ip}", "err")
        raise HTTPException(status_code=401, detail="Wrong password")
    
    token = await create_session()
    log_activity("auth", f"Successful login from {ip}", "ok")
    
    max_age = SESSION_TTL if remember else None
    resp = JSONResponse({"ok": True})
    resp.set_cookie(SESSION_COOKIE, token, max_age=max_age, httponly=True, samesite="lax", path="/")
    return resp

@app.post("/api/logout")
async def api_logout(request: Request):
    await destroy_session(request.cookies.get(SESSION_COOKIE))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp

@app.get("/api/me")
async def api_me(request: Request):
    return {"authenticated": await is_valid_session(request.cookies.get(SESSION_COOKIE))}

# ─── API: Activity Logs ───────────────────────────────────────────────────────

@app.get("/api/activity")
async def get_activity_logs(_=Depends(require_auth)):
    limit = 100
    logs = list(activity_logs)[-limit:]
    return {"logs": logs}

# ─── Backup ────────────────────────────────────────────────────────────────────

@app.get("/api/backup")
async def get_backup(_=Depends(require_auth)):
    async with LINKS_LOCK:
        links = dict(LINKS)
    async with SUBS_LOCK:
        subs = dict(SUBS)
    return {
        "links": links,
        "subs": subs,
        "password_hash": AUTH["password_hash"],
        "settings": SETTINGS,
        "exported_at": datetime.now().isoformat(),
        "version": "10.0"
    }

@app.post("/api/backup/restore")
async def restore_backup(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
        
        if "links" in body and isinstance(body["links"], dict):
            async with LINKS_LOCK:
                LINKS.clear()
                for uid, link_data in body["links"].items():
                    if not isinstance(link_data, dict):
                        continue
                    LINKS[uid] = link_data
        
        if "subs" in body and isinstance(body["subs"], dict):
            async with SUBS_LOCK:
                SUBS.clear()
                for sid, sub_data in body["subs"].items():
                    if not isinstance(sub_data, dict):
                        continue
                    SUBS[sid] = sub_data
        
        if "password_hash" in body:
            AUTH["password_hash"] = body["password_hash"]
        
        if "settings" in body and isinstance(body["settings"], dict):
            SETTINGS.update(body["settings"])
        
        await save_state()
        log_activity("backup", "Backup restored", "ok")
        return {"ok": True, "message": "Backup restored successfully"}
    except Exception as e:
        logger.error(f"Backup restore error: {e}")
        raise HTTPException(status_code=400, detail=f"Backup restore error: {str(e)}")

# ─── VLESS WebSocket Tunnel ────────────────────────────────────────────────

RELAY_BUF = 512 * 1024

def _ws_client_ip(ws: WebSocket) -> str:
    fwd = ws.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = ws.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return ws.client.host if ws.client else "Unknown"

async def check_device_limit(uuid: str, client_ip: str) -> bool:
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
        if not link:
            return False
        max_devices = link.get("max_devices", 0)
        if max_devices == 0:
            return True
    
    async with DEVICE_CONNECTIONS_LOCK:
        current_ips = device_connections.get(uuid, [])
        if client_ip in current_ips:
            return True
        if len(current_ips) >= max_devices:
            return False
        if uuid not in device_connections:
            device_connections[uuid] = []
        device_connections[uuid].append(client_ip)
        return True

async def parse_vless_header(chunk: bytes):
    if len(chunk) < 24:
        raise ValueError("chunk too small")
    pos = 1
    pos += 16
    addon_len = chunk[pos]
    pos += 1 + addon_len
    command = chunk[pos]
    pos += 1
    port = int.from_bytes(chunk[pos:pos+2], "big")
    pos += 2
    addr_type = chunk[pos]
    pos += 1
    if addr_type == 1:
        address = ".".join(str(b) for b in chunk[pos:pos+4])
        pos += 4
    elif addr_type == 2:
        dlen = chunk[pos]
        pos += 1
        address = chunk[pos:pos+dlen].decode("utf-8", errors="ignore")
        pos += dlen
    elif addr_type == 3:
        ab = chunk[pos:pos+16]
        pos += 16
        address = ":".join(f"{ab[i]:02x}{ab[i+1]:02x}" for i in range(0, 16, 2))
    else:
        raise ValueError(f"unknown addr type: {addr_type}")
    return command, address, port, chunk[pos:]

async def check_and_use(uid: str, n: int) -> bool:
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link is None:
            return False
        if not is_link_allowed(link):
            return False
        link["used_bytes"] = link.get("used_bytes", 0) + n
        stats["total_bytes"] = stats.get("total_bytes", 0) + n
        hourly_traffic[now_ir().strftime("%H:00")] = hourly_traffic.get(now_ir().strftime("%H:00"), 0) + n
        
        limit = link.get("limit_bytes", 0)
        used = link.get("used_bytes", 0)
        if limit > 0 and used / limit > 0.8 and not link.get("alert_80"):
            link["alert_80"] = True
            log_activity("warning", f"⚠️ Config {link.get('label')} usage reached 80%", "warn")
        
        return True

async def relay_ws_to_tcp(ws: WebSocket, writer: asyncio.StreamWriter, conn_id: str, uid: str):
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            data = msg.get("bytes") or (msg.get("text") or "").encode()
            if not data:
                continue
            if not await check_and_use(uid, len(data)):
                await ws.close(code=1008, reason="quota/disabled/unknown")
                break
            stats["total_requests"] = stats.get("total_requests", 0) + 1
            if conn_id in connections:
                connections[conn_id]["bytes"] = connections[conn_id].get("bytes", 0) + len(data)
            writer.write(data)
            if writer.transport.get_write_buffer_size() > RELAY_BUF:
                await writer.drain()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        try:
            writer.write_eof()
        except Exception:
            pass

async def relay_tcp_to_ws(ws: WebSocket, reader: asyncio.StreamReader, conn_id: str, uid: str):
    first = True
    try:
        while True:
            data = await reader.read(RELAY_BUF)
            if not data:
                break
            if not await check_and_use(uid, len(data)):
                await ws.close(code=1008, reason="quota/disabled/unknown")
                break
            if conn_id in connections:
                connections[conn_id]["bytes"] = connections[conn_id].get("bytes", 0) + len(data)
            payload = (b"\x00\x00" + data) if first else data
            first = False
            await ws.send_bytes(payload)
    except Exception:
        pass

@app.websocket("/ws/{uuid}")
async def websocket_tunnel(ws: WebSocket, uuid: str):
    await ws.accept()

    client_ip = _ws_client_ip(ws)
    
    async with LINKS_LOCK:
        link = LINKS.get(uuid)

    if not link:
        logger.warning(f"🚫 WS rejected uuid={uuid[:8]}… (user not found)")
        await ws.close(code=1008, reason="user not found")
        return

    if not is_link_allowed(link):
        logger.warning(f"🚫 WS rejected uuid={uuid[:8]}… (not allowed)")
        await ws.close(code=1008, reason="not authorized")
        return

    max_devices = link.get("max_devices", 0)
    if max_devices > 0:
        if not await check_device_limit(uuid, client_ip):
            logger.warning(f"🚫 Device limit exceeded for {uuid[:8]}… (max: {max_devices})")
            await ws.close(code=1008, reason="device limit exceeded")
            return

    conn_id = secrets.token_urlsafe(6)
    connections[conn_id] = {
        "uuid": uuid,
        "ip": client_ip,
        "transport": "vless-ws",
        "connected_at": datetime.now().isoformat(),
        "bytes": 0,
    }
    
    logger.info(f"✅ WS [{conn_id}] uuid={uuid[:8]}… ip={client_ip} total={len(connections)}")
    log_activity("connection", f"New connection from {client_ip} (config {link.get('label','?')})", "info")
    
    writer = None

    try:
        first_msg = await asyncio.wait_for(ws.receive(), timeout=15.0)
        if first_msg["type"] == "websocket.disconnect":
            return
        first_chunk = first_msg.get("bytes") or (first_msg.get("text") or "").encode()
        if not first_chunk:
            return

        command, address, port, payload = await parse_vless_header(first_chunk)

        if not await check_and_use(uuid, len(first_chunk)):
            await ws.close(code=1008, reason="quota/disabled")
            return

        stats["total_requests"] = stats.get("total_requests", 0) + 1
        if conn_id in connections:
            connections[conn_id]["bytes"] = connections[conn_id].get("bytes", 0) + len(first_chunk)
        logger.info(f"➡️  [{conn_id}] → {address}:{port}")

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(address, port),
            timeout=10.0
        )
        sock = writer.transport.get_extra_info('socket')
        if sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)

        if payload:
            writer.write(payload)
            await writer.drain()

        done, pending = await asyncio.wait(
            {
                asyncio.create_task(relay_ws_to_tcp(ws, writer, conn_id, uuid)),
                asyncio.create_task(relay_tcp_to_ws(ws, reader, conn_id, uuid)),
            },
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

        asyncio.create_task(save_state())

    except WebSocketDisconnect:
        pass
    except asyncio.TimeoutError:
        stats["total_errors"] = stats.get("total_errors", 0) + 1
        error_logs.append({"error": "connection timeout", "time": datetime.now().isoformat()})
    except Exception as exc:
        stats["total_errors"] = stats.get("total_errors", 0) + 1
        error_logs.append({"error": str(exc), "time": datetime.now().isoformat()})
        logger.error(f"WS error [{conn_id}]: {exc}")
    finally:
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        connections.pop(conn_id, None)
        await remove_device_connection(uuid, client_ip)
        logger.info(f"🔌 WS closed [{conn_id}] total={len(connections)}")

# ─── Subscriptions ─────────────────────────────────────────────────────────

@app.get("/sub-group/{group_id}")
async def subscription_group(group_id: str, request: Request):
    """ساب‌لینک گروهی - تمام کانفیگ‌های یک گروه رو برمی‌گردونه"""
    host = get_host()
    lines = []
    
    async with LINKS_LOCK:
        for uid, link in LINKS.items():
            if link.get("group_id") == group_id and is_link_allowed(link):
                fp = link.get("fingerprint", "chrome")
                port = link.get("port", 443)
                label = link.get("label", "User")
                remark = f"Eagle-{label}-{port}"
                vless = generate_vless_link(
                    uid, host, remark=remark,
                    protocol=link.get("protocol", DEFAULT_PROTOCOL),
                    fingerprint=fp, port=port
                )
                lines.append(vless)
    
    if not lines:
        return Response("", media_type="text/plain")
    
    content = base64.b64encode("\n".join(lines).encode()).decode()
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "profile-title": f"Eagle-Group-{group_id[:8]}",
            "profile-update-interval": "12",
        }
    )

@app.get("/sub/{uuid}")
async def subscription_single(uuid: str, request: Request):
    lang = request.cookies.get("eagle-lang", SETTINGS.get("language", "fa"))
    if lang not in ["fa", "en"]:
        lang = "fa"
    
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    
    if not link:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Not Found</title></head>
        <body style="background:#0a0a1a;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
            <div style="text-align:center;padding:40px;background:rgba(20,20,40,0.7);border-radius:20px;">
                <h1>🪐</h1>
                <p style="color:#888;">User not found</p>
            </div>
        </body>
        </html>
        """, status_code=404)
    
    # صفحه ساده برای نمایش اطلاعات کاربر
    label = link.get("label", "User")
    port = link.get("port", 443)
    fp = link.get("fingerprint", "chrome")
    protocol = link.get("protocol", "vless-ws")
    host = get_host()
    remark = f"Eagle-{label}"
    
    vless_link = generate_vless_link(uuid, host, remark=remark, protocol=protocol, fingerprint=fp, port=port)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🪐 {label}</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{font-family:'Vazirmatn',sans-serif;background:#0a0a1a;min-height:100vh;display:flex;align-items:center;justify-content:center;color:#F0EEFF;padding:16px}}
    .card{{background:rgba(10,10,30,0.8);backdrop-filter:blur(30px);border:1px solid rgba(100,80,255,0.08);border-radius:20px;padding:30px;max-width:500px;width:100%}}
    .brand{{display:flex;align-items:center;gap:10px;margin-bottom:20px}}
    .brand-icon{{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9);display:flex;align-items:center;justify-content:center;font-size:20px}}
    .brand-text{{font-size:16px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
    .info-item{{background:rgba(100,80,255,0.03);border:1px solid rgba(100,80,255,0.04);border-radius:8px;padding:10px 12px;margin-bottom:8px;display:flex;justify-content:space-between}}
    .info-label{{color:#8888BB;font-size:11px}}
    .info-value{{color:#F0EEFF;font-weight:600;font-size:12px}}
    .vless-box{{background:rgba(0,0,0,0.2);border:1px solid rgba(100,80,255,0.04);border-radius:8px;padding:10px;margin:12px 0;word-break:break-all;font-family:monospace;font-size:10px;color:#A78BFA}}
    .btn{{display:inline-block;padding:8px 16px;border-radius:8px;border:none;cursor:pointer;font-family:inherit;font-weight:600;font-size:12px;transition:all .2s}}
    .btn-primary{{background:linear-gradient(135deg,#7C6BFF,#5B4BD9);color:#fff}}
    .btn-primary:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(100,80,255,0.3)}}
    .btn-secondary{{background:rgba(100,80,255,0.05);border:1px solid rgba(100,80,255,0.04);color:#8888BB}}
    .btn-secondary:hover{{background:rgba(100,80,255,0.1)}}
    .actions{{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}}
    .actions .btn{{flex:1;text-align:center;min-width:80px}}
    .status{{display:inline-block;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:700}}
    .status.active{{background:rgba(16,185,129,0.12);color:#34D399}}
    .status.inactive{{background:rgba(239,68,68,0.12);color:#F87171}}
    .footer{{margin-top:16px;padding-top:12px;border-top:1px solid rgba(100,80,255,0.03);text-align:center;font-size:9px;color:#555577}}
    </style>
    </head>
    <body>
    <div class="card">
        <div class="brand"><div class="brand-icon">🪐</div><div class="brand-text">پنل عقاب</div></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <h2 style="font-size:18px;font-weight:800">🪐 {label}</h2>
            <span class="status {'active' if link.get('active', True) and not is_link_expired(link) else 'inactive'}">
                {'فعال' if link.get('active', True) and not is_link_expired(link) else 'غیرفعال'}
            </span>
        </div>
        <div class="info-item"><span class="info-label">UUID</span><span class="info-value" style="font-family:monospace;font-size:10px">{uuid}</span></div>
        <div class="info-item"><span class="info-label">پورت</span><span class="info-value">{port}</span></div>
        <div class="info-item"><span class="info-label">پروتکل</span><span class="info-value">{protocol}</span></div>
        <div class="info-item"><span class="info-label">فینگرپرینت</span><span class="info-value">{fp}</span></div>
        <div class="info-item"><span class="info-label">مصرف</span><span class="info-value">{fmt_bytes(link.get('used_bytes', 0))}</span></div>
        <div class="info-item"><span class="info-label">سهمیه</span><span class="info-value">{'نامحدود' if link.get('limit_bytes', 0) == 0 else fmt_bytes(link.get('limit_bytes', 0))}</span></div>
        <div class="vless-box">{vless_link}</div>
        <div class="actions">
            <button class="btn btn-primary" onclick="copyText('{vless_link}')">📋 کپی</button>
            <button class="btn btn-secondary" onclick="window.open('https://api.qrserver.com/v1/create-qr-code/?size=250x250&data='+encodeURIComponent('{vless_link}'), '_blank')">📱 QR</button>
        </div>
        <div class="footer">🪐 پنل عقاب</div>
    </div>
    <script>
    function copyText(text) {{
        navigator.clipboard.writeText(text).then(() => {{
            const btn = event.target;
            const orig = btn.textContent;
            btn.textContent = '✅ کپی شد';
            setTimeout(() => btn.textContent = orig, 1500);
        }});
    }}
    </script>
    </body>
    </html>
    """)

@app.get("/sub-all")
async def subscription_all(_=Depends(require_auth)):
    host = get_host()
    async with LINKS_LOCK:
        lines = []
        for uid, d in LINKS.items():
            if is_link_allowed(d):
                fp = d.get("fingerprint", "chrome")
                port = d.get("port", 443)
                label = d.get("label", "User")
                remark = f"Eagle-{label}"
                lines.append(generate_vless_link(uid, host, remark=remark, protocol=d.get("protocol", DEFAULT_PROTOCOL), fingerprint=fp, port=port))
    content = base64.b64encode("\n".join(lines).encode()).decode()
    return Response(content=content, media_type="text/plain")

# ─── HTML Pages ─────────────────────────────────────────────────────────────

def get_login_html(lang: str = "fa") -> str:
    t = lambda k: tr(k, lang)
    dir_attr = "rtl" if lang == "fa" else "ltr"
    
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dir_attr}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🪐 {t('app_name')} · {t('login')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0a0a1a;--card:rgba(10,10,30,0.75);--card-b:rgba(100,80,255,0.12);--accent:#7C6BFF;--accent2:#A78BFA;--accent3:#5B4BD9;--t1:#F0EEFF;--t2:#8888BB;--t3:#555577;--border:rgba(100,80,255,0.08);--glow:0 0 80px rgba(100,80,255,0.05);}}
body{{font-family:'Vazirmatn',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0a0a1a,#1a0a2a,#0a0a2a);padding:20px;color:var(--t1);position:relative;overflow:hidden}}
.stars{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.star{{position:absolute;border-radius:50%;background:#fff;animation:twinkle 3s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{opacity:0.2}}50%{{opacity:0.8}}}}
.glow-orb{{position:fixed;border-radius:50%;filter:blur(150px);z-index:0;animation:orbFloat 6s ease-in-out infinite;pointer-events:none}}
.orb1{{width:500px;height:500px;background:rgba(100,80,255,0.05);top:-200px;right:-100px}}
.orb2{{width:400px;height:400px;background:rgba(167,139,250,0.04);bottom:-100px;left:-80px;animation-delay:2s}}
@keyframes orbFloat{{0%,100%{{transform:translate(0,0) scale(1)}}50%{{transform:translate(30px,-30px) scale(1.1)}}}}
.container{{position:relative;z-index:10;display:grid;grid-template-columns:1fr 1fr;max-width:1100px;width:100%;background:var(--card);backdrop-filter:blur(30px);border-radius:24px;border:1px solid var(--border);overflow:hidden;box-shadow:var(--glow),0 25px 80px rgba(0,0,0,0.6)}}
.login-section{{padding:48px 40px}}
.brand{{display:flex;align-items:center;gap:12px;margin-bottom:32px}}
.brand-icon{{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 40px rgba(100,80,255,0.2)}}
.brand-text{{font-size:16px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.brand-sub{{font-size:9px;color:var(--t3);margin-top:0px;-webkit-text-fill-color:var(--t3)}}
.welcome{{font-size:22px;font-weight:800;color:var(--t1);margin-bottom:4px}}
.sub-text{{font-size:13px;color:var(--t3);margin-bottom:28px}}
.field{{margin-bottom:18px}}
.field label{{display:block;font-size:10px;font-weight:600;color:var(--t2);margin-bottom:4px}}
.field input{{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--border);background:rgba(0,0,20,.3);color:var(--t1);font-family:inherit;font-size:14px;outline:none;transition:.3s}}
.field input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.08),0 0 30px rgba(100,80,255,.04)}}
.field input::placeholder{{color:var(--t3)}}
.options{{display:flex;justify-content:space-between;align-items:center;margin:14px 0 20px;font-size:12px}}
.options label{{display:flex;align-items:center;gap:6px;color:var(--t2);cursor:pointer}}
.options label input[type="checkbox"]{{accent-color:var(--accent);width:16px;height:16px;cursor:pointer}}
.btn-login{{width:100%;padding:12px;border-radius:10px;border:none;cursor:pointer;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);background-size:200% 200%;animation:gradientMove 4s ease infinite;color:#fff;font-family:inherit;font-size:15px;font-weight:700;transition:all .3s;box-shadow:0 4px 30px rgba(100,80,255,.25)}}
@keyframes gradientMove{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.btn-login:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(100,80,255,.35)}}
.btn-login:disabled{{opacity:.5;cursor:not-allowed;transform:none}}
.or-divider{{display:flex;align-items:center;gap:14px;margin:20px 0;color:var(--t3);font-size:11px}}
.or-divider::before,.or-divider::after{{content:'';flex:1;height:1px;background:var(--border)}}
.connect-btn{{width:100%;padding:12px;border-radius:10px;border:1px solid var(--border);background:rgba(100,80,255,0.03);color:var(--t1);font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:.3s;display:flex;align-items:center;justify-content:center;gap:8px}}
.connect-btn:hover{{background:rgba(100,80,255,0.06);border-color:rgba(100,80,255,0.2)}}
.signup-text{{text-align:center;margin-top:18px;font-size:12px;color:var(--t3)}}
.signup-text a{{color:var(--accent);text-decoration:none;font-weight:600}}
.signup-text a:hover{{text-decoration:underline}}
.error-box{{display:none;background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.15);border-radius:8px;padding:10px 12px;margin-bottom:14px;font-size:12px;color:#F87171;align-items:center;gap:8px}}
.error-box.show{{display:flex}}
.info-section{{background:linear-gradient(135deg,#0a0a1a,#1a0a2a);padding:48px 36px;display:flex;flex-direction:column;justify-content:center;border-right:1px solid var(--border)}}
.info-title{{font-size:22px;font-weight:800;color:var(--t1);margin-bottom:6px}}
.info-sub{{font-size:13px;color:var(--t3);margin-bottom:24px}}
.features{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.feature{{background:rgba(100,80,255,0.03);border-radius:12px;padding:14px 12px;text-align:center;border:1px solid rgba(100,80,255,0.04)}}
.feature .icon{{font-size:28px;display:block;margin-bottom:4px}}
.feature .name{{font-size:11px;font-weight:600;color:var(--t1)}}
.feature .desc{{font-size:8px;color:var(--t3);margin-top:2px}}
.lang-toggle{{position:fixed;top:20px;left:20px;z-index:50;display:flex;gap:6px;background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:10px;padding:4px}}
.lang-toggle button{{background:none;border:none;color:var(--t3);font-family:inherit;font-size:11px;font-weight:600;padding:4px 10px;border-radius:6px;cursor:pointer;transition:.3s}}
.lang-toggle button.active{{background:linear-gradient(135deg,#7C6BFF,#5B4BD9);color:#fff}}
.lang-toggle button:hover:not(.active){{color:var(--t1)}}
@media(max-width:900px){{.container{{grid-template-columns:1fr}}.info-section{{display:none}}.login-section{{padding:32px 24px}}}}
@media(max-width:480px){{.login-section{{padding:24px 16px}}.welcome{{font-size:19px}}}}
</style>
</head>
<body>
<div class="stars"><div class="star" style="width:2px;height:2px;top:10%;left:5%;animation-delay:0s"></div><div class="star" style="width:3px;height:3px;top:20%;left:15%;animation-delay:1s"></div><div class="star" style="width:1px;height:1px;top:30%;left:25%;animation-delay:2s"></div><div class="star" style="width:2px;height:2px;top:15%;left:35%;animation-delay:0.5s"></div><div class="star" style="width:3px;height:3px;top:40%;left:45%;animation-delay:1.5s"></div><div class="star" style="width:1px;height:1px;top:25%;left:55%;animation-delay:2.5s"></div><div class="star" style="width:2px;height:2px;top:50%;left:65%;animation-delay:0.7s"></div><div class="star" style="width:3px;height:3px;top:60%;left:75%;animation-delay:1.8s"></div><div class="star" style="width:1px;height:1px;top:70%;left:85%;animation-delay:2.2s"></div><div class="star" style="width:2px;height:2px;top:80%;left:95%;animation-delay:1.2s"></div></div>
<div class="glow-orb orb1"></div><div class="glow-orb orb2"></div>

<div class="lang-toggle">
    <button class="active" onclick="setLang('fa')">🇮🇷 {t('persian')}</button>
    <button onclick="setLang('en')">🇬🇧 {t('english')}</button>
</div>

<div class="container">
    <div class="login-section">
        <div class="brand"><div class="brand-icon">🪐</div><div><div class="brand-text">{t('app_name')}</div><div class="brand-sub">{t('app_sub')}</div></div></div>
        <div class="welcome" id="welcome-text">{t('welcome')}</div>
        <div class="sub-text" id="sub-text">{t('login_sub')}</div>
        <div class="error-box" id="error-box"><i class="ti ti-alert-circle"></i><span id="error-text"></span></div>
        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="field"><label id="label-username">{t('username')}</label><input type="text" id="username" placeholder="{t('username')}" value="admin" dir="ltr"></div>
            <div class="field"><label id="label-password">{t('password')}</label><input type="password" id="password" placeholder="{t('password')}" dir="ltr"></div>
            <div class="options"><label><input type="checkbox" id="remember"> <span id="remember-text">{t('remember')}</span></label></div>
            <button class="btn-login" type="submit" id="login-btn"><i class="ti ti-login-2"></i> <span id="login-text">{t('login')}</span></button>
        </form>
        <div class="or-divider"><span id="or-text">{t('or')}</span></div>
        <button class="connect-btn" onclick="quickConnect()"><i class="ti ti-plug"></i> <span id="connect-text">{t('connect')}</span></button>
        <div class="signup-text" id="signup-text">{t('signup')} <a href="/dashboard">{t('signup_link')}</a></div>
    </div>
    <div class="info-section">
        <div class="info-title" id="info-title">🪐 {t('app_name')}</div>
        <div class="info-sub" id="info-sub">{t('login_sub')}</div>
        <div class="features">
            <div class="feature"><span class="icon">🔒</span><div class="name" id="f-secure">🔒</div><div class="desc" id="f-secure-d">{t('active')}</div></div>
            <div class="feature"><span class="icon">⚡</span><div class="name" id="f-fast">⚡</div><div class="desc" id="f-fast-d">{t('speed')}</div></div>
            <div class="feature"><span class="icon">🌍</span><div class="name" id="f-global">🌍</div><div class="desc" id="f-global-d">{t('connections')}</div></div>
            <div class="feature"><span class="icon">🕵️</span><div class="name" id="f-anon">🕵️</div><div class="desc" id="f-anon-d">{t('secure')}</div></div>
        </div>
    </div>
</div>

<script>
const translations = {{
    fa: {{ welcome: "{t('welcome')}", sub: "{t('login_sub')}", username: "{t('username')}", password: "{t('password')}", remember: "{t('remember')}", login: "{t('login')}", or: "{t('or')}", connect: "{t('connect')}", signup: "{t('signup')}", signup_link: "{t('signup_link')}" }},
    en: {{ welcome: "Welcome Back", sub: "Login to your account", username: "Username or Email", password: "Password", remember: "Remember me", login: "Login", or: "OR", connect: "Connect with One Click", signup: "Don't have an account?", signup_link: "Sign up" }}
}};
let currentLang = localStorage.getItem('eagle-lang') || 'fa';
function setLang(lang) {{
    currentLang = lang;
    localStorage.setItem('eagle-lang', lang);
    document.querySelectorAll('.lang-toggle button').forEach(b => b.classList.toggle('active', b.textContent.includes(lang === 'fa' ? 'فارسی' : 'English')));
    updateTexts();
}}
function updateTexts() {{
    const t = translations[currentLang];
    document.getElementById('welcome-text').textContent = t.welcome;
    document.getElementById('sub-text').textContent = t.sub;
    document.getElementById('label-username').textContent = t.username;
    document.getElementById('label-password').textContent = t.password;
    document.getElementById('remember-text').textContent = t.remember;
    document.getElementById('login-text').textContent = t.login;
    document.getElementById('or-text').textContent = t.or;
    document.getElementById('connect-text').textContent = t.connect;
    document.getElementById('signup-text').innerHTML = t.signup + ' <a href="/dashboard">' + t.signup_link + '</a>';
}}
async function handleLogin(e) {{
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const err = document.getElementById('error-box');
    const errText = document.getElementById('error-text');
    err.classList.remove('show');
    btn.disabled = true;
    btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> {t('loading')}';
    try {{
        const r = await fetch('/api/login', {{
            method: 'POST', headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{password: document.getElementById('password').value, remember: document.getElementById('remember').checked}})
        }});
        if (!r.ok) {{
            const d = await r.json().catch(() => ({{}}));
            errText.textContent = d.detail || '{t('wrong_password')}';
            err.classList.add('show');
            btn.disabled = false;
            btn.innerHTML = '<i class="ti ti-login-2"></i> ' + translations[currentLang].login;
            return;
        }}
        window.location.href = '/dashboard';
    }} catch(e) {{
        errText.textContent = '{t('connection_error')}';
        err.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = '<i class="ti ti-login-2"></i> ' + translations[currentLang].login;
    }}
}}
function quickConnect() {{
    document.getElementById('password').value = '123456';
    document.getElementById('remember').checked = true;
    document.getElementById('login-form').dispatchEvent(new Event('submit'));
}}
document.getElementById('password').addEventListener('keydown', (e) => {{
    if (e.key === 'Enter') document.getElementById('login-form').dispatchEvent(new Event('submit'));
}});
setLang(currentLang);
</script>
</body></html>"""

def get_dashboard_html(lang: str = "fa") -> str:
    t = lambda k: tr(k, lang)
    dir_attr = "rtl" if lang == "fa" else "ltr"
    
    ports = [443, 8443, 2096, 8080, 2053, 2087]
    port_options = "".join([
        f'<label style="display:flex;align-items:center;gap:4px;font-size:10px;color:var(--t2);cursor:pointer;padding:3px 6px;background:rgba(100,80,255,0.02);border-radius:4px;border:1px solid rgba(100,80,255,0.03)">'
        f'<input type="checkbox" class="port-checkbox" value="{p}" {"checked" if p == 443 else ""}> {p}'
        f'</label>' for p in ports
    ])
    
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dir_attr}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🪐 {t('app_name')} · {t('dashboard')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0a0a1a;--bg2:#12122a;--bg3:#1a1a3a;--card:rgba(10,10,30,0.7);--card-b:rgba(100,80,255,0.08);--card-bh:rgba(100,80,255,0.15);--accent:#7C6BFF;--accent2:#A78BFA;--accent3:#5B4BD9;--green:#10B981;--green-bg:rgba(16,185,129,0.08);--green-t:#34D399;--red:#EF4444;--red-bg:rgba(239,68,68,0.08);--red-t:#F87171;--amber:#F59E0B;--amber-bg:rgba(245,158,11,0.08);--amber-t:#FCD34D;--t1:#F0EEFF;--t2:#8888BB;--t3:#555577;--sidebar-w:180px;--radius:12px;--shadow:0 8px 32px rgba(0,0,0,0.5),0 0 60px rgba(100,80,255,0.02);}}
body{{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;display:flex;font-size:13px;position:relative;overflow-x:hidden}}
.stars-bg{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.star-bg{{position:absolute;border-radius:50%;background:#fff;animation:twinkleBg 4s ease-in-out infinite}}
@keyframes twinkleBg{{0%,100%{{opacity:0.1}}50%{{opacity:0.4}}}}
.glow-main{{position:fixed;border-radius:50%;filter:blur(200px);z-index:0;pointer-events:none}}
.glow-left{{width:600px;height:600px;background:rgba(100,80,255,0.02);top:-300px;left:-200px}}
.glow-right{{width:500px;height:500px;background:rgba(167,139,250,0.02);bottom:-200px;right:-100px}}
.sidebar{{width:var(--sidebar-w);min-height:100vh;background:var(--card);backdrop-filter:blur(30px);border-left:1px solid var(--card-b);display:flex;flex-direction:column;flex-shrink:0;position:fixed;right:0;top:0;bottom:0;z-index:200;transition:transform .3s;box-shadow:var(--shadow)}}
.logo{{display:flex;align-items:center;gap:10px;padding:16px 12px 12px;border-bottom:1px solid var(--card-b)}}
.logo-icon{{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;box-shadow:0 0 30px rgba(100,80,255,0.15)}}
.logo-name{{font-size:13px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.logo-sub{{font-size:7px;color:var(--t3);margin-top:0px}}
.nav-wrap{{flex:1;overflow-y:auto;padding:6px 0;position:relative;z-index:1}}
.nav-it{{display:flex;align-items:center;gap:8px;padding:8px 10px;color:var(--t3);font-size:11px;cursor:pointer;border-right:2px solid transparent;transition:all .2s;margin:1px 4px;border-radius:6px}}
.nav-it i{{font-size:14px;width:18px;text-align:center;flex-shrink:0}}
.nav-it:hover{{background:rgba(100,80,255,0.05);color:var(--t2)}}
.nav-it.on{{background:rgba(100,80,255,0.08);color:var(--t1);border-right-color:var(--accent);font-weight:600;box-shadow:0 0 30px rgba(100,80,255,0.03)}}
.sb-foot{{padding:10px 12px;border-top:1px solid var(--card-b)}}
.logout-btn{{display:flex;align-items:center;justify-content:center;gap:6px;background:var(--red-bg);color:var(--red-t);border-radius:6px;padding:6px;font-size:10px;font-weight:500;font-family:inherit;border:1px solid rgba(239,68,68,0.1);cursor:pointer;width:100%;transition:.2s}}
.logout-btn:hover{{background:rgba(239,68,68,0.15)}}
.mob-top{{display:none;position:fixed;top:0;right:0;left:0;height:48px;background:var(--card);backdrop-filter:blur(30px);border-bottom:1px solid var(--card-b);z-index:150;align-items:center;justify-content:space-between;padding:0 10px}}
.mob-top .ml{{display:flex;align-items:center;gap:6px}}
.mob-logo{{width:26px;height:26px;border-radius:6px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9);display:flex;align-items:center;justify-content:center;font-size:13px}}
.mob-title{{color:var(--t1);font-size:11px;font-weight:700}}
.menu-btn{{background:rgba(100,80,255,0.05);border:1px solid var(--card-b);color:var(--t2);width:30px;height:30px;border-radius:6px;font-size:14px;display:flex;align-items:center;justify-content:center;cursor:pointer}}
.overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:190;backdrop-filter:blur(6px)}}
.overlay.show{{display:block}}
.main{{margin-right:var(--sidebar-w);flex:1;padding:16px 20px 80px;min-width:0;transition:margin .3s;position:relative;z-index:1}}
.pg{{display:none;animation:pageIn .3s ease}}
.pg.on{{display:block}}
@keyframes pageIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
.topbar{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}}
.tb-title{{font-size:17px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:6px}}
.tb-title i{{color:var(--accent);font-size:19px}}
.tb-sub{{font-size:10px;color:var(--t3);margin-top:1px}}
.tb-right{{display:flex;align-items:center;gap:5px;flex-wrap:wrap}}
.badge{{font-size:8px;padding:2px 8px;border-radius:12px;font-weight:700;display:inline-flex;align-items:center;gap:3px;white-space:nowrap}}
.bg-green{{background:var(--green-bg);color:var(--green-t)}}
.bg-blue{{background:rgba(100,80,255,0.1);color:var(--accent)}}
.bg-fire{{background:rgba(100,80,255,0.08);color:#A78BFA}}
.bg-amber{{background:var(--amber-bg);color:var(--amber-t)}}
.dot{{width:5px;height:5px;border-radius:50%;flex-shrink:0;display:inline-block}}
.dg{{background:var(--green)}}.dr{{background:var(--red)}}.da{{background:var(--amber)}}.db{{background:var(--accent)}}
.pulse{{animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.stats-grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:16px}}
.stat-card{{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 8px;transition:all .3s;text-align:center;position:relative;overflow:hidden}}
.stat-card::before{{content:'';position:absolute;top:-50%;right:-50%;width:100px;height:100px;background:radial-gradient(circle,rgba(100,80,255,0.03),transparent 70%);pointer-events:none}}
.stat-card:hover{{border-color:var(--card-bh);transform:translateY(-2px);box-shadow:var(--shadow)}}
.stat-card .icon{{font-size:18px;margin-bottom:3px;display:block}}
.stat-card .number{{font-size:18px;font-weight:800;color:var(--t1);line-height:1.2}}
.stat-card .number.small{{font-size:13px}}
.stat-card .label{{font-size:9px;color:var(--t3);margin-top:2px;font-weight:500}}
.stat-card .sub{{font-size:7px;color:var(--t3);margin-top:0px;opacity:.6}}
.user-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}}
.user-card{{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 14px;transition:all .3s;position:relative;overflow:hidden}}
.user-card::before{{content:'';position:absolute;top:-50%;right:-50%;width:150px;height:150px;background:radial-gradient(circle,rgba(100,80,255,0.02),transparent 70%);pointer-events:none}}
.user-card:hover{{border-color:var(--card-bh);transform:translateY(-2px)}}
.user-card .head{{display:flex;align-items:center;justify-content:space-between;margin-bottom:3px}}
.user-card .name{{font-size:12px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:4px}}
.user-card .status{{font-size:8px;font-weight:700;padding:1px 8px;border-radius:8px}}
.user-card .status.on{{background:var(--green-bg);color:var(--green-t)}}
.user-card .status.off{{background:var(--red-bg);color:var(--red-t)}}
.user-card .uuid{{font-family:monospace;font-size:7px;color:var(--t3);margin-bottom:4px;word-break:break-all}}
.user-card .info{{display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:9px;color:var(--t2);margin-bottom:3px}}
.user-card .quota-info{{display:flex;justify-content:space-between;font-size:9px;color:var(--t2);margin-bottom:2px}}
.user-card .quota-bar{{height:3px;border-radius:2px;background:rgba(100,80,255,0.05);overflow:hidden;margin-bottom:6px}}
.user-card .quota-fill{{height:100%;border-radius:2px;background:linear-gradient(90deg,#7C6BFF,#5B4BD9,#A78BFA);transition:width .6s ease}}
.user-card .last-seen{{font-size:8px;color:var(--t3);margin-bottom:4px}}
.user-card .actions{{display:flex;gap:3px;flex-wrap:wrap}}
.user-card .actions .btn{{font-size:8px;padding:3px 6px;border-radius:4px;flex:1;justify-content:center}}
.user-card .lock-badge{{font-size:7px;color:var(--amber-t);background:var(--amber-bg);padding:0px 5px;border-radius:4px}}
.user-card .port-badge{{font-size:7px;color:var(--accent);background:rgba(100,80,255,0.08);padding:0px 5px;border-radius:4px}}
.btn{{font-family:inherit;font-size:10px;font-weight:600;border-radius:6px;padding:5px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;border:none;transition:all .2s;white-space:nowrap}}
.btn i{{font-size:11px}}
.btn-p{{background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);background-size:200% 200%;animation:btnGradient 4s ease infinite;color:#fff;box-shadow:0 3px 15px rgba(100,80,255,.2)}}
@keyframes btnGradient{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.btn-p:hover{{transform:translateY(-1px);box-shadow:0 6px 25px rgba(100,80,255,.3)}}
.btn-o{{background:rgba(255,255,255,0.02);border:1px solid var(--card-b);color:var(--t2)}}
.btn-o:hover{{background:rgba(100,80,255,0.05)}}
.btn-d{{background:var(--red-bg);color:var(--red-t);border:1px solid rgba(239,68,68,.1)}}
.btn-d:hover{{background:rgba(239,68,68,.15)}}
.btn-pur{{background:rgba(100,80,255,0.08);color:var(--accent);border:1px solid rgba(100,80,255,.1)}}
.btn-pur:hover{{background:rgba(100,80,255,0.15)}}
.btn-amber{{background:var(--amber-bg);color:var(--amber-t);border:1px solid rgba(245,158,11,0.1)}}
.btn-amber:hover{{background:rgba(245,158,11,0.15)}}
.btn-sm{{padding:2px 6px;font-size:8px;border-radius:4px}}
.btn-icon{{width:22px;height:22px;padding:0;justify-content:center}}
.modal-bg{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:500;align-items:center;justify-content:center;backdrop-filter:blur(8px)}}
.modal-bg.open{{display:flex}}
.modal{{background:var(--card);backdrop-filter:blur(30px);border:1px solid var(--card-b);border-radius:14px;padding:20px 18px;max-width:440px;width:calc(100% - 20px);max-height:90vh;overflow-y:auto;position:relative;animation:pageIn .3s ease;box-shadow:var(--shadow)}}
.modal-close{{position:absolute;top:10px;left:10px;background:rgba(100,80,255,0.05);border:1px solid var(--card-b);color:var(--t2);width:24px;height:24px;border-radius:6px;font-size:12px;display:flex;align-items:center;justify-content:center;cursor:pointer;border:none;transition:.2s}}
.modal-close:hover{{background:var(--red-bg);color:var(--red-t)}}
.modal-title{{font-size:14px;font-weight:700;color:var(--t1);margin-bottom:12px;display:flex;align-items:center;gap:6px}}
.modal-title i{{color:var(--accent);font-size:15px}}
.fg{{display:flex;flex-direction:column;gap:2px;margin-bottom:8px}}
.fg label{{font-size:8px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.04em;display:flex;align-items:center;gap:3px}}
.fi{{width:100%;padding:6px 10px;border-radius:6px;border:1px solid var(--card-b);background:rgba(0,0,20,.2);color:var(--t1);font-family:inherit;font-size:10px;outline:none;transition:.2s}}
.fi:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.06)}}
.fi::placeholder{{color:var(--t3)}}
select.fi{{appearance:none;cursor:pointer}}
.fg-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}}
.conn-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}}
.conn-card{{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:10px;padding:10px 12px;transition:.2s}}
.conn-card:hover{{border-color:var(--card-bh)}}
.conn-card .ip{{font-family:monospace;font-size:11px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:4px}}
.conn-card .label{{font-size:8px;color:var(--t3);margin-top:1px}}
.conn-card .conn-info{{display:flex;justify-content:space-between;margin-top:4px;font-size:8px;color:var(--t2);gap:3px;flex-wrap:wrap}}
.conn-status-dot{{display:inline-block;width:5px;height:5px;border-radius:50%;background:#34D399;animation:pulse 1.5s infinite;margin-left:3px}}
.settings-card{{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:14px 16px;max-width:480px;margin-bottom:10px;position:relative;overflow:hidden}}
.settings-card::before{{content:'';position:absolute;top:-50%;right:-50%;width:150px;height:150px;background:radial-gradient(circle,rgba(100,80,255,0.02),transparent 70%);pointer-events:none}}
.settings-card .title{{font-size:13px;font-weight:700;color:var(--t1);margin-bottom:10px;display:flex;align-items:center;gap:6px}}
.settings-card .title i{{color:var(--accent)}}
.settings-card .field{{margin-bottom:8px}}
.settings-card .field label{{font-size:9px;color:var(--t3);display:block;margin-bottom:2px;font-weight:600}}
.settings-card .field input{{width:100%;padding:6px 10px;border-radius:6px;border:1px solid var(--card-b);background:rgba(0,0,20,.2);color:var(--t1);font-family:inherit;font-size:11px;outline:none;transition:.2s}}
.settings-card .field input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.06)}}
.settings-card .btn{{width:100%;justify-content:center;margin-top:3px;font-size:11px;padding:6px}}
.settings-card .toggle-row{{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--card-b)}}
.settings-card .toggle-row .toggle-label{{font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px}}
.switch{{position:relative;width:36px;height:20px;background:var(--t3);border-radius:10px;cursor:pointer;transition:.3s;flex-shrink:0}}
.switch.on{{background:linear-gradient(135deg,#7C6BFF,#5B4BD9)}}
.switch .slider{{position:absolute;top:2px;right:2px;width:16px;height:16px;background:#fff;border-radius:50%;transition:.3s;box-shadow:0 2px 4px rgba(0,0,0,0.2)}}
.switch.on .slider{{right:18px}}
.toast{{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(50px);background:var(--card);backdrop-filter:blur(30px);border:1px solid var(--card-b);color:var(--t1);border-radius:8px;padding:8px 16px;font-size:11px;opacity:0;transition:all .3s;z-index:999;pointer-events:none;box-shadow:var(--shadow);display:flex;align-items:center;gap:5px}}
.toast.show{{opacity:1;transform:translateX(-50%) translateY(0)}}
.toast.ok{{border-color:rgba(16,185,129,.2);background:var(--green-bg);color:var(--green-t)}}
.toast.err{{border-color:rgba(239,68,68,.2);background:var(--red-bg);color:var(--red-t)}}
.empty{{text-align:center;padding:30px 15px;color:var(--t3)}}
.empty i{{font-size:28px;opacity:.3;display:block;margin-bottom:6px}}
.empty p{{font-size:10px}}
.bottom-nav{{display:none;position:fixed;bottom:0;right:0;left:0;background:var(--card);backdrop-filter:blur(30px);border-top:1px solid var(--card-b);z-index:300;padding:4px 2px 6px;justify-content:space-around;align-items:center}}
.bottom-nav .nav-item{{display:flex;flex-direction:column;align-items:center;gap:1px;color:var(--t3);font-size:7px;cursor:pointer;padding:3px 6px;border-radius:6px;transition:all .2s;border:none;background:none;font-family:inherit;min-width:40px;position:relative}}
.bottom-nav .nav-item i{{font-size:16px;transition:all .2s}}
.bottom-nav .nav-item:hover{{color:var(--t2)}}
.bottom-nav .nav-item.active{{color:var(--accent)}}
.bottom-nav .nav-item.active i{{transform:scale(1.1)}}
@media(max-width:768px){{.bottom-nav{{display:flex !important}}.main{{padding-bottom:65px !important;margin-right:0 !important;padding-top:55px !important}}.sidebar{{transform:translateX(100%);padding-bottom:60px}}.sidebar.open{{transform:translateX(0)}}.mob-top{{display:flex}}.stats-grid{{grid-template-columns:repeat(3,1fr)}}.user-grid{{grid-template-columns:1fr}}}}
@media(max-width:480px){{.stats-grid{{grid-template-columns:1fr 1fr}}.main{{padding:50px 8px 65px}}.bottom-nav .nav-item{{min-width:32px;padding:2px 4px}}.bottom-nav .nav-item i{{font-size:14px}}.bottom-nav .nav-item span{{font-size:6px}}}}
@media(min-width:769px){{.bottom-nav{{display:none !important}}}}
</style>
</head>
<body>
<div class="stars-bg"><div class="star-bg" style="width:2px;height:2px;top:5%;left:10%;animation-delay:0s"></div><div class="star-bg" style="width:3px;height:3px;top:15%;left:30%;animation-delay:1.5s"></div><div class="star-bg" style="width:1px;height:1px;top:25%;left:50%;animation-delay:0.8s"></div><div class="star-bg" style="width:2px;height:2px;top:40%;left:70%;animation-delay:2.2s"></div><div class="star-bg" style="width:3px;height:3px;top:55%;left:15%;animation-delay:0.5s"></div><div class="star-bg" style="width:1px;height:1px;top:70%;left:85%;animation-delay:1.8s"></div><div class="star-bg" style="width:2px;height:2px;top:85%;left:40%;animation-delay:2.5s"></div></div>
<div class="glow-main glow-left"></div><div class="glow-main glow-right"></div>
<div class="toast" id="toast"></div>

<div class="modal-bg" id="modal-user">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('modal-user')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-user-plus"></i> 🪐 {t('create_user')}</div>
    <div class="fg"><label><i class="ti ti-tag"></i> {t('username_label')}</label><input class="fi" id="user-label" placeholder="{t('username_label')}"></div>
    <div class="fg-grid">
      <div class="fg"><label><i class="ti ti-database"></i> {t('quota_label')}</label><input class="fi" id="user-quota" type="number" min="0.5" step="0.5" value="2"></div>
      <div class="fg"><label><i class="ti ti-calendar"></i> {t('expiry_label')}</label><input class="fi" id="user-exp" type="number" min="0" value="30"></div>
      <div class="fg"><label><i class="ti ti-devices"></i> {t('devices_label')}</label><input class="fi" id="user-devices" type="number" min="0" max="10" value="1"></div>
    </div>
    <div class="fg">
      <label><i class="ti ti-fingerprint"></i> {t('fingerprint_label')}</label>
      <select class="fi" id="user-fingerprint">
        <option value="chrome">🌐 Chrome</option><option value="firefox">🦊 Firefox</option><option value="safari">🧭 Safari</option><option value="edge">🌊 Edge</option><option value="ios">📱 iOS</option><option value="android">🤖 Android</option><option value="safari_ios">🍏 Safari iOS</option><option value="random">🎲 Random</option><option value="none">🚫 None</option>
      </select>
      <div style="font-size:7px;color:var(--t3);margin-top:2px;">💡 {t('fingerprint_hint')}</div>
    </div>
    <div class="fg">
      <label><i class="ti ti-plug"></i> {t('select_ports')}</label>
      <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px;">{port_options}</div>
      <div style="display:flex;gap:6px;margin-top:4px;">
        <button type="button" class="btn btn-sm btn-o" onclick="document.querySelectorAll('.port-checkbox').forEach(c=>c.checked=true)">{t('select_all')}</button>
        <button type="button" class="btn btn-sm btn-o" onclick="document.querySelectorAll('.port-checkbox').forEach(c=>c.checked=false)">{t('deselect_all')}</button>
      </div>
      <div style="font-size:7px;color:var(--t3);margin-top:2px;">💡 {t('port_selection_hint')}</div>
    </div>
    <div class="fg"><label><i class="ti ti-lock"></i> {t('password_label')}</label><input class="fi" id="user-password" type="password" placeholder="{t('password_label')}" dir="ltr"></div>
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-p" onclick="saveUser()" style="flex:2"><i class="ti ti-check"></i> {t('create_user')}</button>
      <button class="btn btn-o" onclick="closeModal('modal-user')" style="flex:1">{t('cancel')}</button>
    </div>
  </div>
</div>

<div class="modal-bg" id="modal-edit">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('modal-edit')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-edit"></i> 🪐 {t('edit_user')}</div>
    <input type="hidden" id="edit-uuid">
    <div class="fg" id="edit-password-section"><label><i class="ti ti-lock"></i> {t('password')}</label><input class="fi" id="edit-password" type="password" placeholder="{t('password')}" dir="ltr"></div>
    <div class="fg"><label><i class="ti ti-tag"></i> {t('username_label')}</label><input class="fi" id="edit-label" placeholder="{t('username_label')}"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
      <div class="fg"><label><i class="ti ti-database"></i> {t('quota_label')}</label><input class="fi" id="edit-quota" type="number" min="0" step="0.5"></div>
      <div class="fg"><label><i class="ti ti-calendar"></i> {t('expiry_label')}</label><input class="fi" id="edit-exp" type="number" min="0"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
      <div class="fg"><label><i class="ti ti-devices"></i> {t('devices_label')}</label><input class="fi" id="edit-devices" type="number" min="0" max="10"></div>
      <div class="fg"><label><i class="ti ti-toggle-left"></i> {t('status_label')}</label><select class="fi" id="edit-status"><option value="true">✅ {t('active')}</option><option value="false">❌ {t('inactive')}</option></select></div>
    </div>
    <div class="fg">
      <label><i class="ti ti-fingerprint"></i> {t('fingerprint_label')}</label>
      <select class="fi" id="edit-fingerprint">
        <option value="chrome">🌐 Chrome</option><option value="firefox">🦊 Firefox</option><option value="safari">🧭 Safari</option><option value="edge">🌊 Edge</option><option value="ios">📱 iOS</option><option value="android">🤖 Android</option><option value="safari_ios">🍏 Safari iOS</option><option value="random">🎲 Random</option><option value="none">🚫 None</option>
      </select>
    </div>
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-p" onclick="saveEdit()" style="flex:2"><i class="ti ti-check"></i> {t('save')}</button>
      <button class="btn btn-o" onclick="closeModal('modal-edit')" style="flex:1">{t('cancel')}</button>
    </div>
  </div>
</div>

<div class="modal-bg" id="modal-delete">
  <div class="modal" style="max-width:340px">
    <button class="modal-close" onclick="closeModal('modal-delete')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-trash"></i> {t('delete_user')}</div>
    <input type="hidden" id="delete-uuid">
    <p style="font-size:10px;color:var(--t2);margin-bottom:10px">{t('delete_password_required')}</p>
    <div class="fg"><label><i class="ti ti-lock"></i> {t('password')}</label><input class="fi" id="delete-password" type="password" placeholder="{t('password')}" dir="ltr"></div>
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-d" onclick="confirmDelete()" style="flex:2"><i class="ti ti-trash"></i> {t('delete')}</button>
      <button class="btn btn-o" onclick="closeModal('modal-delete')" style="flex:1">{t('cancel')}</button>
    </div>
  </div>
</div>

<div class="mob-top"><div class="ml"><div class="mob-logo">🪐</div><span class="mob-title">{t('app_name')}</span></div><button class="menu-btn" id="open-sb"><i class="ti ti-menu-2"></i></button></div>
<div class="overlay" id="overlay"></div>

<aside class="sidebar" id="sb">
  <div class="logo"><div class="logo-icon">🪐</div><div><div class="logo-name">{t('app_name')}</div><div class="logo-sub">{t('app_sub')}</div></div></div>
  <div class="nav-wrap">
    <div class="nav-it on" data-pg="dashboard"><i class="ti ti-layout-dashboard"></i> {t('dashboard')}</div>
    <div class="nav-it" data-pg="users"><i class="ti ti-users"></i> {t('users')}</div>
    <div class="nav-it" data-pg="inbound"><i class="ti ti-plug"></i> {t('inbound')}</div>
    <div class="nav-it" data-pg="connections"><i class="ti ti-plug-connected"></i> {t('connections')}</div>
    <div class="nav-it" data-pg="settings"><i class="ti ti-settings"></i> {t('settings')}</div>
    <div class="nav-it" data-pg="logs"><i class="ti ti-notes"></i> {t('logs')}</div>
    <div class="nav-it" data-pg="backup"><i class="ti ti-database"></i> {t('backup')}</div>
  </div>
  <div class="sb-foot"><button class="logout-btn" onclick="logout()"><i class="ti ti-logout"></i> {t('logout')}</button></div>
</aside>

<div class="bottom-nav" id="bottomNav">
  <button class="nav-item active" data-pg="dashboard" onclick="navTo('dashboard')"><i class="ti ti-layout-dashboard"></i><span>{t('dashboard')}</span></button>
  <button class="nav-item" data-pg="users" onclick="navTo('users')"><i class="ti ti-users"></i><span>{t('users')}</span></button>
  <button class="nav-item" data-pg="inbound" onclick="navTo('inbound')"><i class="ti ti-plug"></i><span>{t('inbound')}</span></button>
  <button class="nav-item" data-pg="settings" onclick="navTo('settings')"><i class="ti ti-settings"></i><span>{t('settings')}</span></button>
</div>

<main class="main">
<section class="pg on" id="pg-dashboard">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-layout-dashboard"></i> {t('dashboard')}</div><div class="tb-sub" id="last-update">{t('last_update')}: {t('loading')}</div></div>
    <div class="tb-right"><span class="badge bg-fire" id="online-badge"><span class="dot dg"></span> 0 {t('online')}</span><button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-plus"></i> {t('new_user')}</button></div>
  </div>
  <div class="stats-grid">
    <div class="stat-card"><span class="icon">📊</span><div class="number" id="stat-traffic">0</div><div class="label">{t('traffic')}</div><div class="sub">MB</div></div>
    <div class="stat-card"><span class="icon">📨</span><div class="number" id="stat-requests">0</div><div class="label">{t('requests')}</div><div class="sub">{t('requests')}</div></div>
    <div class="stat-card"><span class="icon">⏱️</span><div class="number" id="stat-uptime">00:00:00</div><div class="label">{t('uptime')}</div><div class="sub">{t('uptime')}</div></div>
    <div class="stat-card"><span class="icon">💾</span><div class="number small" id="stat-disk">0 GB</div><div class="label">{t('disk')}</div><div class="sub" id="stat-disk-used">{t('usage')}</div></div>
    <div class="stat-card"><span class="icon">📶</span><div class="number small" id="stat-speed">0 B/s</div><div class="label">{t('speed')}</div><div class="sub">{t('speed')}</div></div>
    <div class="stat-card"><span class="icon">👥</span><div class="number" id="stat-users">0</div><div class="label">{t('users_count')}</div><div class="sub" id="stat-users-active">0 {t('active')}</div></div>
  </div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:10px 12px;margin-top:4px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span style="font-size:11px;font-weight:700;color:var(--t1)">🆕 {t('recent_users')}</span><button class="btn btn-sm btn-o" onclick="loadDashboard()"><i class="ti ti-refresh"></i></button></div>
    <div id="recent-users" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:4px"></div>
  </div>
</section>

<section class="pg" id="pg-users">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-users"></i> {t('users')}</div><div class="tb-sub" id="users-count">0 {t('users')}</div></div><div class="tb-right"><button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-plus"></i> {t('new_user')}</button></div></div>
  <div id="users-grid" class="user-grid"><div class="empty"><i class="ti ti-users"></i><p>{t('no_users')}</p></div></div>
</section>

<section class="pg" id="pg-inbound">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-plug"></i> {t('inbound')}</div><div class="tb-sub">{t('inbound_settings')}</div></div></div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 14px;margin-bottom:10px">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:var(--t1)" id="inbound-port">443</div><div style="font-size:8px;color:var(--t3)">{t('port')}</div></div>
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:var(--t1)" id="inbound-protocol">VLESS</div><div style="font-size:8px;color:var(--t3)">{t('protocol')}</div></div>
      <div style="text-align:center"><div style="font-size:12px;font-weight:700;color:var(--t1)" id="inbound-host">—</div><div style="font-size:8px;color:var(--t3)">{t('host')}</div></div>
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:#34D399">✅ {t('active')}</div><div style="font-size:8px;color:var(--t3)">{t('status')}</div></div>
    </div>
    <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
      <button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-user-plus"></i> {t('new_user')}</button>
      <button class="btn btn-o btn-sm" onclick="openModal('modal-inbound')"><i class="ti ti-settings"></i> {t('settings')}</button>
    </div>
  </div>
</section>

<section class="pg" id="pg-connections">
  <div class="topbar"><div><div class="tb-title">🔌 {t('connections')}</div><div class="tb-sub" id="conn-count">0 {t('connections')}</div></div><div class="tb-right"><span class="badge bg-green"><span class="dot dg pulse"></span> {t('active')}</span><button class="btn btn-sm btn-o" onclick="loadConnections()"><i class="ti ti-refresh"></i></button></div></div>
  <div id="conns-grid" class="conn-grid"><div class="empty"><i class="ti ti-plug-off"></i><p>{t('no_connections')}</p></div></div>
</section>

<section class="pg" id="pg-settings">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-settings"></i> {t('settings')}</div><div class="tb-sub">{t('settings')}</div></div></div>
  <div class="settings-card"><div class="title"><i class="ti ti-language"></i> {t('language')}</div>
    <div style="display:flex;gap:6px;margin-top:4px"><button class="btn btn-pur" onclick="setLang('fa')" style="flex:1;font-size:11px;padding:6px 12px" id="lang-fa-btn">🇮🇷 {t('persian')}</button><button class="btn btn-o" onclick="setLang('en')" style="flex:1;font-size:11px;padding:6px 12px" id="lang-en-btn">🇬🇧 {t('english')}</button></div>
    <div style="font-size:9px;color:var(--t3);margin-top:6px">💡 {t('current_lang')}: <span id="current-lang-label">{t('persian')}</span></div>
  </div>
  <div class="settings-card"><div class="title"><i class="ti ti-key"></i> {t('change_password')}</div>
    <div class="field"><label>{t('old_password')}</label><input class="fi" id="old-password" type="password" placeholder="{t('old_password')}" dir="ltr"></div>
    <div class="field"><label>{t('new_password')}</label><input class="fi" id="new-password" type="password" placeholder="{t('new_password')}" dir="ltr"></div>
    <div class="field"><label>{t('confirm_password')}</label><input class="fi" id="confirm-password" type="password" placeholder="{t('confirm_password')}" dir="ltr"></div>
    <button class="btn btn-p" onclick="changePassword()"><i class="ti ti-key"></i> {t('change_password')}</button>
    <div id="password-result" style="margin-top:8px;display:none;font-size:11px;"></div>
  </div>
  <div class="settings-card"><div class="title"><i class="ti ti-plug"></i> {t('inbound_settings')}</div>
    <div class="field"><label>{t('port')}</label><input class="fi" id="inbound-port-setting" type="number" min="1" max="65535" value="443"></div>
    <button class="btn btn-p" onclick="updateInbound()"><i class="ti ti-check"></i> {t('save')}</button>
  </div>
  <div class="settings-card"><div class="title"><i class="ti ti-color-swatch"></i> {t('rgb_mode')}</div>
    <div class="toggle-row"><div class="toggle-label"><i class="ti ti-color-palette" style="background:linear-gradient(135deg,#ff0000,#00ff00,#0000ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent"></i> {t('rgb_mode')}</div><div class="switch" id="rgb-switch" onclick="toggleRGB()"><div class="slider"></div></div></div>
  </div>
</section>

<section class="pg" id="pg-logs">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-notes"></i> {t('logs')}</div><div class="tb-sub" id="logs-count">0 {t('logs')}</div></div><div class="tb-right"><button class="btn btn-sm btn-o" onclick="loadLogs()"><i class="ti ti-refresh"></i></button></div></div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:8px 10px;max-height:400px;overflow-y:auto"><div id="logs-container" style="font-family:monospace;font-size:9px;color:var(--t2);direction:ltr;text-align:left;line-height:1.5"></div></div>
</section>

<section class="pg" id="pg-backup">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-database"></i> {t('backup')}</div><div class="tb-sub">{t('backup')}</div></div></div>
  <div class="settings-card"><div class="title"><i class="ti ti-download"></i> {t('backup_download')}</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap"><button class="btn btn-p btn-sm" onclick="createBackup()" style="flex:2"><i class="ti ti-download"></i> {t('backup_download')}</button><button class="btn btn-o btn-sm" onclick="document.getElementById('restore-input').click()" style="flex:1"><i class="ti ti-upload"></i> {t('backup_restore')}</button><input type="file" id="restore-input" accept=".json" style="display:none" onchange="restoreBackup(event)"></div>
  </div>
</section>
</main>

<script>
function toast(msg, type='') {{ const t=document.getElementById('toast'); t.textContent=msg; t.className='toast show'+(type?' '+type:''); setTimeout(()=>t.classList.remove('show'),2500); }}
function fmtB(b) {{ if(!b||b===0) return '0 B'; if(b<1024) return b+' B'; if(b<1024**2) return (b/1024).toFixed(1)+' KB'; if(b<1024**3) return (b/1024**2).toFixed(1)+' MB'; if(b<1024**4) return (b/1024**3).toFixed(2)+' GB'; return (b/1024**4).toFixed(2)+' TB'; }}
function esc(s) {{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function openModal(id) {{ document.getElementById(id).classList.add('open'); }}
function closeModal(id) {{ document.getElementById(id).classList.remove('open'); }}

let currentLang = localStorage.getItem('eagle-lang') || 'fa';
function setLang(lang) {{
    currentLang = lang;
    localStorage.setItem('eagle-lang', lang);
    document.getElementById('lang-fa-btn').className = 'btn ' + (lang === 'fa' ? 'btn-pur' : 'btn-o');
    document.getElementById('lang-en-btn').className = 'btn ' + (lang === 'en' ? 'btn-pur' : 'btn-o');
    document.getElementById('current-lang-label').textContent = lang === 'fa' ? 'فارسی' : 'English';
    fetch('/api/settings/language', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{language: lang}}) }}).catch(() => {{}});
    location.reload();
}}

async function authF(url, opts={{}}) {{ const r = await fetch(url, opts); if(r.status === 401) {{ location.href = '/login'; throw new Error('unauthorized'); }} return r; }}
async function logout() {{ try {{ await fetch('/api/logout', {{method:'POST'}}); }} catch(e) {{}} location.href = '/login'; }}

function navTo(name) {{
    document.querySelectorAll('.nav-it').forEach(n => n.classList.toggle('on', n.dataset.pg === name));
    document.querySelectorAll('.pg').forEach(p => p.classList.toggle('on', p.id === 'pg-' + name));
    document.querySelectorAll('.bottom-nav .nav-item').forEach(n => n.classList.toggle('active', n.dataset.pg === name));
    closeSb();
    const loaders = {{ dashboard: loadDashboard, users: loadUsers, inbound: loadInbound, connections: loadConnections, logs: loadLogs, settings: () => {{}} }};
    if(loaders[name]) loaders[name]();
}}
document.querySelectorAll('.nav-it, .bottom-nav .nav-item').forEach(el => {{ el.addEventListener('click', () => navTo(el.dataset.pg)); }});
const sb = document.getElementById('sb'), overlay = document.getElementById('overlay');
function openSb(){{ sb.classList.add('open'); overlay.classList.add('show'); }}
function closeSb(){{ sb.classList.remove('open'); overlay.classList.remove('show'); }}
document.getElementById('open-sb').addEventListener('click', openSb);
overlay.addEventListener('click', closeSb);

async function saveUser() {{
    const label = document.getElementById('user-label').value.trim() || 'کاربر';
    const quota = parseFloat(document.getElementById('user-quota').value) || 0;
    const exp = parseInt(document.getElementById('user-exp').value) || 30;
    const devices = parseInt(document.getElementById('user-devices').value) || 0;
    const password = document.getElementById('user-password').value.trim();
    const fingerprint = document.getElementById('user-fingerprint').value || 'chrome';
    const portCheckboxes = document.querySelectorAll('.port-checkbox:checked');
    const ports = Array.from(portCheckboxes).map(cb => parseInt(cb.value));
    if(ports.length === 0) {{ toast('لطفاً حداقل یک پورت انتخاب کنید', 'err'); return; }}
    try {{
        const r = await authF('/api/links', {{
            method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ label, limit_value: quota, limit_unit: 'GB', expires_days: exp, max_devices: devices, password, fingerprint, protocol: 'vless-ws', ports }})
        }});
        if(!r.ok) throw new Error();
        const data = await r.json();
        document.getElementById('user-label').value = '';
        document.getElementById('user-quota').value = '2';
        document.getElementById('user-exp').value = '30';
        document.getElementById('user-devices').value = '1';
        document.getElementById('user-password').value = '';
        document.getElementById('user-fingerprint').value = 'chrome';
        document.querySelectorAll('.port-checkbox').forEach(cb => cb.checked = cb.value === '443');
        closeModal('modal-user');
        toast(`✅ {t('configs_created')} (${data.count})`, 'ok');
        if(data.group_sub_url) {{
            setTimeout(() => {{
                if(confirm('{t('group_sub_link')}: ' + data.group_sub_url + '\\n\\n{t('copy_group_sub')}?')) {{
                    navigator.clipboard.writeText(data.group_sub_url).then(() => toast('{t('group_sub_copied')}', 'ok'));
                }}
            }}, 500);
        }}
        loadUsers(); loadDashboard();
    }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function loadDashboard() {{
    try {{
        const r = await authF('/api/dashboard/stats');
        const data = await r.json();
        document.getElementById('stat-traffic').textContent = (data.traffic.total / (1024*1024)).toFixed(1);
        document.getElementById('stat-requests').textContent = data.requests || 0;
        document.getElementById('stat-uptime').textContent = data.uptime || '00:00:00';
        document.getElementById('stat-disk').textContent = data.disk.total_fmt || '0 GB';
        document.getElementById('stat-disk-used').textContent = '{t('usage')}: ' + (data.disk.used_fmt || '0');
        document.getElementById('stat-speed').textContent = data.speed.download_fmt || '0 B/s';
        document.getElementById('stat-users').textContent = data.links_count || 0;
        document.getElementById('stat-users-active').textContent = (data.active_links || 0) + ' {t('active')}';
        document.getElementById('online-badge').innerHTML = '<span class="dot dg"></span> ' + (data.connections || 0) + ' {t('online')}';
        document.getElementById('last-update').textContent = '{t('last_update')}: ' + new Date().toLocaleTimeString('fa-IR');
        const usersR = await authF('/api/links');
        const usersData = await usersR.json();
        const links = usersData.links || [];
        const recent = links.slice(0, 4);
        const grid = document.getElementById('recent-users');
        if(!recent.length) {{ grid.innerHTML = '<div class="empty" style="padding:10px"><i class="ti ti-users"></i><p style="font-size:9px">{t('no_users')}</p></div>'; }}
        else {{ grid.innerHTML = recent.map(l => `<div style="background:rgba(100,80,255,0.02);border-radius:4px;padding:4px 6px;display:flex;justify-content:space-between;align-items:center"><div><div style="font-size:9px;font-weight:600;color:var(--t1)">${esc(l.label)}</div><div style="font-size:7px;color:var(--t3)">${l.active ? '🟢' : '🔴'}</div></div><div style="font-size:8px;color:var(--t2)">${fmtB(l.used_bytes || 0)}</div></div>`).join(''); }}
    }} catch(e) {{ console.error(e); }}
}}

async function loadInbound() {{
    try {{ const r = await authF('/api/inbound'); const data = await r.json(); document.getElementById('inbound-port').textContent = data.port || 443; document.getElementById('inbound-protocol').textContent = (data.protocol || 'vless').toUpperCase(); document.getElementById('inbound-host').textContent = data.host || '—'; document.getElementById('inbound-port-setting').value = data.port || 443; loadUsers(); }} catch(e) {{ console.error(e); }}
}}

async function updateInbound() {{
    const port = parseInt(document.getElementById('inbound-port-setting').value) || 443;
    try {{ const r = await authF('/api/inbound', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ port }}) }}); if(!r.ok) {{ toast('❌ {t('error')}', 'err'); return; }} toast('✅ {t('settings_saved')}', 'ok'); loadInbound(); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function loadUsers() {{
    try {{
        const r = await authF('/api/links');
        const {{ links=[] }} = await r.json();
        const grid = document.getElementById('users-grid');
        document.getElementById('users-count').textContent = links.length + ' {t('users')}';
        if(!links.length) {{ grid.innerHTML = '<div class="empty"><i class="ti ti-users"></i><p>{t('no_users')}</p></div>'; return; }}
        const fpEmoji = {{ chrome:'🌐', firefox:'🦊', safari:'🧭', edge:'🌊', ios:'📱', android:'🤖', safari_ios:'🍏', random:'🎲', none:'🚫' }};
        grid.innerHTML = links.map(l => {{
            const pct = l.limit_bytes === 0 ? 0 : Math.min(100, (l.used_bytes / l.limit_bytes) * 100);
            const active = l.active && !l.expired;
            const statusClass = active ? 'on' : 'off';
            const statusText = active ? '🟢' : '🔴';
            const lastSeen = l.last_connected_at ? new Date(l.last_connected_at).toLocaleString('fa-IR') : '—';
            const fp = l.fingerprint || 'chrome';
            const fpEmojiChar = fpEmoji[fp] || '🌐';
            const port = l.port || 443;
            return `<div class="user-card"><div class="head"><div class="name">🪐 ${esc(l.label)} ${l.has_password ? '<span class="lock-badge">🔒</span>' : ''}</div><span class="status ${statusClass}">${statusText}</span></div><div class="uuid">🔑 ${esc(l.uuid)}</div><div class="info"><span>📊 ${fmtB(l.used_bytes || 0)}</span><span>📦 ${l.limit_bytes === 0 ? '∞' : fmtB(l.limit_bytes)}</span><span>📱 ${l.max_devices || '∞'}</span><span>${l.expired ? '⛔' : '✅'}</span></div><div style="font-size:8px;color:var(--t3);margin-bottom:3px;display:flex;gap:6px;flex-wrap:wrap;"><span>🖥️ ${fpEmojiChar} ${fp}</span><span class="port-badge">🔌 ${port}</span>${l.group_id ? `<span style="font-size:7px;color:var(--t3)">📁 ${l.group_id.slice(0,10)}</span>` : ''}</div><div class="last-seen"><i class="ti ti-clock"></i> ${lastSeen}</div><div class="quota-info"><span>{t('usage')}</span><span>${pct.toFixed(0)}%</span></div><div class="quota-bar"><div class="quota-fill" style="width:${pct}%"></div></div><div class="actions"><button class="btn btn-o btn-sm" onclick="navigator.clipboard.writeText('${esc(l.vless_link)}').then(()=>toast('{t('config_copied')}','ok'))"><i class="ti ti-copy"></i></button><button class="btn btn-pur btn-sm" onclick="navigator.clipboard.writeText('${esc(l.sub_url)}').then(()=>toast('{t('sub_copied')}','ok'))"><i class="ti ti-link"></i></button><button class="btn btn-amber btn-sm" onclick="resetUsage('${l.uuid}')"><i class="ti ti-rotate"></i></button><button class="btn btn-pur btn-sm btn-icon" onclick="openEditModal('${l.uuid}')"><i class="ti ti-edit"></i></button><button class="btn btn-d btn-sm btn-icon" onclick="openDeleteModal('${l.uuid}')"><i class="ti ti-trash"></i></button></div></div>`;
        }}).join('');
    }} catch(e) {{ console.error(e); }}
}}

async function openEditModal(uuid) {{
    try {{ const r = await authF('/api/links'); const {{ links=[] }} = await r.json(); const link = links.find(l => l.uuid === uuid); if(!link) {{ toast('{t('user_not_found')}', 'err'); return; }} document.getElementById('edit-uuid').value = uuid; document.getElementById('edit-label').value = link.label || ''; document.getElementById('edit-password').value = ''; document.getElementById('edit-quota').value = link.limit_bytes === 0 ? '' : (link.limit_bytes / (1024**3)).toFixed(1); document.getElementById('edit-exp').value = link.expires_at ? Math.ceil((new Date(link.expires_at) - new Date()) / (1000*60*60*24)) : ''; document.getElementById('edit-devices').value = link.max_devices || 0; document.getElementById('edit-status').value = link.active ? 'true' : 'false'; document.getElementById('edit-fingerprint').value = link.fingerprint || 'chrome'; document.getElementById('edit-password-section').style.display = link.has_password ? 'block' : 'none'; openModal('modal-edit'); }} catch(e) {{ toast('{t('error')}', 'err'); }}
}}

async function saveEdit() {{
    const uuid = document.getElementById('edit-uuid').value;
    const password = document.getElementById('edit-password').value.trim();
    const label = document.getElementById('edit-label').value.trim() || 'کاربر';
    const quota = parseFloat(document.getElementById('edit-quota').value) || 0;
    const exp = parseInt(document.getElementById('edit-exp').value) || 0;
    const devices = parseInt(document.getElementById('edit-devices').value) || 0;
    const active = document.getElementById('edit-status').value === 'true';
    const fingerprint = document.getElementById('edit-fingerprint').value || 'chrome';
    try {{ const r = await authF('/api/links/' + uuid, {{ method: 'PATCH', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ label, limit_value: quota, limit_unit: 'GB', expires_days: exp, max_devices: devices, active, password, fingerprint }}) }}); if(!r.ok) {{ if(r.status === 403) {{ toast('❌ {t('wrong_password')}', 'err'); return; }} throw new Error(); }} closeModal('modal-edit'); toast('✅ {t('user_updated')}', 'ok'); loadUsers(); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

function openDeleteModal(uuid) {{ document.getElementById('delete-uuid').value = uuid; document.getElementById('delete-password').value = ''; openModal('modal-delete'); }}
async function confirmDelete() {{
    const uuid = document.getElementById('delete-uuid').value;
    const password = document.getElementById('delete-password').value.trim();
    try {{ const r = await authF('/api/links/' + uuid, {{ method: 'DELETE', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ password }}) }}); if(!r.ok) {{ if(r.status === 403) {{ toast('❌ {t('wrong_password')}', 'err'); return; }} throw new Error(); }} closeModal('modal-delete'); toast('✅ {t('user_deleted')}', 'ok'); loadUsers(); loadDashboard(); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function resetUsage(uuid) {{
    if(!confirm('{t('reset_usage')}?')) return;
    try {{ const r = await authF('/api/links/' + uuid, {{ method: 'PATCH', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ reset_usage: true }}) }}); if(!r.ok) throw new Error(); toast('✅ {t('usage_reset')}', 'ok'); loadUsers(); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function loadConnections() {{
    try {{ const r = await authF('/api/connections'); const d = await r.json(); const grid = document.getElementById('conns-grid'); const count = d.count || 0; document.getElementById('conn-count').textContent = count + ' {t('connections')}'; if(!count) {{ grid.innerHTML = '<div class="empty"><i class="ti ti-plug-off"></i><p>{t('no_connections')}</p></div>'; return; }} grid.innerHTML = d.connections.map(c => {{ const secs = c.connected_at ? Math.max(0, Math.floor((Date.now() - new Date(c.connected_at).getTime()) / 1000)) : 0; const dur = secs < 60 ? secs + 'ث' : secs < 3600 ? Math.floor(secs/60) + 'د' : Math.floor(secs/3600) + 'س'; return `<div class="conn-card"><div class="ip"><span class="conn-status-dot"></span> ${esc(c.ip)}</div><div class="label">${esc(c.label || 'نامشخص')}</div><div class="conn-info"><span>📥 ${esc(c.bytes_fmt || '0 B')}</span><span>⏱ ${dur}</span></div></div>`; }}).join(''); }} catch(e) {{ console.error(e); }}
}}

async function loadLogs() {{
    try {{ const r = await authF('/api/activity'); const data = await r.json(); const logs = data.logs || []; document.getElementById('logs-count').textContent = logs.length + ' {t('logs')}'; const container = document.getElementById('logs-container'); if(!logs.length) {{ container.innerHTML = '<div class="empty"><i class="ti ti-notes"></i><p>{t('no_logs')}</p></div>'; return; }} container.innerHTML = logs.map(log => {{ const time = log.time ? new Date(log.time).toLocaleString('fa-IR') : '—'; const color = log.level === 'err' ? '#F87171' : log.level === 'warn' ? '#FCD34D' : '#A78BFA'; return `<div style="padding:3px 0;border-bottom:1px solid rgba(100,80,255,0.02);display:flex;gap:6px"><span style="color:${color};font-weight:700">[${(log.level || 'info').toUpperCase()}]</span><span style="color:var(--t3)">${time}</span><span>${esc(log.message)}</span></div>`; }}).join(''); }} catch(e) {{ console.error(e); }}
}}

async function changePassword() {{
    const oldPw = document.getElementById('old-password').value;
    const newPw = document.getElementById('new-password').value;
    const confirmPw = document.getElementById('confirm-password').value;
    const result = document.getElementById('password-result');
    if(!oldPw || !newPw || !confirmPw) {{ result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ {t('password_too_short')}'; return; }}
    if(newPw.length < 4) {{ result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ {t('password_too_short')}'; return; }}
    if(newPw !== confirmPw) {{ result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ {t('password_mismatch')}'; return; }}
    try {{ const r = await authF('/api/change-password', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ old_password: oldPw, new_password: newPw }}) }}); const data = await r.json(); if(!r.ok) {{ result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ ' + (data.detail || data.message || '{t('error')}'); return; }} result.style.display='block'; result.style.color='#34D399'; result.innerHTML='✅ {t('password_changed')}'; document.getElementById('old-password').value = ''; document.getElementById('new-password').value = ''; document.getElementById('confirm-password').value = ''; toast('✅ {t('password_changed')}', 'ok'); }} catch(e) {{ result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ {t('error')}'; }}
}}

let rgbMode = false;
async function loadRGBStatus() {{ try {{ const r = await authF('/api/settings'); const data = await r.json(); rgbMode = data.rgb_mode || false; updateRGBUI(); }} catch(e) {{}} }}
function updateRGBUI() {{ const sw = document.getElementById('rgb-switch'); if(rgbMode) {{ document.body.classList.add('rgb-mode'); sw.classList.add('on'); }} else {{ document.body.classList.remove('rgb-mode'); sw.classList.remove('on'); }} }}
async function toggleRGB() {{ const newState = !rgbMode; try {{ const r = await authF('/api/settings/rgb', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ enabled: newState }}) }}); const data = await r.json(); rgbMode = data.rgb_mode; updateRGBUI(); toast(rgbMode ? '🌈 {t('rgb_mode')} فعال شد' : '🌙 {t('rgb_mode')} غیرفعال شد', 'ok'); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function createBackup() {{
    try {{ const r = await authF('/api/backup'); const data = await r.json(); const blob = new Blob([JSON.stringify(data, null, 2)], {{type:'application/json'}}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `eagle_backup_${{new Date().toISOString().slice(0,10)}}.json`; a.click(); URL.revokeObjectURL(url); toast('✅ {t('backup_created')}', 'ok'); }} catch(e) {{ toast('❌ {t('error')}', 'err'); }}
}}

async function restoreBackup(event) {{
    const file = event.target.files[0]; if(!file) return;
    try {{ const text = await file.text(); const data = JSON.parse(text); const r = await authF('/api/backup/restore', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(data) }}); if(!r.ok) {{ toast('❌ {t('error')}', 'err'); return; }} toast('✅ {t('backup_restored')}', 'ok'); setTimeout(() => location.reload(), 1000); }} catch(e) {{ toast('❌ {t('error')}: ' + e.message, 'err'); }} event.target.value = '';
}}

document.addEventListener('DOMContentLoaded', async () => {{
    try {{ const r = await fetch('/api/me'); const d = await r.json(); if(!d.authenticated) location.href = '/login'; }} catch(e) {{ location.href = '/login'; }}
    setLang(currentLang);
    await loadRGBStatus();
    loadDashboard(); loadInbound(); loadUsers(); loadConnections(); loadLogs();
    setInterval(() => {{ if(document.getElementById('pg-dashboard').classList.contains('on')) loadDashboard(); if(document.getElementById('pg-connections').classList.contains('on')) loadConnections(); if(document.getElementById('pg-users').classList.contains('on')) loadUsers(); }}, 5000);
}});
</script>
</body></html>"""

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/dashboard")
    lang = request.cookies.get("eagle-lang", SETTINGS.get("language", "fa"))
    if lang not in ["fa", "en"]:
        lang = "fa"
    return HTMLResponse(content=get_login_html(lang))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/login")
    lang = request.cookies.get("eagle-lang", SETTINGS.get("language", "fa"))
    if lang not in ["fa", "en"]:
        lang = "fa"
    return HTMLResponse(content=get_dashboard_html(lang))

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>🪐 Eagle Gateway</title>
    <style>body{font-family:sans-serif;background:#0a0a0f;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}.card{text-align:center;padding:40px;background:rgba(20,20,40,0.7);border-radius:20px;border:1px solid rgba(100,80,255,0.2)}h1{font-size:48px;margin:0}.sub{color:#888}a{color:#7C6BFF;text-decoration:none;font-weight:bold}</style>
    </head>
    <body>
    <div class="card"><h1>🪐</h1><h2>Eagle Gateway v10 Pro</h2><p class="sub">VPN Management Panel</p><a href="/login">Login →</a></div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=CONFIG["port"], log_level="info", workers=1)
