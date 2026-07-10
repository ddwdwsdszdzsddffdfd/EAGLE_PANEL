
LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🪐 ورود · پنل عقاب</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0a1a;
  --card:rgba(10,10,30,0.75);
  --card-b:rgba(100,80,255,0.12);
  --accent:#7C6BFF;
  --accent2:#A78BFA;
  --accent3:#5B4BD9;
  --t1:#F0EEFF;
  --t2:#8888BB;
  --t3:#555577;
  --border:rgba(100,80,255,0.08);
  --glow:0 0 80px rgba(100,80,255,0.05);
}
body{font-family:'Vazirmatn',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0a0a1a,#1a0a2a,#0a0a2a);padding:20px;color:var(--t1);position:relative;overflow:hidden}
.stars{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.star{position:absolute;border-radius:50%;background:#fff;animation:twinkle 3s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:0.2}50%{opacity:0.8}}
.glow-orb{position:fixed;border-radius:50%;filter:blur(150px);z-index:0;animation:orbFloat 6s ease-in-out infinite;pointer-events:none}
.orb1{width:500px;height:500px;background:rgba(100,80,255,0.05);top:-200px;right:-100px}
.orb2{width:400px;height:400px;background:rgba(167,139,250,0.04);bottom:-100px;left:-80px;animation-delay:2s}
@keyframes orbFloat{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(30px,-30px) scale(1.1)}}
.container{position:relative;z-index:10;display:grid;grid-template-columns:1fr 1fr;max-width:1100px;width:100%;background:var(--card);backdrop-filter:blur(30px);border-radius:24px;border:1px solid var(--border);overflow:hidden;box-shadow:var(--glow),0 25px 80px rgba(0,0,0,0.6)}
.login-section{padding:48px 40px}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:32px}
.brand-icon{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 40px rgba(100,80,255,0.2)}
.brand-text{font-size:16px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.brand-sub{font-size:9px;color:var(--t3);margin-top:0px;-webkit-text-fill-color:var(--t3)}
.welcome{font-size:22px;font-weight:800;color:var(--t1);margin-bottom:4px}
.sub-text{font-size:13px;color:var(--t3);margin-bottom:28px}
.field{margin-bottom:18px}
.field label{display:block;font-size:10px;font-weight:600;color:var(--t2);margin-bottom:4px}
.field input{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--border);background:rgba(0,0,20,.3);color:var(--t1);font-family:inherit;font-size:14px;outline:none;transition:.3s}
.field input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.08),0 0 30px rgba(100,80,255,.04)}
.field input::placeholder{color:var(--t3)}
.options{display:flex;justify-content:space-between;align-items:center;margin:14px 0 20px;font-size:12px}
.options label{display:flex;align-items:center;gap:6px;color:var(--t2);cursor:pointer}
.options label input[type="checkbox"]{accent-color:var(--accent);width:16px;height:16px;cursor:pointer}
.btn-login{width:100%;padding:12px;border-radius:10px;border:none;cursor:pointer;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);background-size:200% 200%;animation:gradientMove 4s ease infinite;color:#fff;font-family:inherit;font-size:15px;font-weight:700;transition:all .3s;box-shadow:0 4px 30px rgba(100,80,255,.25)}
@keyframes gradientMove{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.btn-login:hover{transform:translateY(-2px);box-shadow:0 8px 40px rgba(100,80,255,.35)}
.btn-login:disabled{opacity:.5;cursor:not-allowed;transform:none}
.or-divider{display:flex;align-items:center;gap:14px;margin:20px 0;color:var(--t3);font-size:11px}
.or-divider::before,.or-divider::after{content:'';flex:1;height:1px;background:var(--border)}
.connect-btn{width:100%;padding:12px;border-radius:10px;border:1px solid var(--border);background:rgba(100,80,255,0.03);color:var(--t1);font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:.3s;display:flex;align-items:center;justify-content:center;gap:8px}
.connect-btn:hover{background:rgba(100,80,255,0.06);border-color:rgba(100,80,255,0.2)}
.signup-text{text-align:center;margin-top:18px;font-size:12px;color:var(--t3)}
.signup-text a{color:var(--accent);text-decoration:none;font-weight:600}
.signup-text a:hover{text-decoration:underline}
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
.lang-toggle{position:fixed;top:20px;left:20px;z-index:50;display:flex;gap:6px;background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:10px;padding:4px}
.lang-toggle button{background:none;border:none;color:var(--t3);font-family:inherit;font-size:11px;font-weight:600;padding:4px 10px;border-radius:6px;cursor:pointer;transition:.3s}
.lang-toggle button.active{background:linear-gradient(135deg,#7C6BFF,#5B4BD9);color:#fff}
.lang-toggle button:hover:not(.active){color:var(--t1)}
@media(max-width:900px){.container{grid-template-columns:1fr}.info-section{display:none}.login-section{padding:32px 24px}}
@media(max-width:480px){.login-section{padding:24px 16px}.welcome{font-size:19px}}
</style>
</head>
<body>
<div class="stars">
    <div class="star" style="width:2px;height:2px;top:10%;left:5%;animation-delay:0s"></div>
    <div class="star" style="width:3px;height:3px;top:20%;left:15%;animation-delay:1s"></div>
    <div class="star" style="width:1px;height:1px;top:30%;left:25%;animation-delay:2s"></div>
    <div class="star" style="width:2px;height:2px;top:15%;left:35%;animation-delay:0.5s"></div>
    <div class="star" style="width:3px;height:3px;top:40%;left:45%;animation-delay:1.5s"></div>
    <div class="star" style="width:1px;height:1px;top:25%;left:55%;animation-delay:2.5s"></div>
    <div class="star" style="width:2px;height:2px;top:50%;left:65%;animation-delay:0.7s"></div>
    <div class="star" style="width:3px;height:3px;top:60%;left:75%;animation-delay:1.8s"></div>
    <div class="star" style="width:1px;height:1px;top:70%;left:85%;animation-delay:2.2s"></div>
    <div class="star" style="width:2px;height:2px;top:80%;left:95%;animation-delay:1.2s"></div>
</div>
<div class="glow-orb orb1"></div><div class="glow-orb orb2"></div>

<div class="lang-toggle">
    <button class="active" onclick="setLang('fa')">🇮🇷 فارسی</button>
    <button onclick="setLang('en')">🇬🇧 English</button>
</div>

<div class="container">
    <div class="login-section">
        <div class="brand">
            <div class="brand-icon">🪐</div>
            <div>
                <div class="brand-text">پنل عقاب</div>
                <div class="brand-sub">مدیریت کاربران</div>
            </div>
        </div>
        <div class="welcome" id="welcome-text">خوش آمدید</div>
        <div class="sub-text" id="sub-text">وارد حساب کاربری خود شوید</div>
        
        <div class="error-box" id="error-box"><i class="ti ti-alert-circle"></i><span id="error-text"></span></div>
        
        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="field">
                <label id="label-username">نام کاربری یا ایمیل</label>
                <input type="text" id="username" placeholder="نام کاربری" value="admin" dir="ltr">
            </div>
            <div class="field">
                <label id="label-password">رمز عبور</label>
                <input type="password" id="password" placeholder="رمز عبور را وارد کنید" dir="ltr">
            </div>
            <div class="options">
                <label><input type="checkbox" id="remember"> <span id="remember-text">مرا به خاطر بسپار</span></label>
            </div>
            <button class="btn-login" type="submit" id="login-btn"><i class="ti ti-login-2"></i> <span id="login-text">ورود</span></button>
        </form>
        
        <div class="or-divider"><span id="or-text">یا</span></div>
        
        <button class="connect-btn" onclick="quickConnect()">
            <i class="ti ti-plug"></i> <span id="connect-text">اتصال با یک کلیک</span>
        </button>
        
        <div class="signup-text" id="signup-text">
            حساب کاربری ندارید؟ <a href="/dashboard">ثبت نام</a>
        </div>
    </div>
    
    <div class="info-section">
        <div class="info-title" id="info-title">🪐 پنل عقاب</div>
        <div class="info-sub" id="info-sub">سریع‌ترین و امن‌ترین اتصال</div>
        <div class="features">
            <div class="feature"><span class="icon">🔒</span><div class="name" id="f-secure">امن</div><div class="desc" id="f-secure-d">حریم خصوصی شما</div></div>
            <div class="feature"><span class="icon">⚡</span><div class="name" id="f-fast">سریع</div><div class="desc" id="f-fast-d">سرعت برق آسا</div></div>
            <div class="feature"><span class="icon">🌍</span><div class="name" id="f-global">جهانی</div><div class="desc" id="f-global-d">سرورهای جهانی</div></div>
            <div class="feature"><span class="icon">🕵️</span><div class="name" id="f-anon">ناشناس</div><div class="desc" id="f-anon-d">خصوصی بمانید</div></div>
        </div>
    </div>
</div>

<script>
const translations = {
    fa: {
        welcome: "خوش آمدید",
        sub: "وارد حساب کاربری خود شوید",
        username: "نام کاربری یا ایمیل",
        password: "رمز عبور",
        remember: "مرا به خاطر بسپار",
        login: "ورود",
        or: "یا",
        connect: "اتصال با یک کلیک",
        signup: "حساب کاربری ندارید؟",
        signup_link: "ثبت نام",
        secure: "امن",
        secure_d: "حریم خصوصی شما",
        fast: "سریع",
        fast_d: "سرعت برق آسا",
        global: "جهانی",
        global_d: "سرورهای جهانی",
        anon: "ناشناس",
        anon_d: "خصوصی بمانید",
        info_title: "🪐 پنل عقاب",
        info_sub: "سریع‌ترین و امن‌ترین اتصال"
    },
    en: {
        welcome: "Welcome Back",
        sub: "Login to your VPN account",
        username: "Username or Email",
        password: "Password",
        remember: "Remember me",
        login: "Login",
        or: "OR",
        connect: "Connect with One Click",
        signup: "Don't have an account?",
        signup_link: "Sign up",
        secure: "Secure",
        secure_d: "Your Privacy",
        fast: "Fast",
        fast_d: "Lightning Speed",
        global: "Global",
        global_d: "Worldwide Servers",
        anon: "Anonymous",
        anon_d: "Stay Private",
        info_title: "🪐 Eagle Panel",
        info_sub: "Fastest & Most Secure Connection"
    }
};

let currentLang = localStorage.getItem('eagle-lang') || 'fa';

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('eagle-lang', lang);
    document.querySelectorAll('.lang-toggle button').forEach(b => b.classList.toggle('active', b.textContent.includes(lang === 'fa' ? 'فارسی' : 'English')));
    updateTexts();
}

function updateTexts() {
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
    document.getElementById('f-secure').textContent = t.secure;
    document.getElementById('f-secure-d').textContent = t.secure_d;
    document.getElementById('f-fast').textContent = t.fast;
    document.getElementById('f-fast-d').textContent = t.fast_d;
    document.getElementById('f-global').textContent = t.global;
    document.getElementById('f-global-d').textContent = t.global_d;
    document.getElementById('f-anon').textContent = t.anon;
    document.getElementById('f-anon-d').textContent = t.anon_d;
    document.getElementById('info-title').textContent = t.info_title;
    document.getElementById('info-sub').textContent = t.info_sub;
}

async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const err = document.getElementById('error-box');
    const errText = document.getElementById('error-text');
    
    err.classList.remove('show');
    btn.disabled = true;
    btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال ورود...';
    
    try {
        const r = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                password: document.getElementById('password').value,
                remember: document.getElementById('remember').checked
            })
        });
        
        if (!r.ok) {
            const d = await r.json().catch(() => ({}));
            errText.textContent = d.detail || 'رمز عبور اشتباه است';
            err.classList.add('show');
            btn.disabled = false;
            btn.innerHTML = '<i class="ti ti-login-2"></i> ' + translations[currentLang].login;
            return;
        }
        
        window.location.href = '/dashboard';
    } catch(e) {
        errText.textContent = 'خطا در ارتباط با سرور';
        err.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = '<i class="ti ti-login-2"></i> ' + translations[currentLang].login;
    }
}

function quickConnect() {
    document.getElementById('password').value = '123456';
    document.getElementById('remember').checked = true;
    document.getElementById('login-form').dispatchEvent(new Event('submit'));
}

document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('login-form').dispatchEvent(new Event('submit'));
});

setLang(currentLang);
</script>
</body></html>"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🪐 پنل عقاب · خانه</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0a1a;
  --bg2:#12122a;
  --bg3:#1a1a3a;
  --card:rgba(10,10,30,0.7);
  --card-b:rgba(100,80,255,0.08);
  --card-bh:rgba(100,80,255,0.15);
  --accent:#7C6BFF;
  --accent2:#A78BFA;
  --accent3:#5B4BD9;
  --green:#10B981;
  --green-bg:rgba(16,185,129,0.08);
  --green-t:#34D399;
  --red:#EF4444;
  --red-bg:rgba(239,68,68,0.08);
  --red-t:#F87171;
  --amber:#F59E0B;
  --amber-bg:rgba(245,158,11,0.08);
  --amber-t:#FCD34D;
  --t1:#F0EEFF;
  --t2:#8888BB;
  --t3:#555577;
  --sidebar-w:180px;
  --radius:12px;
  --shadow:0 8px 32px rgba(0,0,0,0.5),0 0 60px rgba(100,80,255,0.02);
}
body{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;display:flex;font-size:13px;position:relative;overflow-x:hidden}
.stars-bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.star-bg{position:absolute;border-radius:50%;background:#fff;animation:twinkleBg 4s ease-in-out infinite}
@keyframes twinkleBg{0%,100%{opacity:0.1}50%{opacity:0.4}}
.glow-main{position:fixed;border-radius:50%;filter:blur(200px);z-index:0;pointer-events:none}
.glow-left{width:600px;height:600px;background:rgba(100,80,255,0.02);top:-300px;left:-200px}
.glow-right{width:500px;height:500px;background:rgba(167,139,250,0.02);bottom:-200px;right:-100px}
.sidebar{width:var(--sidebar-w);min-height:100vh;background:var(--card);backdrop-filter:blur(30px);border-left:1px solid var(--card-b);display:flex;flex-direction:column;flex-shrink:0;position:fixed;right:0;top:0;bottom:0;z-index:200;transition:transform .3s;box-shadow:var(--shadow)}
.logo{display:flex;align-items:center;gap:10px;padding:16px 12px 12px;border-bottom:1px solid var(--card-b)}
.logo-icon{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;box-shadow:0 0 30px rgba(100,80,255,0.15)}
.logo-name{font-size:13px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo-sub{font-size:7px;color:var(--t3);margin-top:0px}
.nav-wrap{flex:1;overflow-y:auto;padding:6px 0;position:relative;z-index:1}
.nav-it{display:flex;align-items:center;gap:8px;padding:8px 10px;color:var(--t3);font-size:11px;cursor:pointer;border-right:2px solid transparent;transition:all .2s;margin:1px 4px;border-radius:6px}
.nav-it i{font-size:14px;width:18px;text-align:center;flex-shrink:0}
.nav-it:hover{background:rgba(100,80,255,0.05);color:var(--t2)}
.nav-it.on{background:rgba(100,80,255,0.08);color:var(--t1);border-right-color:var(--accent);font-weight:600;box-shadow:0 0 30px rgba(100,80,255,0.03)}
.sb-foot{padding:10px 12px;border-top:1px solid var(--card-b)}
.logout-btn{display:flex;align-items:center;justify-content:center;gap:6px;background:var(--red-bg);color:var(--red-t);border-radius:6px;padding:6px;font-size:10px;font-weight:500;font-family:inherit;border:1px solid rgba(239,68,68,0.1);cursor:pointer;width:100%;transition:.2s}
.logout-btn:hover{background:rgba(239,68,68,0.15)}
.mob-top{display:none;position:fixed;top:0;right:0;left:0;height:48px;background:var(--card);backdrop-filter:blur(30px);border-bottom:1px solid var(--card-b);z-index:150;align-items:center;justify-content:space-between;padding:0 10px}
.mob-top .ml{display:flex;align-items:center;gap:6px}
.mob-logo{width:26px;height:26px;border-radius:6px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9);display:flex;align-items:center;justify-content:center;font-size:13px}
.mob-title{color:var(--t1);font-size:11px;font-weight:700}
.menu-btn{background:rgba(100,80,255,0.05);border:1px solid var(--card-b);color:var(--t2);width:30px;height:30px;border-radius:6px;font-size:14px;display:flex;align-items:center;justify-content:center;cursor:pointer}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:190;backdrop-filter:blur(6px)}
.overlay.show{display:block}
.main{margin-right:var(--sidebar-w);flex:1;padding:16px 20px 80px;min-width:0;transition:margin .3s;position:relative;z-index:1}
.pg{display:none;animation:pageIn .3s ease}
.pg.on{display:block}
@keyframes pageIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.tb-title{font-size:17px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:6px}
.tb-title i{color:var(--accent);font-size:19px}
.tb-sub{font-size:10px;color:var(--t3);margin-top:1px}
.tb-right{display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.badge{font-size:8px;padding:2px 8px;border-radius:12px;font-weight:700;display:inline-flex;align-items:center;gap:3px;white-space:nowrap}
.bg-green{background:var(--green-bg);color:var(--green-t)}
.bg-blue{background:rgba(100,80,255,0.1);color:var(--accent)}
.bg-fire{background:rgba(100,80,255,0.08);color:#A78BFA}
.bg-amber{background:var(--amber-bg);color:var(--amber-t)}
.dot{width:5px;height:5px;border-radius:50%;flex-shrink:0;display:inline-block}
.dg{background:var(--green)}.dr{background:var(--red)}.da{background:var(--amber)}.db{background:var(--accent)}
.pulse{animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
.stats-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:16px}
.stat-card{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 8px;transition:all .3s;text-align:center;position:relative;overflow:hidden}
.stat-card::before{content:'';position:absolute;top:-50%;right:-50%;width:100px;height:100px;background:radial-gradient(circle,rgba(100,80,255,0.03),transparent 70%);pointer-events:none}
.stat-card:hover{border-color:var(--card-bh);transform:translateY(-2px);box-shadow:var(--shadow)}
.stat-card .icon{font-size:18px;margin-bottom:3px;display:block}
.stat-card .number{font-size:18px;font-weight:800;color:var(--t1);line-height:1.2}
.stat-card .number.small{font-size:13px}
.stat-card .label{font-size:9px;color:var(--t3);margin-top:2px;font-weight:500}
.stat-card .sub{font-size:7px;color:var(--t3);margin-top:0px;opacity:.6}
.user-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.user-card{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 14px;transition:all .3s;position:relative;overflow:hidden}
.user-card::before{content:'';position:absolute;top:-50%;right:-50%;width:150px;height:150px;background:radial-gradient(circle,rgba(100,80,255,0.02),transparent 70%);pointer-events:none}
.user-card:hover{border-color:var(--card-bh);transform:translateY(-2px)}
.user-card .head{display:flex;align-items:center;justify-content:space-between;margin-bottom:3px}
.user-card .name{font-size:12px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:4px}
.user-card .status{font-size:8px;font-weight:700;padding:1px 8px;border-radius:8px}
.user-card .status.on{background:var(--green-bg);color:var(--green-t)}
.user-card .status.off{background:var(--red-bg);color:var(--red-t)}
.user-card .uuid{font-family:monospace;font-size:7px;color:var(--t3);margin-bottom:4px;word-break:break-all}
.user-card .info{display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:9px;color:var(--t2);margin-bottom:3px}
.user-card .quota-info{display:flex;justify-content:space-between;font-size:9px;color:var(--t2);margin-bottom:2px}
.user-card .quota-bar{height:3px;border-radius:2px;background:rgba(100,80,255,0.05);overflow:hidden;margin-bottom:6px}
.user-card .quota-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#7C6BFF,#5B4BD9,#A78BFA);transition:width .6s ease}
.user-card .last-seen{font-size:8px;color:var(--t3);margin-bottom:4px}
.user-card .actions{display:flex;gap:3px;flex-wrap:wrap}
.user-card .actions .btn{font-size:8px;padding:3px 6px;border-radius:4px;flex:1;justify-content:center}
.user-card .lock-badge{font-size:7px;color:var(--amber-t);background:var(--amber-bg);padding:0px 5px;border-radius:4px}
.btn{font-family:inherit;font-size:10px;font-weight:600;border-radius:6px;padding:5px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;border:none;transition:all .2s;white-space:nowrap}
.btn i{font-size:11px}
.btn-p{background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);background-size:200% 200%;animation:btnGradient 4s ease infinite;color:#fff;box-shadow:0 3px 15px rgba(100,80,255,.2)}
@keyframes btnGradient{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.btn-p:hover{transform:translateY(-1px);box-shadow:0 6px 25px rgba(100,80,255,.3)}
.btn-o{background:rgba(255,255,255,0.02);border:1px solid var(--card-b);color:var(--t2)}
.btn-o:hover{background:rgba(100,80,255,0.05)}
.btn-d{background:var(--red-bg);color:var(--red-t);border:1px solid rgba(239,68,68,.1)}
.btn-d:hover{background:rgba(239,68,68,.15)}
.btn-pur{background:rgba(100,80,255,0.08);color:var(--accent);border:1px solid rgba(100,80,255,.1)}
.btn-pur:hover{background:rgba(100,80,255,0.15)}
.btn-amber{background:var(--amber-bg);color:var(--amber-t);border:1px solid rgba(245,158,11,0.1)}
.btn-amber:hover{background:rgba(245,158,11,0.15)}
.btn-sm{padding:2px 6px;font-size:8px;border-radius:4px}
.btn-icon{width:22px;height:22px;padding:0;justify-content:center}
.modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:500;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
.modal-bg.open{display:flex}
.modal{background:var(--card);backdrop-filter:blur(30px);border:1px solid var(--card-b);border-radius:14px;padding:20px 18px;max-width:440px;width:calc(100% - 20px);max-height:90vh;overflow-y:auto;position:relative;animation:pageIn .3s ease;box-shadow:var(--shadow)}
.modal-close{position:absolute;top:10px;left:10px;background:rgba(100,80,255,0.05);border:1px solid var(--card-b);color:var(--t2);width:24px;height:24px;border-radius:6px;font-size:12px;display:flex;align-items:center;justify-content:center;cursor:pointer;border:none;transition:.2s}
.modal-close:hover{background:var(--red-bg);color:var(--red-t)}
.modal-title{font-size:14px;font-weight:700;color:var(--t1);margin-bottom:12px;display:flex;align-items:center;gap:6px}
.modal-title i{color:var(--accent);font-size:15px}
.fg{display:flex;flex-direction:column;gap:2px;margin-bottom:8px}
.fg label{font-size:8px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.04em;display:flex;align-items:center;gap:3px}
.fi{width:100%;padding:6px 10px;border-radius:6px;border:1px solid var(--card-b);background:rgba(0,0,20,.2);color:var(--t1);font-family:inherit;font-size:10px;outline:none;transition:.2s}
.fi:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.06)}
.fi::placeholder{color:var(--t3)}
select.fi{appearance:none;cursor:pointer}
.fg-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
.conn-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.conn-card{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:10px;padding:10px 12px;transition:.2s}
.conn-card:hover{border-color:var(--card-bh)}
.conn-card .ip{font-family:monospace;font-size:11px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:4px}
.conn-card .label{font-size:8px;color:var(--t3);margin-top:1px}
.conn-card .conn-info{display:flex;justify-content:space-between;margin-top:4px;font-size:8px;color:var(--t2);gap:3px;flex-wrap:wrap}
.conn-status-dot{display:inline-block;width:5px;height:5px;border-radius:50%;background:#34D399;animation:pulse 1.5s infinite;margin-left:3px}
.settings-card{background:var(--card);backdrop-filter:blur(20px);border:1px solid var(--card-b);border-radius:var(--radius);padding:14px 16px;max-width:480px;margin-bottom:10px;position:relative;overflow:hidden}
.settings-card::before{content:'';position:absolute;top:-50%;right:-50%;width:150px;height:150px;background:radial-gradient(circle,rgba(100,80,255,0.02),transparent 70%);pointer-events:none}
.settings-card .title{font-size:13px;font-weight:700;color:var(--t1);margin-bottom:10px;display:flex;align-items:center;gap:6px}
.settings-card .title i{color:var(--accent)}
.settings-card .field{margin-bottom:8px}
.settings-card .field label{font-size:9px;color:var(--t3);display:block;margin-bottom:2px;font-weight:600}
.settings-card .field input{width:100%;padding:6px 10px;border-radius:6px;border:1px solid var(--card-b);background:rgba(0,0,20,.2);color:var(--t1);font-family:inherit;font-size:11px;outline:none;transition:.2s}
.settings-card .field input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(100,80,255,.06)}
.settings-card .btn{width:100%;justify-content:center;margin-top:3px;font-size:11px;padding:6px}
.settings-card .toggle-row{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--card-b)}
.settings-card .toggle-row .toggle-label{font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px}
.switch{position:relative;width:36px;height:20px;background:var(--t3);border-radius:10px;cursor:pointer;transition:.3s;flex-shrink:0}
.switch.on{background:linear-gradient(135deg,#7C6BFF,#5B4BD9)}
.switch .slider{position:absolute;top:2px;right:2px;width:16px;height:16px;background:#fff;border-radius:50%;transition:.3s;box-shadow:0 2px 4px rgba(0,0,0,0.2)}
.switch.on .slider{right:18px}
.toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(50px);background:var(--card);backdrop-filter:blur(30px);border:1px solid var(--card-b);color:var(--t1);border-radius:8px;padding:8px 16px;font-size:11px;opacity:0;transition:all .3s;z-index:999;pointer-events:none;box-shadow:var(--shadow);display:flex;align-items:center;gap:5px}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.toast.ok{border-color:rgba(16,185,129,.2);background:var(--green-bg);color:var(--green-t)}
.toast.err{border-color:rgba(239,68,68,.2);background:var(--red-bg);color:var(--red-t)}
.empty{text-align:center;padding:30px 15px;color:var(--t3)}
.empty i{font-size:28px;opacity:.3;display:block;margin-bottom:6px}
.empty p{font-size:10px}
.bottom-nav{display:none;position:fixed;bottom:0;right:0;left:0;background:var(--card);backdrop-filter:blur(30px);border-top:1px solid var(--card-b);z-index:300;padding:4px 2px 6px;justify-content:space-around;align-items:center}
.bottom-nav .nav-item{display:flex;flex-direction:column;align-items:center;gap:1px;color:var(--t3);font-size:7px;cursor:pointer;padding:3px 6px;border-radius:6px;transition:all .2s;border:none;background:none;font-family:inherit;min-width:40px;position:relative}
.bottom-nav .nav-item i{font-size:16px;transition:all .2s}
.bottom-nav .nav-item:hover{color:var(--t2)}
.bottom-nav .nav-item.active{color:var(--accent)}
.bottom-nav .nav-item.active i{transform:scale(1.1)}
@media(max-width:768px){
  .bottom-nav{display:flex !important}
  .main{padding-bottom:65px !important;margin-right:0 !important;padding-top:55px !important}
  .sidebar{transform:translateX(100%);padding-bottom:60px}
  .sidebar.open{transform:translateX(0)}
  .mob-top{display:flex}
  .stats-grid{grid-template-columns:repeat(3,1fr)}
  .user-grid{grid-template-columns:1fr}
}
@media(max-width:480px){
  .stats-grid{grid-template-columns:1fr 1fr}
  .main{padding:50px 8px 65px}
  .bottom-nav .nav-item{min-width:32px;padding:2px 4px}
  .bottom-nav .nav-item i{font-size:14px}
  .bottom-nav .nav-item span{font-size:6px}
}
@media(min-width:769px){.bottom-nav{display:none !important}}
</style>
</head>
<body>
<div class="stars-bg">
    <div class="star-bg" style="width:2px;height:2px;top:5%;left:10%;animation-delay:0s"></div>
    <div class="star-bg" style="width:3px;height:3px;top:15%;left:30%;animation-delay:1.5s"></div>
    <div class="star-bg" style="width:1px;height:1px;top:25%;left:50%;animation-delay:0.8s"></div>
    <div class="star-bg" style="width:2px;height:2px;top:40%;left:70%;animation-delay:2.2s"></div>
    <div class="star-bg" style="width:3px;height:3px;top:55%;left:15%;animation-delay:0.5s"></div>
    <div class="star-bg" style="width:1px;height:1px;top:70%;left:85%;animation-delay:1.8s"></div>
    <div class="star-bg" style="width:2px;height:2px;top:85%;left:40%;animation-delay:2.5s"></div>
</div>
<div class="glow-main glow-left"></div><div class="glow-main glow-right"></div>
<div class="toast" id="toast"></div>

<!-- ===== مودال ساخت کاربر با فینگرپرینت ===== -->
<div class="modal-bg" id="modal-user">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('modal-user')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-user-plus"></i> 🪐 ساخت کاربر جدید</div>
    
    <div class="fg"><label><i class="ti ti-tag"></i> نام کاربری</label><input class="fi" id="user-label" placeholder="مثلاً: کاربر علی"></div>
    
    <div class="fg-grid">
      <div class="fg"><label><i class="ti ti-database"></i> حجم (GB)</label><input class="fi" id="user-quota" type="number" min="0.5" step="0.5" value="2"></div>
      <div class="fg"><label><i class="ti ti-calendar"></i> انقضا (روز)</label><input class="fi" id="user-exp" type="number" min="0" value="30"></div>
      <div class="fg"><label><i class="ti ti-devices"></i> دستگاه</label><input class="fi" id="user-devices" type="number" min="0" max="10" value="1"></div>
    </div>
    
    <!-- ✅ انتخاب فینگرپرینت با استیکر -->
    <div class="fg">
      <label><i class="ti ti-fingerprint"></i> فینگرپرینت</label>
      <select class="fi" id="user-fingerprint">
        <option value="chrome">🌐 Chrome</option>
        <option value="firefox">🦊 Firefox</option>
        <option value="safari">🧭 Safari</option>
        <option value="edge">🌊 Edge</option>
        <option value="ios">📱 iOS</option>
        <option value="android">🤖 Android</option>
        <option value="safari_ios">🍏 Safari iOS</option>
        <option value="random">🎲 Random</option>
        <option value="none">🚫 None</option>
      </select>
      <div style="font-size:7px;color:var(--t3);margin-top:2px;">💡 فینگرپرینت مناسب دستگاه خود را انتخاب کنید</div>
    </div>
    
    <div class="fg"><label><i class="ti ti-lock"></i> رمز (اختیاری)</label><input class="fi" id="user-password" type="password" placeholder="برای حذف/ویرایش" dir="ltr"></div>
    
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-p" onclick="saveUser()" style="flex:2"><i class="ti ti-check"></i> ساخت</button>
      <button class="btn btn-o" onclick="closeModal('modal-user')" style="flex:1">انصراف</button>
    </div>
  </div>
</div>

<!-- ===== مودال ویرایش با فینگرپرینت ===== -->
<div class="modal-bg" id="modal-edit">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('modal-edit')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-edit"></i> 🪐 ویرایش کاربر</div>
    <input type="hidden" id="edit-uuid">
    
    <div class="fg" id="edit-password-section"><label><i class="ti ti-lock"></i> رمز</label><input class="fi" id="edit-password" type="password" placeholder="رمز کانفیگ" dir="ltr"></div>
    <div class="fg"><label><i class="ti ti-tag"></i> نام</label><input class="fi" id="edit-label" placeholder="نام کاربری"></div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
      <div class="fg"><label><i class="ti ti-database"></i> حجم (GB)</label><input class="fi" id="edit-quota" type="number" min="0" step="0.5"></div>
      <div class="fg"><label><i class="ti ti-calendar"></i> انقضا (روز)</label><input class="fi" id="edit-exp" type="number" min="0"></div>
    </div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
      <div class="fg"><label><i class="ti ti-devices"></i> دستگاه</label><input class="fi" id="edit-devices" type="number" min="0" max="10"></div>
      <div class="fg"><label><i class="ti ti-toggle-left"></i> وضعیت</label><select class="fi" id="edit-status"><option value="true">✅ فعال</option><option value="false">❌ غیرفعال</option></select></div>
    </div>
    
    <!-- ✅ انتخاب فینگرپرینت در ویرایش -->
    <div class="fg">
      <label><i class="ti ti-fingerprint"></i> فینگرپرینت</label>
      <select class="fi" id="edit-fingerprint">
        <option value="chrome">🌐 Chrome</option>
        <option value="firefox">🦊 Firefox</option>
        <option value="safari">🧭 Safari</option>
        <option value="edge">🌊 Edge</option>
        <option value="ios">📱 iOS</option>
        <option value="android">🤖 Android</option>
        <option value="safari_ios">🍏 Safari iOS</option>
        <option value="random">🎲 Random</option>
        <option value="none">🚫 None</option>
      </select>
    </div>
    
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-p" onclick="saveEdit()" style="flex:2"><i class="ti ti-check"></i> ذخیره</button>
      <button class="btn btn-o" onclick="closeModal('modal-edit')" style="flex:1">انصراف</button>
    </div>
  </div>
</div>

<div class="modal-bg" id="modal-delete">
  <div class="modal" style="max-width:340px">
    <button class="modal-close" onclick="closeModal('modal-delete')"><i class="ti ti-x"></i></button>
    <div class="modal-title"><i class="ti ti-trash"></i> حذف کاربر</div>
    <input type="hidden" id="delete-uuid">
    <p style="font-size:10px;color:var(--t2);margin-bottom:10px">برای حذف، رمز کانفیگ را وارد کنید.</p>
    <div class="fg"><label><i class="ti ti-lock"></i> رمز</label><input class="fi" id="delete-password" type="password" placeholder="رمز کانفیگ" dir="ltr"></div>
    <div style="display:flex;gap:6px;margin-top:10px">
      <button class="btn btn-d" onclick="confirmDelete()" style="flex:2"><i class="ti ti-trash"></i> حذف</button>
      <button class="btn btn-o" onclick="closeModal('modal-delete')" style="flex:1">انصراف</button>
    </div>
  </div>
</div>

<!-- ===== هدر موبایل ===== -->
<div class="mob-top">
  <div class="ml"><div class="mob-logo">🪐</div><span class="mob-title">پنل عقاب</span></div>
  <button class="menu-btn" id="open-sb"><i class="ti ti-menu-2"></i></button>
</div>
<div class="overlay" id="overlay"></div>

<!-- ===== سایدبار ===== -->
<aside class="sidebar" id="sb">
  <div class="logo"><div class="logo-icon">🪐</div><div><div class="logo-name">پنل عقاب</div><div class="logo-sub">مدیریت کاربران</div></div></div>
  <div class="nav-wrap">
    <div class="nav-it on" data-pg="dashboard"><i class="ti ti-layout-dashboard"></i> خانه</div>
    <div class="nav-it" data-pg="users"><i class="ti ti-users"></i> کاربران</div>
    <div class="nav-it" data-pg="inbound"><i class="ti ti-plug"></i> اینباند</div>
    <div class="nav-it" data-pg="connections"><i class="ti ti-plug-connected"></i> اتصالات</div>
    <div class="nav-it" data-pg="settings"><i class="ti ti-settings"></i> تنظیمات</div>
    <div class="nav-it" data-pg="logs"><i class="ti ti-notes"></i> لاگ‌ها</div>
    <div class="nav-it" data-pg="backup"><i class="ti ti-database"></i> بکاپ</div>
  </div>
  <div class="sb-foot">
    <button class="logout-btn" onclick="logout()"><i class="ti ti-logout"></i> خروج</button>
  </div>
</aside>

<!-- ===== منوی پایین ===== -->
<div class="bottom-nav" id="bottomNav">
  <button class="nav-item active" data-pg="dashboard" onclick="navTo('dashboard')"><i class="ti ti-layout-dashboard"></i><span>خانه</span></button>
  <button class="nav-item" data-pg="users" onclick="navTo('users')"><i class="ti ti-users"></i><span>کاربران</span></button>
  <button class="nav-item" data-pg="inbound" onclick="navTo('inbound')"><i class="ti ti-plug"></i><span>اینباند</span></button>
  <button class="nav-item" data-pg="settings" onclick="navTo('settings')"><i class="ti ti-settings"></i><span>تنظیمات</span></button>
</div>

<!-- ===== محتوای اصلی ===== -->
<main class="main">

<!-- ===== خانه ===== -->
<section class="pg on" id="pg-dashboard">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-layout-dashboard"></i> خانه</div><div class="tb-sub" id="last-update">بروزرسانی: لحظه‌ای</div></div>
    <div class="tb-right">
      <span class="badge bg-fire" id="online-badge"><span class="dot dg"></span> ۰ آنلاین</span>
      <button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-plus"></i> کاربر</button>
    </div>
  </div>
  <div class="stats-grid">
    <div class="stat-card"><span class="icon">📊</span><div class="number" id="stat-traffic">۰</div><div class="label">ترافیک</div><div class="sub">MB</div></div>
    <div class="stat-card"><span class="icon">📨</span><div class="number" id="stat-requests">۰</div><div class="label">درخواست‌ها</div><div class="sub">تعداد</div></div>
    <div class="stat-card"><span class="icon">⏱️</span><div class="number" id="stat-uptime">۰۰:۰۰:۰۰</div><div class="label">آپتایم</div><div class="sub">زمان</div></div>
    <div class="stat-card"><span class="icon">💾</span><div class="number small" id="stat-disk">۰ GB</div><div class="label">فضای دیسک</div><div class="sub" id="stat-disk-used">استفاده</div></div>
    <div class="stat-card"><span class="icon">📶</span><div class="number small" id="stat-speed">۰ B/s</div><div class="label">سرعت</div><div class="sub">لحظه‌ای</div></div>
    <div class="stat-card"><span class="icon">👥</span><div class="number" id="stat-users">۰</div><div class="label">کاربران</div><div class="sub" id="stat-users-active">۰ فعال</div></div>
  </div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:10px 12px;margin-top:4px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <span style="font-size:11px;font-weight:700;color:var(--t1)">🆕 کاربران اخیر</span>
      <button class="btn btn-sm btn-o" onclick="loadDashboard()"><i class="ti ti-refresh"></i></button>
    </div>
    <div id="recent-users" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:4px"></div>
  </div>
</section>

<!-- ===== کاربران ===== -->
<section class="pg" id="pg-users">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-users"></i> کاربران</div><div class="tb-sub" id="users-count">۰ کاربر</div></div>
    <div class="tb-right"><button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-plus"></i> جدید</button></div>
  </div>
  <div id="users-grid" class="user-grid"><div class="empty"><i class="ti ti-users"></i><p>هیچ کاربری وجود ندارد</p></div></div>
</section>

<!-- ===== اینباند ===== -->
<section class="pg" id="pg-inbound">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-plug"></i> اینباند</div><div class="tb-sub">تنظیمات ورودی</div></div></div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:12px 14px;margin-bottom:10px">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:var(--t1)" id="inbound-port">۴۴۳</div><div style="font-size:8px;color:var(--t3)">پورت</div></div>
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:var(--t1)" id="inbound-protocol">VLESS</div><div style="font-size:8px;color:var(--t3)">پروتکل</div></div>
      <div style="text-align:center"><div style="font-size:12px;font-weight:700;color:var(--t1)" id="inbound-host">—</div><div style="font-size:8px;color:var(--t3)">هاست</div></div>
      <div style="text-align:center"><div style="font-size:14px;font-weight:700;color:#34D399">✅ فعال</div><div style="font-size:8px;color:var(--t3)">وضعیت</div></div>
    </div>
    <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
      <button class="btn btn-p btn-sm" onclick="openModal('modal-user')"><i class="ti ti-user-plus"></i> کاربر</button>
      <button class="btn btn-o btn-sm" onclick="openModal('modal-inbound')"><i class="ti ti-settings"></i> تنظیمات</button>
    </div>
  </div>
</section>

<!-- ===== اتصالات ===== -->
<section class="pg" id="pg-connections">
  <div class="topbar"><div><div class="tb-title">🔌 اتصالات</div><div class="tb-sub" id="conn-count">۰ اتصال</div></div>
    <div class="tb-right"><span class="badge bg-green"><span class="dot dg pulse"></span> فعال</span><button class="btn btn-sm btn-o" onclick="loadConnections()"><i class="ti ti-refresh"></i></button></div>
  </div>
  <div id="conns-grid" class="conn-grid"><div class="empty"><i class="ti ti-plug-off"></i><p>هیچ اتصالی وجود ندارد</p></div></div>
</section>

<!-- ===== تنظیمات ===== -->
<section class="pg" id="pg-settings">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-settings"></i> تنظیمات</div><div class="tb-sub">مدیریت پنل</div></div></div>
  
  <div class="settings-card">
    <div class="title"><i class="ti ti-language"></i> زبان پنل</div>
    <div style="display:flex;gap:6px;margin-top:4px">
      <button class="btn btn-pur" onclick="setLang('fa')" style="flex:1;font-size:11px;padding:6px 12px" id="lang-fa-btn">🇮🇷 فارسی</button>
      <button class="btn btn-o" onclick="setLang('en')" style="flex:1;font-size:11px;padding:6px 12px" id="lang-en-btn">🇬🇧 English</button>
    </div>
    <div style="font-size:9px;color:var(--t3);margin-top:6px">💡 زبان فعلی: <span id="current-lang-label">فارسی</span></div>
  </div>
  
  <div class="settings-card">
    <div class="title"><i class="ti ti-key"></i> تغییر رمز</div>
    <div class="field"><label>رمز فعلی</label><input class="fi" id="old-password" type="password" placeholder="رمز فعلی" dir="ltr"></div>
    <div class="field"><label>رمز جدید</label><input class="fi" id="new-password" type="password" placeholder="حداقل ۴ کاراکتر" dir="ltr"></div>
    <div class="field"><label>تکرار</label><input class="fi" id="confirm-password" type="password" placeholder="تکرار" dir="ltr"></div>
    <button class="btn btn-p" onclick="changePassword()"><i class="ti ti-key"></i> تغییر</button>
    <div id="password-result" style="margin-top:8px;display:none;font-size:11px;"></div>
  </div>
  
  <div class="settings-card">
    <div class="title"><i class="ti ti-plug"></i> پورت اینباند</div>
    <div class="field"><label>پورت</label><input class="fi" id="inbound-port-setting" type="number" min="1" max="65535" value="443"></div>
    <button class="btn btn-p" onclick="updateInbound()"><i class="ti ti-check"></i> ذخیره</button>
  </div>
  
  <div class="settings-card">
    <div class="title"><i class="ti ti-color-swatch"></i> تم RGB</div>
    <div class="toggle-row">
      <div class="toggle-label"><i class="ti ti-color-palette" style="background:linear-gradient(135deg,#ff0000,#00ff00,#0000ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent"></i> RGB</div>
      <div class="switch" id="rgb-switch" onclick="toggleRGB()"><div class="slider"></div></div>
    </div>
  </div>
</section>

<!-- ===== لاگ‌ها ===== -->
<section class="pg" id="pg-logs">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-notes"></i> لاگ‌ها</div><div class="tb-sub" id="logs-count">۰ لاگ</div></div>
    <div class="tb-right"><button class="btn btn-sm btn-o" onclick="loadLogs()"><i class="ti ti-refresh"></i></button></div>
  </div>
  <div style="background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:8px 10px;max-height:400px;overflow-y:auto">
    <div id="logs-container" style="font-family:monospace;font-size:9px;color:var(--t2);direction:ltr;text-align:left;line-height:1.5"></div>
  </div>
</section>

<!-- ===== بکاپ ===== -->
<section class="pg" id="pg-backup">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-database"></i> بکاپ</div><div class="tb-sub">ذخیره و بازیابی</div></div></div>
  <div class="settings-card">
    <div class="title"><i class="ti ti-download"></i> بکاپ‌گیری</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      <button class="btn btn-p btn-sm" onclick="createBackup()" style="flex:2"><i class="ti ti-download"></i> دانلود</button>
      <button class="btn btn-o btn-sm" onclick="document.getElementById('restore-input').click()" style="flex:1"><i class="ti ti-upload"></i> بازیابی</button>
      <input type="file" id="restore-input" accept=".json" style="display:none" onchange="restoreBackup(event)">
    </div>
  </div>
</section>

</main>

<script>
// ===== توابع کمکی =====
function toast(msg, type='') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (type ? ' ' + type : '');
  setTimeout(() => t.classList.remove('show'), 2500);
}

function fmtB(b) {
  if (!b || b === 0) return '0 B';
  if (b < 1024) return b + ' B';
  if (b < 1024**2) return (b/1024).toFixed(1) + ' KB';
  if (b < 1024**3) return (b/1024**2).toFixed(1) + ' MB';
  if (b < 1024**4) return (b/1024**3).toFixed(2) + ' GB';
  return (b/1024**4).toFixed(2) + ' TB';
}

function esc(s) {
  return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// ===== زبان =====
let currentLang = localStorage.getItem('eagle-lang') || 'fa';

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('eagle-lang', lang);
    document.getElementById('lang-fa-btn').className = 'btn ' + (lang === 'fa' ? 'btn-pur' : 'btn-o');
    document.getElementById('lang-en-btn').className = 'btn ' + (lang === 'en' ? 'btn-pur' : 'btn-o');
    document.getElementById('current-lang-label').textContent = lang === 'fa' ? 'فارسی' : 'English';
    
    fetch('/api/settings/language', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({language: lang})
    }).catch(() => {});
    
    if (lang === 'en') {
        document.querySelector('.tb-title:first-child').innerHTML = '<i class="ti ti-layout-dashboard"></i> Home';
        document.querySelector('#pg-users .tb-title').innerHTML = '<i class="ti ti-users"></i> Users';
        document.querySelector('#pg-inbound .tb-title').innerHTML = '<i class="ti ti-plug"></i> Inbound';
        document.querySelector('#pg-connections .tb-title').innerHTML = '🔌 Connections';
        document.querySelector('#pg-settings .tb-title').innerHTML = '<i class="ti ti-settings"></i> Settings';
        document.querySelector('#pg-logs .tb-title').innerHTML = '<i class="ti ti-notes"></i> Logs';
        document.querySelector('#pg-backup .tb-title').innerHTML = '<i class="ti ti-database"></i> Backup';
        document.querySelector('#pg-settings .settings-card:first-child .title').innerHTML = '<i class="ti ti-language"></i> Panel Language';
    } else {
        document.querySelector('.tb-title:first-child').innerHTML = '<i class="ti ti-layout-dashboard"></i> خانه';
        document.querySelector('#pg-users .tb-title').innerHTML = '<i class="ti ti-users"></i> کاربران';
        document.querySelector('#pg-inbound .tb-title').innerHTML = '<i class="ti ti-plug"></i> اینباند';
        document.querySelector('#pg-connections .tb-title').innerHTML = '🔌 اتصالات';
        document.querySelector('#pg-settings .tb-title').innerHTML = '<i class="ti ti-settings"></i> تنظیمات';
        document.querySelector('#pg-logs .tb-title').innerHTML = '<i class="ti ti-notes"></i> لاگ‌ها';
        document.querySelector('#pg-backup .tb-title').innerHTML = '<i class="ti ti-database"></i> بکاپ';
        document.querySelector('#pg-settings .settings-card:first-child .title').innerHTML = '<i class="ti ti-language"></i> زبان پنل';
    }
}

// ===== احراز هویت =====
async function authF(url, opts={}) {
  const r = await fetch(url, opts);
  if (r.status === 401) { location.href = '/login'; throw new Error('unauthorized'); }
  return r;
}

async function logout() {
  try { await fetch('/api/logout', {method:'POST'}); } catch(e) {}
  location.href = '/login';
}

// ===== ناوبری =====
function navTo(name) {
  document.querySelectorAll('.nav-it').forEach(n => n.classList.toggle('on', n.dataset.pg === name));
  document.querySelectorAll('.pg').forEach(p => p.classList.toggle('on', p.id === 'pg-' + name));
  document.querySelectorAll('.bottom-nav .nav-item').forEach(n => n.classList.toggle('active', n.dataset.pg === name));
  closeSb();
  const loaders = {
    dashboard: loadDashboard,
    users: loadUsers,
    inbound: loadInbound,
    connections: loadConnections,
    logs: loadLogs,
    settings: () => {}
  };
  if (loaders[name]) loaders[name]();
}

document.querySelectorAll('.nav-it, .bottom-nav .nav-item').forEach(el => {
  el.addEventListener('click', () => navTo(el.dataset.pg));
});

const sb = document.getElementById('sb'), overlay = document.getElementById('overlay');
function openSb(){ sb.classList.add('open'); overlay.classList.add('show'); }
function closeSb(){ sb.classList.remove('open'); overlay.classList.remove('show'); }
document.getElementById('open-sb').addEventListener('click', openSb);
overlay.addEventListener('click', closeSb);

// ===== داشبورد =====
async function loadDashboard() {
  try {
    const r = await authF('/api/dashboard/stats');
    const data = await r.json();
    document.getElementById('stat-traffic').textContent = (data.traffic.total / (1024*1024)).toFixed(1);
    document.getElementById('stat-requests').textContent = data.requests || 0;
    document.getElementById('stat-uptime').textContent = data.uptime || '00:00:00';
    document.getElementById('stat-disk').textContent = data.disk.total_fmt || '0 GB';
    document.getElementById('stat-disk-used').textContent = 'استفاده: ' + (data.disk.used_fmt || '0');
    document.getElementById('stat-speed').textContent = data.speed.download_fmt || '0 B/s';
    document.getElementById('stat-users').textContent = data.links_count || 0;
    document.getElementById('stat-users-active').textContent = (data.active_links || 0) + ' فعال';
    document.getElementById('online-badge').innerHTML = '<span class="dot dg"></span> ' + (data.connections || 0) + ' آنلاین';
    document.getElementById('last-update').textContent = 'بروزرسانی: ' + new Date().toLocaleTimeString('fa-IR');
    
    const usersR = await authF('/api/links');
    const usersData = await usersR.json();
    const links = usersData.links || [];
    const recent = links.slice(0, 4);
    const grid = document.getElementById('recent-users');
    if (!recent.length) {
      grid.innerHTML = '<div class="empty" style="padding:10px"><i class="ti ti-users"></i><p style="font-size:9px">هیچ کاربری وجود ندارد</p></div>';
    } else {
      grid.innerHTML = recent.map(l => `
        <div style="background:rgba(100,80,255,0.02);border-radius:4px;padding:4px 6px;display:flex;justify-content:space-between;align-items:center">
          <div><div style="font-size:9px;font-weight:600;color:var(--t1)">${esc(l.label)}</div><div style="font-size:7px;color:var(--t3)">${l.active ? '🟢' : '🔴'}</div></div>
          <div style="font-size:8px;color:var(--t2)">${fmtB(l.used_bytes || 0)}</div>
        </div>
      `).join('');
    }
  } catch(e) { console.error(e); }
}

// ===== اینباند =====
async function loadInbound() {
  try {
    const r = await authF('/api/inbound');
    const data = await r.json();
    document.getElementById('inbound-port').textContent = data.port || 443;
    document.getElementById('inbound-protocol').textContent = (data.protocol || 'vless').toUpperCase();
    document.getElementById('inbound-host').textContent = data.host || '—';
    document.getElementById('inbound-port-setting').value = data.port || 443;
    loadUsers();
  } catch(e) { console.error(e); }
}

async function updateInbound() {
  const port = parseInt(document.getElementById('inbound-port-setting').value) || 443;
  try {
    const r = await authF('/api/inbound', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port: port })
    });
    if (!r.ok) { toast('❌ خطا', 'err'); return; }
    toast('✅ ذخیره شد', 'ok');
    loadInbound();
  } catch(e) { toast('❌ خطا', 'err'); }
}

// ===== کاربران با نمایش فینگرپرینت =====
async function loadUsers() {
  try {
    const r = await authF('/api/links');
    const { links=[] } = await r.json();
    const grid = document.getElementById('users-grid');
    document.getElementById('users-count').textContent = links.length + ' کاربر';
    
    if (!links.length) {
      grid.innerHTML = '<div class="empty"><i class="ti ti-users"></i><p>هیچ کاربری وجود ندارد</p></div>';
      return;
    }
    
    // ✅ مپ فینگرپرینت به استیکر
    const fpEmoji = {
      chrome: '🌐',
      firefox: '🦊',
      safari: '🧭',
      edge: '🌊',
      ios: '📱',
      android: '🤖',
      safari_ios: '🍏',
      random: '🎲',
      none: '🚫'
    };
    
    grid.innerHTML = links.map(l => {
      const pct = l.limit_bytes === 0 ? 0 : Math.min(100, (l.used_bytes / l.limit_bytes) * 100);
      const active = l.active && !l.expired;
      const statusClass = active ? 'on' : 'off';
      const statusText = active ? '🟢' : '🔴';
      const lastSeen = l.last_connected_at ? new Date(l.last_connected_at).toLocaleString('fa-IR') : '—';
      const fp = l.fingerprint || 'chrome';
      const fpEmojiChar = fpEmoji[fp] || '🌐';
      const fpNames = {
        chrome: 'Chrome', firefox: 'Firefox', safari: 'Safari',
        edge: 'Edge', ios: 'iOS', android: 'Android',
        safari_ios: 'Safari iOS', random: 'Random', none: 'None'
      };
      const fpName = fpNames[fp] || fp.charAt(0).toUpperCase() + fp.slice(1);
      
      return `<div class="user-card">
        <div class="head">
          <div class="name">🪐 ${esc(l.label)} ${l.has_password ? '<span class="lock-badge">🔒</span>' : ''}</div>
          <span class="status ${statusClass}">${statusText}</span>
        </div>
        <div class="uuid">🔑 ${esc(l.uuid)}</div>
        <div class="info">
          <span>📊 ${fmtB(l.used_bytes || 0)}</span>
          <span>📦 ${l.limit_bytes === 0 ? '∞' : fmtB(l.limit_bytes)}</span>
          <span>📱 ${l.max_devices || '∞'}</span>
          <span>${l.expired ? '⛔' : '✅'}</span>
        </div>
        <!-- ✅ نمایش فینگرپرینت با استیکر -->
        <div style="font-size:8px;color:var(--t3);margin-bottom:3px;">
          🖥️ فینگرپرینت: <span style="color:var(--accent);font-weight:600;">${fpEmojiChar} ${fpName}</span>
        </div>
        <div class="last-seen"><i class="ti ti-clock"></i> ${lastSeen}</div>
        <div class="quota-info"><span>مصرف</span><span>${pct.toFixed(0)}%</span></div>
        <div class="quota-bar"><div class="quota-fill" style="width:${pct}%"></div></div>
        <div class="actions">
          <button class="btn btn-o btn-sm" onclick="navigator.clipboard.writeText('${esc(l.vless_link)}').then(()=>toast('✅ کپی شد','ok'))"><i class="ti ti-copy"></i></button>
          <button class="btn btn-pur btn-sm" onclick="navigator.clipboard.writeText('${esc(l.sub_url)}').then(()=>toast('✅ کپی شد','ok'))"><i class="ti ti-link"></i></button>
          <button class="btn btn-amber btn-sm" onclick="resetUsage('${l.uuid}')"><i class="ti ti-rotate"></i></button>
          <button class="btn btn-pur btn-sm btn-icon" onclick="openEditModal('${l.uuid}')"><i class="ti ti-edit"></i></button>
          <button class="btn btn-d btn-sm btn-icon" onclick="openDeleteModal('${l.uuid}')"><i class="ti ti-trash"></i></button>
        </div>
      </div>`;
    }).join('');
  } catch(e) {
    console.error(e);
  }
}

// ===== ساخت کاربر با فینگرپرینت =====
async function saveUser() {
  const label = document.getElementById('user-label').value.trim() || 'کاربر';
  const quota = parseFloat(document.getElementById('user-quota').value) || 0;
  const exp = parseInt(document.getElementById('user-exp').value) || 30;
  const devices = parseInt(document.getElementById('user-devices').value) || 0;
  const password = document.getElementById('user-password').value.trim();
  const fingerprint = document.getElementById('user-fingerprint').value || 'chrome';
  
  try {
    const r = await authF('/api/links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        label,
        limit_value: quota,
        limit_unit: 'GB',
        expires_days: exp,
        max_devices: devices,
        password,
        fingerprint: fingerprint,
        protocol: 'vless-ws',
        port: 443
      })
    });
    if (!r.ok) throw new Error();
    
    document.getElementById('user-label').value = '';
    document.getElementById('user-quota').value = '2';
    document.getElementById('user-exp').value = '30';
    document.getElementById('user-devices').value = '1';
    document.getElementById('user-password').value = '';
    document.getElementById('user-fingerprint').value = 'chrome';
    
    closeModal('modal-user');
    toast('✅ کاربر ساخته شد', 'ok');
    loadUsers(); loadDashboard();
  } catch(e) {
    toast('❌ خطا', 'err');
  }
}

// ===== ویرایش کاربر با فینگرپرینت =====
async function openEditModal(uuid) {
  try {
    const r = await authF('/api/links');
    const { links=[] } = await r.json();
    const link = links.find(l => l.uuid === uuid);
    if (!link) { toast('کاربر یافت نشد', 'err'); return; }
    
    document.getElementById('edit-uuid').value = uuid;
    document.getElementById('edit-label').value = link.label || '';
    document.getElementById('edit-password').value = '';
    document.getElementById('edit-quota').value = link.limit_bytes === 0 ? '' : (link.limit_bytes / (1024**3)).toFixed(1);
    document.getElementById('edit-exp').value = link.expires_at ? Math.ceil((new Date(link.expires_at) - new Date()) / (1000*60*60*24)) : '';
    document.getElementById('edit-devices').value = link.max_devices || 0;
    document.getElementById('edit-status').value = link.active ? 'true' : 'false';
    document.getElementById('edit-fingerprint').value = link.fingerprint || 'chrome';
    document.getElementById('edit-password-section').style.display = link.has_password ? 'block' : 'none';
    
    openModal('modal-edit');
  } catch(e) {
    toast('خطا', 'err');
  }
}

async function saveEdit() {
  const uuid = document.getElementById('edit-uuid').value;
  const password = document.getElementById('edit-password').value.trim();
  const label = document.getElementById('edit-label').value.trim() || 'کاربر';
  const quota = parseFloat(document.getElementById('edit-quota').value) || 0;
  const exp = parseInt(document.getElementById('edit-exp').value) || 0;
  const devices = parseInt(document.getElementById('edit-devices').value) || 0;
  const active = document.getElementById('edit-status').value === 'true';
  const fingerprint = document.getElementById('edit-fingerprint').value || 'chrome';
  
  try {
    const r = await authF('/api/links/' + uuid, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        label,
        limit_value: quota,
        limit_unit: 'GB',
        expires_days: exp,
        max_devices: devices,
        active,
        password,
        fingerprint
      })
    });
    if (!r.ok) {
      if (r.status === 403) { toast('❌ رمز اشتباه', 'err'); return; }
      throw new Error();
    }
    closeModal('modal-edit');
    toast('✅ ویرایش شد', 'ok');
    loadUsers();
  } catch(e) {
    toast('❌ خطا', 'err');
  }
}

// ===== حذف =====
function openDeleteModal(uuid) {
  document.getElementById('delete-uuid').value = uuid;
  document.getElementById('delete-password').value = '';
  openModal('modal-delete');
}

async function confirmDelete() {
  const uuid = document.getElementById('delete-uuid').value;
  const password = document.getElementById('delete-password').value.trim();
  try {
    const r = await authF('/api/links/' + uuid, {
      method: 'DELETE', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });
    if (!r.ok) { if (r.status === 403) { toast('❌ رمز اشتباه', 'err'); return; } throw new Error(); }
    closeModal('modal-delete');
    toast('✅ حذف شد', 'ok');
    loadUsers(); loadDashboard();
  } catch(e) { toast('❌ خطا', 'err'); }
}

async function resetUsage(uuid) {
  if (!confirm('ریست مصرف؟')) return;
  try {
    const r = await authF('/api/links/' + uuid, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reset_usage: true })
    });
    if (!r.ok) throw new Error();
    toast('✅ ریست شد', 'ok');
    loadUsers();
  } catch(e) { toast('❌ خطا', 'err'); }
}

// ===== اتصالات =====
async function loadConnections() {
  try {
    const r = await authF('/api/connections');
    const d = await r.json();
    const grid = document.getElementById('conns-grid');
    const count = d.count || 0;
    document.getElementById('conn-count').textContent = count + ' اتصال';
    if (!count) { grid.innerHTML = '<div class="empty"><i class="ti ti-plug-off"></i><p>هیچ اتصالی وجود ندارد</p></div>'; return; }
    grid.innerHTML = d.connections.map(c => {
      const secs = c.connected_at ? Math.max(0, Math.floor((Date.now() - new Date(c.connected_at).getTime()) / 1000)) : 0;
      const dur = secs < 60 ? secs + 'ث' : secs < 3600 ? Math.floor(secs/60) + 'د' : Math.floor(secs/3600) + 'س';
      return `<div class="conn-card"><div class="ip"><span class="conn-status-dot"></span> ${esc(c.ip)}</div><div class="label">${esc(c.label || 'نامشخص')}</div><div class="conn-info"><span>📥 ${esc(c.bytes_fmt || '0 B')}</span><span>⏱ ${dur}</span></div></div>`;
    }).join('');
  } catch(e) { console.error(e); }
}

// ===== لاگ‌ها =====
async function loadLogs() {
  try {
    const r = await authF('/api/activity');
    const data = await r.json();
    const logs = data.logs || [];
    document.getElementById('logs-count').textContent = logs.length + ' لاگ';
    const container = document.getElementById('logs-container');
    if (!logs.length) { container.innerHTML = '<div class="empty"><i class="ti ti-notes"></i><p>هیچ لاگی وجود ندارد</p></div>'; return; }
    container.innerHTML = logs.map(log => {
      const time = log.time ? new Date(log.time).toLocaleString('fa-IR') : '—';
      const color = log.level === 'err' ? '#F87171' : log.level === 'warn' ? '#FCD34D' : '#A78BFA';
      return `<div style="padding:3px 0;border-bottom:1px solid rgba(100,80,255,0.02);display:flex;gap:6px"><span style="color:${color};font-weight:700">[${(log.level || 'info').toUpperCase()}]</span><span style="color:var(--t3)">${time}</span><span>${esc(log.message)}</span></div>`;
    }).join('');
  } catch(e) { console.error(e); }
}

// ===== تم RGB =====
let rgbMode = false;
async function loadRGBStatus() {
  try {
    const r = await authF('/api/settings');
    const data = await r.json();
    rgbMode = data.rgb_mode || false;
    updateRGBUI();
  } catch(e) {}
}

function updateRGBUI() {
  const sw = document.getElementById('rgb-switch');
  if (rgbMode) {
    document.body.classList.add('rgb-mode');
    sw.classList.add('on');
  } else {
    document.body.classList.remove('rgb-mode');
    sw.classList.remove('on');
  }
}

async function toggleRGB() {
  const newState = !rgbMode;
  try {
    const r = await authF('/api/settings/rgb', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: newState })
    });
    const data = await r.json();
    rgbMode = data.rgb_mode;
    updateRGBUI();
    toast(rgbMode ? '🌈 RGB فعال شد' : '🌙 RGB غیرفعال شد', 'ok');
  } catch(e) { toast('❌ خطا', 'err'); }
}

// ===== تغییر رمز =====
async function changePassword() {
  const oldPw = document.getElementById('old-password').value;
  const newPw = document.getElementById('new-password').value;
  const confirmPw = document.getElementById('confirm-password').value;
  const result = document.getElementById('password-result');
  if (!oldPw || !newPw || !confirmPw) { result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ همه فیلدها را پر کنید'; return; }
  if (newPw.length < 4) { result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ حداقل ۴ کاراکتر'; return; }
  if (newPw !== confirmPw) { result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ رمزها مطابقت ندارند'; return; }
  try {
    const r = await authF('/api/change-password', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_password: oldPw, new_password: newPw })
    });
    const data = await r.json();
    if (!r.ok) { result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ ' + (data.detail || data.message || 'خطا'); return; }
    result.style.display='block'; result.style.color='#34D399'; result.innerHTML='✅ رمز تغییر کرد!';
    document.getElementById('old-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
    toast('✅ رمز تغییر کرد', 'ok');
  } catch(e) { result.style.display='block'; result.style.color='#F87171'; result.innerHTML='❌ خطا'; }
}

// ===== بکاپ =====
async function createBackup() {
  try {
    const r = await authF('/api/backup');
    const data = await r.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eagle_backup_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast('✅ بکاپ دانلود شد', 'ok');
  } catch(e) { toast('❌ خطا', 'err'); }
}

async function restoreBackup(event) {
  const file = event.target.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    const r = await authF('/api/backup/restore', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!r.ok) { toast('❌ خطا', 'err'); return; }
    toast('✅ بکاپ بازیابی شد', 'ok');
    setTimeout(() => location.reload(), 1000);
  } catch(e) { toast('❌ خطا: ' + e.message, 'err'); }
  event.target.value = '';
}

// ===== بارگذاری اولیه =====
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const r = await fetch('/api/me');
    const d = await r.json();
    if (!d.authenticated) location.href = '/login';
  } catch(e) { location.href = '/login'; }
  
  setLang(currentLang);
  await loadRGBStatus();
  loadDashboard();
  loadInbound();
  loadUsers();
  loadConnections();
  loadLogs();
  
  setInterval(() => {
    if (document.getElementById('pg-dashboard').classList.contains('on')) loadDashboard();
    if (document.getElementById('pg-connections').classList.contains('on')) loadConnections();
    if (document.getElementById('pg-users').classList.contains('on')) loadUsers();
  }, 5000);
});
</script>
</body></html>"""

# ===== صفحه ساب‌لینک =====
def get_sub_page_html(uuid: str, link: dict) -> str:
    from datetime import datetime
    used = link.get('used_bytes', 0)
    limit = link.get('limit_bytes', 0)
    active = link.get('active', True)
    expired = link.get('expired', False)
    label = link.get('label', 'کاربر')
    fingerprint = link.get('fingerprint', 'chrome')
    max_devices = link.get('max_devices', 0)
    protocol = link.get('protocol', 'vless-ws')
    port = link.get('port', 443)
    active_connections = link.get('active_connections', 0)
    active_connections_list = link.get('active_connections_list', [])
    last_connected = link.get('last_connected_at')
    last_connected_text = "—"
    if last_connected:
        try:
            dt = datetime.fromisoformat(last_connected)
            last_connected_text = dt.strftime("%Y-%m-%d %H:%M")
        except:
            last_connected_text = last_connected[:16]
    percent = 0
    if limit > 0:
        percent = min(100, (used / limit) * 100)
    expires_at = link.get('expires_at')
    if expires_at:
        try:
            exp_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            days_left = (exp_date - datetime.now().astimezone()).days
            if days_left < 0:
                days_left = 0
        except:
            days_left = 'نامشخص'
    else:
        days_left = 'نامحدود'
    is_allowed = active and not expired
    sub_url = link.get('sub_url', '')
    def fmt_bytes(b):
        if not b or b == 0:
            return '0 B'
        if b < 1024:
            return f'{b} B'
        if b < 1024**2:
            return f'{b/1024:.1f} KB'
        if b < 1024**3:
            return f'{b/1024**2:.2f} MB'
        return f'{b/1024**3:.2f} GB'
    used_fmt = fmt_bytes(used)
    limit_fmt = 'نامحدود' if limit == 0 else fmt_bytes(limit)
    from main import get_host, generate_vless_link
    host = get_host()
    remark = f"عقاب-{label}"
    new_vless_link = generate_vless_link(uuid, host, remark=remark, protocol=protocol, fingerprint=fingerprint, port=port)
    
    conns_html = ""
    if active_connections > 0:
        conns_html = f"""
        <div style="background:rgba(100,80,255,0.02);border:1px solid rgba(100,80,255,0.04);border-radius:10px;padding:8px 10px;margin:8px 0">
            <div style="display:flex;align-items:center;gap:4px;margin-bottom:4px;font-size:9px;color:#8888BB">
                <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:#34D399;animation:pulse 1.5s infinite"></span>
                <span style="font-weight:700;color:#34D399;font-size:9px">{active_connections} دستگاه متصل</span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:3px">"""
        for conn in active_connections_list[:10]:
            ip = conn.get('ip', 'نامشخص')
            conns_html += f"""<span style="font-family:monospace;font-size:8px;background:rgba(100,80,255,0.04);border:1px solid rgba(100,80,255,0.04);padding:1px 6px;border-radius:3px;color:#8888BB">🔵 {ip}</span>"""
        if len(active_connections_list) > 10:
            conns_html += f"""<span style="font-family:monospace;font-size:8px;background:rgba(100,80,255,0.02);padding:1px 6px;border-radius:3px;color:#555577">+{len(active_connections_list)-10}</span>"""
        conns_html += "</div></div>"
    else:
        conns_html = f"""<div style="background:rgba(100,80,255,0.02);border:1px solid rgba(100,80,255,0.04);border-radius:10px;padding:6px 10px;margin:8px 0;text-align:center"><span style="font-size:9px;color:#555577">🔴 بدون اتصال فعال</span></div>"""
    
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🪐 {label}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}@keyframes fireBG{{0%{{background-position:0% 50%}}25%{{background-position:50% 0%}}50%{{background-position:100% 50%}}75%{{background-position:50% 100%}}100%{{background-position:0% 50%}}}}@keyframes flameFlicker{{0%{{opacity:0.6;transform:scale(1)}}50%{{opacity:1;transform:scale(1.02)}}100%{{opacity:0.6;transform:scale(1)}}}}@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}body{{font-family:'Vazirmatn',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px;color:#F0EEFF;background:linear-gradient(135deg,#0a0a1a,#1a0a2a,#0a0a2a);}}
.stars-sub{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}.star-sub{{position:absolute;border-radius:50%;background:#fff;animation:twinkleSub 4s ease-in-out infinite}}@keyframes twinkleSub{{0%,100%{{opacity:0.1}}50%{{opacity:0.4}}}}
.glow-sub{{position:fixed;border-radius:50%;filter:blur(150px);z-index:0;pointer-events:none}}.glow-sub1{{width:350px;height:350px;background:rgba(100,80,255,0.04);top:-120px;right:-60px}}.glow-sub2{{width:250px;height:250px;background:rgba(167,139,250,0.03);bottom:-60px;left:-40px;animation-delay:2s}}
.card{{position:relative;z-index:10;background:rgba(10,10,30,0.8);backdrop-filter:blur(30px);border:1px solid rgba(100,80,255,0.06);border-radius:20px;padding:24px 22px 20px;max-width:420px;width:100%;box-shadow:0 0 60px rgba(0,0,0,0.4),0 0 80px rgba(100,80,255,0.02);animation:cardIn 0.6s ease;}}@keyframes cardIn{{from{{opacity:0;transform:translateY(20px) scale(0.97)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
.brand{{display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid rgba(100,80,255,0.04);}}.brand-icon{{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#7C6BFF,#5B4BD9,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;box-shadow:0 0 30px rgba(100,80,255,0.1);}}.brand-text .name{{font-size:13px;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C6BFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.brand-text .sub{{font-size:7px;color:#555577;margin-top:0px}}
.user-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:2px}}.user-name{{font-size:17px;font-weight:800;color:#F0EEFF;display:flex;align-items:center;gap:4px}}.user-name .fire{{font-size:15px}}
.status{{display:inline-flex;align-items:center;gap:3px;padding:2px 10px;border-radius:12px;font-size:9px;font-weight:700;}}.status.active{{background:rgba(100,80,255,0.12);color:#A78BFA;border:1px solid rgba(100,80,255,0.08);}}.status.inactive{{background:rgba(239,68,68,0.12);color:#F87171;border:1px solid rgba(239,68,68,0.08);}}
.uuid-box{{background:rgba(100,80,255,0.02);border:1px solid rgba(100,80,255,0.04);border-radius:6px;padding:4px 8px;font-size:8px;font-family:monospace;color:#555577;word-break:break-all;margin:3px 0 8px;cursor:pointer}}.uuid-box:hover{{background:rgba(100,80,255,0.04)}}
.info-grid{{display:grid;gap:5px;margin:8px 0}}.info-item{{background:rgba(100,80,255,0.02);border:1px solid rgba(100,80,255,0.02);border-radius:6px;padding:6px 10px;display:flex;justify-content:space-between;align-items:center}}.info-label{{font-size:9px;color:#8888BB;display:flex;align-items:center;gap:3px}}.info-label i{{font-size:10px;color:#7C6BFF}}.info-value{{font-size:11px;font-weight:700;color:#F0EEFF}}.info-value.used{{color:#A78BFA}}.info-value.proto{{font-size:8px;background:rgba(100,80,255,0.05);padding:1px 6px;border-radius:4px;border:1px solid rgba(100,80,255,0.04);}}
.progress{{margin:8px 0 10px}}.progress-bar{{height:3px;border-radius:3px;background:rgba(100,80,255,0.04);overflow:hidden}}.progress-fill{{height:100%;border-radius:3px;background:linear-gradient(90deg,#7C6BFF,#5B4BD9,#A78BFA);width:{percent:.1f}%;transition:width 1s ease}}.progress-text{{display:flex;justify-content:space-between;font-size:8px;color:#8888BB;margin-top:2px}}.progress-text .pct{{font-weight:700;color:#F0EEFF}}
.vless-section{{background:rgba(100,80,255,0.02);border:1px solid rgba(100,80,255,0.03);border-radius:8px;padding:8px 10px;margin:8px 0}}.vless-label{{font-size:7px;color:#8888BB;font-weight:700;text-transform:uppercase;letter-spacing:.04em;display:flex;align-items:center;gap:4px;margin-bottom:4px}}.vless-label i{{color:#7C6BFF;font-size:10px}}.vless-link{{font-family:monospace;font-size:8px;color:#A78BFA;word-break:break-all;line-height:1.5;background:rgba(0,0,0,0.2);padding:4px 6px;border-radius:4px;border:1px solid rgba(100,80,255,0.02);}}
.actions{{display:flex;gap:4px;margin-top:8px;flex-wrap:wrap}}.btn{{font-family:inherit;font-size:9px;font-weight:600;border-radius:6px;padding:5px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:3px;border:none;transition:all .2s;white-space:nowrap;flex:1;justify-content:center}}.btn i{{font-size:11px}}
.btn-primary{{background:linear-gradient(135deg,#7C6BFF,#5B4BD9);color:#fff;box-shadow:0 3px 15px rgba(100,80,255,0.15)}}.btn-primary:hover{{transform:translateY(-1px);box-shadow:0 6px 25px rgba(100,80,255,0.25)}}
.btn-secondary{{background:rgba(100,80,255,0.03);border:1px solid rgba(100,80,255,0.04);color:#8888BB}}.btn-secondary:hover{{background:rgba(100,80,255,0.06);color:#F0EEFF}}
.btn-success{{background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.08);color:#34D399}}.btn-success:hover{{background:rgba(16,185,129,0.1)}}
.footer{{margin-top:12px;padding-top:10px;border-top:1px solid rgba(100,80,255,0.02);text-align:center;font-size:7px;color:#555577}}.footer .eagle{{color:#7C6BFF;font-weight:700}}
.toast{{position:fixed;bottom:16px;left:50%;transform:translateX(-50%) translateY(40px);background:rgba(10,10,30,0.9);backdrop-filter:blur(20px);border:1px solid rgba(100,80,255,0.08);color:#F0EEFF;border-radius:8px;padding:6px 14px;font-size:10px;opacity:0;transition:all .3s;z-index:999;pointer-events:none;display:flex;align-items:center;gap:4px;box-shadow:0 8px 30px rgba(0,0,0,0.3)}}.toast.show{{opacity:1;transform:translateX(-50%) translateY(0)}}.toast.ok{{border-color:rgba(16,185,129,0.15);color:#34D399}}
@media(max-width:400px){{.card{{padding:16px 14px 14px}}.user-name{{font-size:15px}}.brand-icon{{width:30px;height:30px;font-size:14px}}.info-item{{padding:4px 8px}}.btn{{font-size:8px;padding:4px 8px}}}}
</style>
</head>
<body>
<div class="stars-sub">
    <div class="star-sub" style="width:2px;height:2px;top:10%;left:10%;animation-delay:0s"></div>
    <div class="star-sub" style="width:3px;height:3px;top:30%;left:40%;animation-delay:1.5s"></div>
    <div class="star-sub" style="width:1px;height:1px;top:50%;left:70%;animation-delay:0.8s"></div>
    <div class="star-sub" style="width:2px;height:2px;top:70%;left:20%;animation-delay:2.2s"></div>
    <div class="star-sub" style="width:3px;height:3px;top:85%;left:80%;animation-delay:0.5s"></div>
</div>
<div class="glow-sub glow-sub1"></div><div class="glow-sub glow-sub2"></div>
<div class="toast" id="toast"></div>
<div class="card">
    <div class="brand"><div class="brand-icon">🪐</div><div class="brand-text"><div class="name">پنل عقاب</div><div class="sub">اطلاعات اشتراک</div></div></div>
    <div class="user-header"><div class="user-name"><span class="fire">🪐</span> {label}</div><span class="status {'active' if is_allowed else 'inactive'}"><i class="ti {'ti-circle-check' if is_allowed else 'ti-circle-x'}"></i>{'فعال' if is_allowed else 'غیرفعال'}</span></div>
    <div class="uuid-box" onclick="copyUUID()">🔑 {uuid}</div>
    {conns_html}
    <div class="info-grid">
        <div class="info-item"><span class="info-label"><i class="ti ti-database"></i> مصرف</span><span class="info-value used">{used_fmt}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-package"></i> سهمیه</span><span class="info-value">{limit_fmt}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-calendar"></i> باقیمانده</span><span class="info-value">{days_left if days_left == 'نامحدود' else f'{days_left} روز'}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-devices"></i> دستگاه</span><span class="info-value">{max_devices if max_devices > 0 else '∞'}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-clock"></i> آخرین اتصال</span><span class="info-value" style="font-size:9px;">{last_connected_text}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-fingerprint"></i> FP</span><span class="info-value proto">{fingerprint}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-settings"></i> پروتکل</span><span class="info-value proto">{protocol}</span></div>
        <div class="info-item"><span class="info-label"><i class="ti ti-plug"></i> پورت</span><span class="info-value proto">{port}</span></div>
    </div>
    <div class="progress"><div class="progress-bar"><div class="progress-fill" style="width:{percent:.1f}%"></div></div><div class="progress-text"><span>میزان مصرف</span><span class="pct">{percent:.1f}%</span></div></div>
    <div class="vless-section"><div class="vless-label"><i class="ti ti-link"></i> لینک کانفیگ</div><div class="vless-link" id="vless-link">{new_vless_link}</div></div>
    <div class="actions"><button class="btn btn-primary" onclick="copyVless()"><i class="ti ti-copy"></i> کپی</button><button class="btn btn-success" onclick="copySub()"><i class="ti ti-link"></i> ساب</button><button class="btn btn-secondary" onclick="showQR()"><i class="ti ti-qrcode"></i> QR</button></div>
    <div class="footer"><span class="eagle">🪐</span> پنل عقاب</div>
</div>
<script>const vless=`{new_vless_link}`;const subUrl=`{sub_url}`;const uuid=`{uuid}`;function toast(msg,type=''){{const t=document.getElementById('toast');t.textContent=msg;t.className='toast show'+(type?' '+type:'');setTimeout(()=>t.classList.remove('show'),2000);}}function copyVless(){{navigator.clipboard.writeText(vless).then(()=>toast('✅ کپی شد','ok'));}}function copySub(){{navigator.clipboard.writeText(subUrl).then(()=>toast('✅ کپی شد','ok'));}}function copyUUID(){{navigator.clipboard.writeText(uuid).then(()=>toast('✅ کپی شد','ok'));}}function showQR(){{window.open('https://api.qrserver.com/v1/create-qr-code/?size=250x250&data='+encodeURIComponent(vless),'_blank');}}</script>
</body></html>"""
