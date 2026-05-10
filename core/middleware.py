from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.deprecation import MiddlewareMixin

from .models import UserDeviceSession, SecurityAlert


class SecurityHeadersMiddleware(MiddlewareMixin):
    PROTECTED_PREFIXES = (
        "/dashboard/",
        "/listening/",
        "/secure/audio/",
        "/security/event/",
    )

    def process_response(self, request, response):
        path = request.path or ""

        if path.startswith(self.PROTECTED_PREFIXES):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["Referrer-Policy"] = "no-referrer"
            response["X-Content-Type-Options"] = "nosniff"
            response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=(), display-capture=()"

        return response


class DeviceLimitMiddleware(MiddlewareMixin):
    MAX_STUDENT_SESSIONS = 2
    MAX_SAFE_IPS = 2
    MAX_SAFE_USER_AGENTS = 2
    DEVICE_COOKIE_NAME = "tsa_device_id"

    def process_request(self, request):
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return None

        if user.is_staff or user.is_superuser:
            return None

        if request.path.startswith("/admin/"):
            return None

        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:1000]
        ip_address = self.get_client_ip(request)
        device_id = request.COOKIES.get(self.DEVICE_COOKIE_NAME, "")

        if not device_id:
            device_id = get_random_string(48)
            request._tsa_new_device_id = device_id

        existed_ip_before = UserDeviceSession.objects.filter(user=user, ip_address=ip_address).exists()
        existed_agent_before = UserDeviceSession.objects.filter(user=user, user_agent=user_agent).exists()
        existed_device_before = UserDeviceSession.objects.filter(user=user, device_id=device_id).exists()

        UserDeviceSession.objects.update_or_create(
            user=user,
            session_key=session_key,
            defaults={
                "device_id": device_id,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "last_seen": timezone.now(),
            }
        )

        if not existed_ip_before:
            self.create_alert_once(user, "high", "Tài khoản đăng nhập từ IP mới", ip_address, user_agent)

        if not existed_agent_before:
            self.create_alert_once(user, "medium", "Tài khoản đăng nhập từ thiết bị hoặc trình duyệt mới", ip_address, user_agent)

        if not existed_device_before:
            self.create_alert_once(user, "high", "Tài khoản xuất hiện mã thiết bị mới", ip_address, user_agent)

        unique_ips = UserDeviceSession.objects.filter(user=user).exclude(ip_address__isnull=True).values("ip_address").distinct().count()
        unique_agents = UserDeviceSession.objects.filter(user=user).exclude(user_agent="").values("user_agent").distinct().count()
        unique_devices = UserDeviceSession.objects.filter(user=user).exclude(device_id="").values("device_id").distinct().count()

        if unique_ips > self.MAX_SAFE_IPS:
            self.create_alert_once(user, "critical", f"Tài khoản có dấu hiệu bất thường: đăng nhập từ {unique_ips} IP khác nhau", ip_address, user_agent)

        if unique_agents > self.MAX_SAFE_USER_AGENTS:
            self.create_alert_once(user, "high", f"Tài khoản có dấu hiệu chia sẻ: xuất hiện {unique_agents} trình duyệt khác nhau", ip_address, user_agent)

        if unique_devices > self.MAX_STUDENT_SESSIONS:
            self.create_alert_once(user, "critical", f"Tài khoản có dấu hiệu chia sẻ: xuất hiện {unique_devices} mã thiết bị khác nhau", ip_address, user_agent)

        active_sessions = list(UserDeviceSession.objects.filter(user=user).order_by("-last_seen"))

        if len(active_sessions) > self.MAX_STUDENT_SESSIONS:
            self.create_alert_once(user, "critical", "Tài khoản vượt quá giới hạn 2 phiên đăng nhập", ip_address, user_agent)

            current_item = None
            other_items = []

            for item in active_sessions:
                if item.session_key == session_key:
                    current_item = item
                else:
                    other_items.append(item)

            keep_ids = set()

            if current_item:
                keep_ids.add(current_item.id)

            for item in other_items[: self.MAX_STUDENT_SESSIONS - len(keep_ids)]:
                keep_ids.add(item.id)

            sessions_to_delete = UserDeviceSession.objects.filter(user=user).exclude(id__in=keep_ids)

            for item in sessions_to_delete:
                Session.objects.filter(session_key=item.session_key).delete()

            sessions_to_delete.delete()

        return None

    def process_response(self, request, response):
        new_device_id = getattr(request, "_tsa_new_device_id", None)

        if new_device_id:
            response.set_cookie(
                self.DEVICE_COOKIE_NAME,
                new_device_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
                secure=request.is_secure(),
            )

        return response

    def create_alert_once(self, user, severity, reason, ip_address=None, user_agent=""):
        SecurityAlert.objects.get_or_create(
            user=user,
            reason=reason,
            ip_address=ip_address,
            is_resolved=False,
            defaults={
                "severity": severity,
                "user_agent": user_agent,
            }
        )

    def get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
