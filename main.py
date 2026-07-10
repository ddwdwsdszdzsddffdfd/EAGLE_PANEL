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

# ─── تنظیمات لاگ ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Eagle-Gateway")

# ─── تنظیمات زمان ──────────────────────────────────────────────────────────
try:
    IRAN_TZ = ZoneInfo("Asia/Tehran")
except:
    IRAN_TZ = None

def now_ir():
    if IRAN_TZ:
        return datetime.now(IRAN_TZ)
    return datetime.now()

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

def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()

def generate_uuid() -> str:
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

def get_host() -> str:
    host = os.environ.get("RAILWAY_PUBLIC_DOMAIN", os.environ.get("RENDER_EXTERNAL_URL", CONFIG["host"]))
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
    except:
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
    try:
        limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)
        timeout = httpx.Timeout(30.0, connect=10.0)
        http_client = httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True)
    except:
        http_client = None
    await load_state()
    log_activity("system", "🪐 Eagle Gateway راه‌اندازی شد", "ok")
    logger.info(f"🪐 Eagle Gateway started on port {CONFIG['port']}")

@app.on_event("shutdown")
async def shutdown():
    await save_state()
    if http_client:
        try:
            await http_client.aclose()
        except:
            pass

# ─── API Routes ─────────────────────────────────────────────────────────────

@app.post("/api/settings/language")
async def set_language(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except:
        body = {}
    lang = body.get("language", "fa")
    if lang in ["fa", "en"]:
        SETTINGS["language"] = lang
        await save_state()
        return {"ok": True, "language": lang}
    raise HTTPException(status_code=400, detail="Invalid language")

@app.get("/api/language")
async def get_language():
    return {"language": SETTINGS.get("language", "fa")}

@app.post("/api/change-password")
async def change_password(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except:
        body = {}
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

@app.get("/api/settings")
async def get_settings(_=Depends(require_auth)):
    return SETTINGS

@app.post("/api/settings/rgb")
async def toggle_rgb(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except:
        body = {}
    SETTINGS["rgb_mode"] = bool(body.get("enabled", False))
    await save_state()
    return {"rgb_mode": SETTINGS["rgb_mode"]}

@app.get("/api/dashboard/stats")
async def dashboard_stats(_=Depends(require_auth)):
    try:
        disk_usage = psutil.disk_usage('/')
    except:
        disk_usage = type('obj', (object,), {'total': 0, 'used': 0, 'free': 0, 'percent': 0})()
    
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
    try:
        body = await request.json()
    except:
        body = {}
    port = body.get("port", 443)
    if port < 1 or port > 65535:
        raise HTTPException(status_code=400, detail="Invalid port")
    SETTINGS["inbound_port"] = port
    await save_state()
    return {"ok": True, "port": port}

@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except:
        body = {}
    
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
    try:
        body = await request.json()
    except:
        body = {}
    
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
    try:
        body = await request.json()
    except:
        body = {}
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

@app.post("/api/login")
async def api_login(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
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

@app.get("/api/activity")
async def get_activity_logs(_=Depends(require_auth)):
    limit = 100
    logs = list(activity_logs)[-limit:]
    return {"logs": logs}

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
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    try:
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

# ─── WebSocket Tunnel ──────────────────────────────────────────────────────

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
        try:
            hourly_traffic[datetime.now().strftime("%H:00")] = hourly_traffic.get(datetime.now().strftime("%H:00"), 0) + n
        except:
            pass
        
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
        except:
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
    except:
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
            except:
                pass
        connections.pop(conn_id, None)
        await remove_device_connection(uuid, client_ip)
        logger.info(f"🔌 WS closed [{conn_id}] total={len(connections)}")

# ─── Subscriptions ─────────────────────────────────────────────────────────

@app.get("/sub-group/{group_id}")
async def subscription_group(group_id: str, request: Request):
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
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    
    if not link:
        return HTMLResponse("""
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

# ─── Pages ──────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/dashboard")
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🪐 پنل عقاب · ورود</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}:root{--bg:#0a0a1a;--card:rgba(10,10,30,0.75);--card-b:rgba(100,80,255,0.12);--accent:#7C6BFF;--t1:#F0EEFF;--t2:#8888BB;--t3:#555577;--border:rgba(100,80,255,0.08)}
body{font-family:'Vazirmatn',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0a0a1a,#1a0a2a,#0a0a2a);padding:20px;color:var(--t1)}
.container{position:relative;z-index:10;display:grid;grid-template-columns:1fr 1fr;max-width:1100px;width:100%;background:var(--card);backdrop-filter:blur(30px);border-radius:24px;border:1px solid var(--border);overflow:hidden;box-shadow:0 0 80px rgba(100,80,255,0.05)}
.login-section{padding:48px 40px}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:32px}
.brand-icon{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:22px}
.brand-text{font-size:16px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.brand-sub{font-size:9px;color:var(--t3)}
.welcome{font-size:22px;font-weight:800;color:var(--t1);margin-bottom:4px}
.sub-text{font-size:13px;color:var(--t3);margin-bottom:28px}
.field{margin-bottom:18px}
.field label{display:block;font-size:10px;font-weight:600;color:var(--t2);margin-bottom:4px}
.field input{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--border);background:rgba(0,0,20,.3);color:var(--t1);font-family:inherit;font-size:14px;outline:none}
.field input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.08)}
.options{display:flex;justify-content:space-between;align-items:center;margin:14px 0 20px;font-size:12px}
.options label{display:flex;align-items:center;gap:6px;color:var(--t2);cursor:pointer}
.options label input[type="checkbox"]{accent-color:var(--accent);width:16px;height:16px;cursor:pointer}
.btn-login{width:100%;padding:12px;border-radius:10px;border:none;cursor:pointer;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);color:#fff;font-family:inherit;font-size:15px;font-weight:700;transition:all .3s;box-shadow:0 4px 30px rgba(100,80,255,.25)}
.btn-login:hover{transform:translateY(-2px);box-shadow:0 8px 40px rgba(100,80,255,.35)}
.btn-login:disabled{opacity:.5;cursor:not-allowed}
.signup-text{text-align:center;margin-top:18px;font-size:12px;color:var(--t3)}
.signup-text a{color:var(--accent);text-decoration:none;font-weight:600}
.error-box{display:none;background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.15);border-radius:8px;padding:10px 12px;margin-bottom:14px;font-size:12px;color:#F87171;align-items:center;gap:8px}
.error-box.show{display:flex}
.info-section{background:linear-gradient(135deg,#0a0a1a,#1a0a2a);padding:48px 36px;display:flex;flex-direction:column;justify-content:center;border-right:1px solid var(--border)}
.info-title{font-size:22px;font-weight:800;color:var(--t1);margin-bottom:6px}
.info-sub{font-size:13px;color:var(--t3);margin-bottom:24px}
.features{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.feature{background:rgba(100,80,255,0.03);border-radius:12px;padding:14px 12px;text-align:center;border:1px solid rgba(100,80,255,0.04)}
.feature .icon{font-size:28px;display:block;margin-bottom:4px}
.feature .name{font-size:11px;font-weight:600;color:var(--t1)}
.feature .desc{font-size:8px;color:var(--t3);margin-top:2px}
@media(max-width:900px){.container{grid-template-columns:1fr}.info-section{display:none}.login-section{padding:32px 24px}}
@media(max-width:480px){.login-section{padding:24px 16px}.welcome{font-size:19px}}
</style>
</head>
<body>
<div class="container">
    <div class="login-section">
        <div class="brand"><div class="brand-icon">🪐</div><div><div class="brand-text">پنل عقاب</div><div class="brand-sub">مدیریت کاربران</div></div></div>
        <div class="welcome">خوش آمدید</div>
        <div class="sub-text">وارد حساب کاربری خود شوید</div>
        <div class="error-box" id="error-box"><i class="ti ti-alert-circle"></i><span id="error-text"></span></div>
        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="field"><label>نام کاربری یا ایمیل</label><input type="text" id="username" placeholder="نام کاربری" value="admin" dir="ltr"></div>
            <div class="field"><label>رمز عبور</label><input type="password" id="password" placeholder="رمز عبور را وارد کنید" dir="ltr"></div>
            <div class="options"><label><input type="checkbox" id="remember"> <span>مرا به خاطر بسپار</span></label></div>
            <button class="btn-login" type="submit" id="login-btn"><i class="ti ti-login-2"></i> ورود</button>
        </form>
        <div class="signup-text">حساب کاربری ندارید؟ <a href="/dashboard">ثبت نام</a></div>
    </div>
    <div class="info-section">
        <div class="info-title">🪐 پنل عقاب</div>
        <div class="info-sub">سریع‌ترین و امن‌ترین اتصال</div>
        <div class="features">
            <div class="feature"><span class="icon">🔒</span><div class="name">امن</div><div class="desc">حریم خصوصی شما</div></div>
            <div class="feature"><span class="icon">⚡</span><div class="name">سریع</div><div class="desc">سرعت برق آسا</div></div>
            <div class="feature"><span class="icon">🌍</span><div class="name">جهانی</div><div class="desc">سرورهای جهانی</div></div>
            <div class="feature"><span class="icon">🕵️</span><div class="name">ناشناس</div><div class="desc">خصوصی بمانید</div></div>
        </div>
    </div>
</div>
<script>
async function handleLogin(e){e.preventDefault();const btn=document.getElementById('login-btn');const err=document.getElementById('error-box');const errText=document.getElementById('error-text');err.classList.remove('show');btn.disabled=true;btn.innerHTML='<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال ورود...';try{const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:document.getElementById('password').value,remember:document.getElementById('remember').checked})});if(!r.ok){const d=await r.json().catch(()=>({}));errText.textContent=d.detail||'رمز عبور اشتباه است';err.classList.add('show');btn.disabled=false;btn.innerHTML='<i class="ti ti-login-2"></i> ورود';return;}window.location.href='/dashboard';}catch(e){errText.textContent='خطا در ارتباط با سرور';err.classList.add('show');btn.disabled=false;btn.innerHTML='<i class="ti ti-login-2"></i> ورود';}}
document.getElementById('password').addEventListener('keydown',(e)=>{if(e.key==='Enter')document.getElementById('login-form').dispatchEvent(new Event('submit'));});
</script>
</body>
</html>
""")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/login")
    return HTMLResponse(open("dashboard.html").read() if os.path.exists("dashboard.html") else """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>پنل عقاب</title></head>
<body style="background:#0a0a1a;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:20px">
<h1 style="font-size:48px">🪐</h1>
<h2>پنل عقاب</h2>
<p style="color:#888">داشبورد با موفقیت بارگذاری شد</p>
<a href="/api/links" style="color:#7C6BFF">مشاهده کاربران</a>
<button onclick="fetch('/api/logout',{method:'POST'}).then(()=>location.href='/login')" style="padding:10px 20px;border-radius:8px;border:none;background:#EF4444;color:#fff;cursor:pointer">خروج</button>
</body>
</html>
""")

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>🪐 Eagle Gateway</title>
<style>body{font-family:sans-serif;background:#0a0a0f;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}.card{text-align:center;padding:40px;background:rgba(20,20,40,0.7);border-radius:20px;border:1px solid rgba(100,80,255,0.2)}h1{font-size:48px;margin:0}.sub{color:#888}a{color:#7C6BFF;text-decoration:none;font-weight:bold}</style></head>
<body><div class="card"><h1>🪐</h1><h2>Eagle Gateway</h2><p class="sub">VPN Management Panel</p><a href="/login">Login →</a></div></body>
</html>
""")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=CONFIG["port"], log_level="info")
