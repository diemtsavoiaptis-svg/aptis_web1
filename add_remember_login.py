from pathlib import Path
import re

# Tìm file interface đăng nhập
candidates = [
    Path("templates/core/home.html"),
    Path("templates/core/login.html"),
    Path("templates/core/index.html"),
]

target = None
for p in candidates:
    if p.exists():
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "Login" in text or "dang-nhap" in text or "login" in text.lower():
            target = p
            break

if target is None:
    for p in Path("templates").rglob("*.html"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "Login" in text and "<form" in text:
            target = p
            break

if target is None:
    raise SystemExit("KHONG_TIM_THAY_FILE_DANG_NHAP")

s = target.read_text(encoding="utf-8", errors="ignore")
Path(str(target) + ".bak_remember_login").write_text(s, encoding="utf-8")

# Add autocomplete cho input account và mật khẩu
s = re.sub(
    r'(<input[^>]*(?:name=["\'](?:username|email|login)["\']|type=["\']email["\'])[^>]*)(>)',
    lambda m: m.group(1) + (' autocomplete="username"' if "autocomplete=" not in m.group(1) else "") + m.group(2),
    s,
    flags=re.I
)

s = re.sub(
    r'(<input[^>]*type=["\']password["\'][^>]*)(>)',
    lambda m: m.group(1) + (' autocomplete="current-password"' if "autocomplete=" not in m.group(1) else "") + m.group(2),
    s,
    flags=re.I
)

remember_html = r'''
<div class="remember-login-row">
    <label class="remember-login-label">
        <input type="checkbox" id="rememberLoginInfo">
        <span>Save information đăng nhập</span>
    </label>
    <small>Trình duyệt sẽ hỗ trợ lưu mật khẩu an toàn.</small>
</div>
'''

# Chèn checkbox trước nút Login đầu tiên nếu chưa có
if "rememberLoginInfo" not in s:
    # Ưu tiên chèn trước button submit
    s = re.sub(
        r'(<button[^>]*type=["\']submit["\'][^>]*>[\s\S]*?Login[\s\S]*?</button>)',
        remember_html + r"\n\1",
        s,
        count=1,
        flags=re.I
    )

    # Nếu không tìm được button thì chèn trước input submit
    if "rememberLoginInfo" not in s:
        s = re.sub(
            r'(<input[^>]*type=["\']submit["\'][^>]*>)',
            remember_html + r"\n\1",
            s,
            count=1,
            flags=re.I
        )

style_block = r'''
<style id="remember-login-style">
.remember-login-row{
    margin: 14px 0 18px;
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(255, 241, 244, .82);
    border: 1px solid rgba(255, 95, 118, .22);
    color: #5b0010;
}
.remember-login-label{
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 900;
    cursor: pointer;
    user-select: none;
}
.remember-login-label input{
    width: 18px;
    height: 18px;
    accent-color: #e60023;
}
.remember-login-row small{
    display: block;
    margin-top: 6px;
    color: #9a5360;
    font-weight: 700;
    font-size: 13px;
}
</style>
'''

script_block = r'''
<script id="remember-login-script">
(function(){
    const STORAGE_KEY = "aptis_remember_login_value";
    const CHECK_KEY = "aptis_remember_login_checked";

    function findLoginInput(){
        return document.querySelector(
            'input[name="username"], input[name="email"], input[name="login"], input[type="email"], input[type="text"]'
        );
    }

    function initRememberLogin(){
        const checkbox = document.getElementById("rememberLoginInfo");
        const loginInput = findLoginInput();
        const form = checkbox checkbox.closest("form") : null;

        if(!checkbox || !loginInput || !form) return;

        const savedChecked = localStorage.getItem(CHECK_KEY) === "1";
        const savedValue = localStorage.getItem(STORAGE_KEY) || "";

        checkbox.checked = savedChecked;

        if(savedChecked && savedValue && !loginInput.value){
            loginInput.value = savedValue;
        }

        form.addEventListener("submit", function(){
            if(checkbox.checked){
                localStorage.setItem(CHECK_KEY, "1");
                localStorage.setItem(STORAGE_KEY, loginInput.value || "");
            }else{
                localStorage.removeItem(CHECK_KEY);
                localStorage.removeItem(STORAGE_KEY);
            }
        });
    }

    if(document.readyState === "loading"){
        document.addEventListener("DOMContentLoaded", initRememberLogin);
    }else{
        initRememberLogin();
    }
})();
</script>
'''

if "remember-login-style" not in s:
    if "</head>" in s:
        s = s.replace("</head>", style_block + "\n</head>", 1)
    else:
        s = style_block + "\n" + s

if "remember-login-script" not in s:
    if "</body>" in s:
        s = s.replace("</body>", script_block + "\n</body>", 1)
    else:
        s += "\n" + script_block

target.write_text(s, encoding="utf-8")
print("DA_THEM_NUT_LUU_THONG_TIN_DANG_NHAP:", target)
