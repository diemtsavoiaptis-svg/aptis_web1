from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .models import UserDeviceSession, SecurityAlert


class SecurityHeadersMiddleware(MiddlewareMixin):
    PROTECTED_PREFIXES = (
        "/dashboard/",
        "/listening/",
        "/secure/audio/",
    )

    def process_response(self, request, response):
        path = request.path or ""

        if path.startswith(self.PROTECTED_PREFIXES):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Frame-Options"] = "DENY"
            response["Referrer-Policy"] = "no-referrer"
            response["X-Content-Type-Options"] = "nosniff"
            response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=(), display-capture=()"

        return response


class DeviceLimitMiddleware(MiddlewareMixin):
    MAX_STUDENT_SESSIONS = 2
    MAX_SAFE_IPS = 2
    MAX_SAFE_USER_AGENTS = 2

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

        existed_ip_before = UserDeviceSession.objects.filter(
            user=user,
            ip_address=ip_address
        ).exists()

        existed_agent_before = UserDeviceSession.objects.filter(
            user=user,
            user_agent=user_agent
        ).exists()

        UserDeviceSession.objects.update_or_create(
            user=user,
            session_key=session_key,
            defaults={
                "user_agent": user_agent,
                "ip_address": ip_address,
                "last_seen": timezone.now(),
            }
        )

        if not existed_ip_before:
            self.create_alert_once(
                user=user,
                severity="high",
                reason="T?i kho?n ??ng nh?p t? IP m?i",
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if not existed_agent_before:
            self.create_alert_once(
                user=user,
                severity="medium",
                reason="T?i kho?n ??ng nh?p t? thi?t b? ho?c tr?nh duy?t m?i",
                ip_address=ip_address,
                user_agent=user_agent,
            )

        unique_ips = (
            UserDeviceSession.objects
            .filter(user=user)
            .exclude(ip_address__isnull=True)
            .values("ip_address")
            .distinct()
            .count()
        )

        unique_agents = (
            UserDeviceSession.objects
            .filter(user=user)
            .exclude(user_agent="")
            .values("user_agent")
            .distinct()
            .count()
        )

        if unique_ips > self.MAX_SAFE_IPS:
            self.create_alert_once(
                user=user,
                severity="critical",
                reason=f"T?i kho?n c? d?u hi?u b?t th??ng: ??ng nh?p t? {unique_ips} IP kh?c nhau",
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if unique_agents > self.MAX_SAFE_USER_AGENTS:
            self.create_alert_once(
                user=user,
                severity="high",
                reason=f"T?i kho?n c? d?u hi?u chia s?: xu?t hi?n {unique_agents} thi?t b? ho?c tr?nh duy?t kh?c nhau",
                ip_address=ip_address,
                user_agent=user_agent,
            )

        active_sessions = list(
            UserDeviceSession.objects
            .filter(user=user)
            .order_by("-last_seen")
        )

        if len(active_sessions) > self.MAX_STUDENT_SESSIONS:
            self.create_alert_once(
                user=user,
                severity="critical",
                reason="T?i kho?n v??t qu? gi?i h?n 2 phi?n ??ng nh?p",
                ip_address=ip_address,
                user_agent=user_agent,
            )

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
