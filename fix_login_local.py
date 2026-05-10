from pathlib import Path
import re

# 1) Sửa form: không bắt email, sửa placeholder tiếng Việt
forms_path = Path("core/forms.py")
forms = forms_path.read_text(encoding="utf-8", errors="ignore")

forms = forms.replace("forms.EmailField", "forms.CharField")
forms = forms.replace("forms.EmailInput", "forms.TextInput")

forms = forms.replace('"placeholder": "Email"', '"placeholder": "Tài khoản hoặc email"')
forms = forms.replace('"placeholder": "H? v? t?n h?c vi?n"', '"placeholder": "Họ và tên học viên"')
forms = forms.replace('"placeholder": "S? ?i?n tho?i"', '"placeholder": "Số điện thoại"')
forms = forms.replace('"placeholder": "M?t kh?u"', '"placeholder": "Mật khẩu"')

# Thêm autocomplete username cho ô tài khoản nếu chưa có
forms = forms.replace(
    '"placeholder": "Tài khoản hoặc email"\n        })',
    '"placeholder": "Tài khoản hoặc email",\n            "autocomplete": "username"\n        })'
)

forms_path.write_text(forms, encoding="utf-8")


# 2) Sửa template: nếu còn input type=email thì đổi sang text
for p in Path("templates").rglob("*.html"):
    html = p.read_text(encoding="utf-8", errors="ignore")
    html = html.replace('type="email"', 'type="text"')
    html = html.replace("type='email'", "type='text'")
    p.write_text(html, encoding="utf-8")


# 3) Sửa login_view: admin/admin@gmail.com đều đăng nhập được, sửa thông báo tiếng Việt
views_path = Path("core/views.py")
views = views_path.read_text(encoding="utf-8", errors="ignore")

new_login_view = '''def login_view(request):
    if request.method != "POST":
        return redirect("home")

    ip = get_client_ip(request) or "unknown"
    throttle_key = f"login_fail:{ip}"
    fail_count = cache.get(throttle_key, 0)

    if fail_count >= 5:
        messages.error(request, "Bạn đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.")
        return redirect("home")

    form = LoginForm(request.POST)

    if not form.is_valid():
        cache.set(throttle_key, fail_count + 1, 60 * 15)
        messages.error(request, "Thông tin đăng nhập chưa hợp lệ.")
        return redirect("home")

    account = form.cleaned_data["email"].strip()
    password = form.cleaned_data["password"]

    candidates = [account]
    if account.lower() == "admin":
        candidates = ["admin", "admin@gmail.com"]

    user_check = User.objects.filter(username__in=candidates).first()

    if user_check and not user_check.is_active:
        messages.error(request, "Tài khoản của bạn đang chờ admin duyệt.")
        return redirect("home")

    user = None
    for username in candidates:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            break

    if user is None:
        cache.set(throttle_key, fail_count + 1, 60 * 15)

        target_user = User.objects.filter(username__in=candidates).first()

        if target_user:
            SecurityAlert.objects.get_or_create(
                user=target_user,
                reason="Có nhiều lần đăng nhập sai mật khẩu",
                defaults={
                    "ip_address": ip
                }
            )

        messages.error(request, "Tài khoản hoặc mật khẩu không đúng.")
        return redirect("home")

    cache.delete(throttle_key)
    login(request, user)
    return redirect("dashboard")
'''

pattern = r'def login_view\(request\):.*?return redirect\("dashboard"\)\n'
views2, count = re.subn(pattern, new_login_view + "\n", views, count=1, flags=re.S)

if count == 0:
    print("CHUA_SUA_DUOC_LOGIN_VIEW")
else:
    views_path.write_text(views2, encoding="utf-8")
    print("DA_SUA_LOGIN_VIEW")

print("DA_SUA_FORMS_TEMPLATE_VIEWS")
