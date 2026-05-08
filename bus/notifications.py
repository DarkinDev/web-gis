"""
Bus Notifications - Email notification system
Gửi email thông báo cho admin khi có sự kiện trong hệ thống.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading


def _send_async(subject, message, html_message, recipient_list):
    """Gửi email trong background thread để không block request"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception:
        pass


def _notify(subject, template, context):
    """Helper: render template rồi gửi email async"""
    recipients = getattr(settings, 'ADMIN_NOTIFICATION_EMAILS', [])
    if not recipients:
        return
    try:
        html_message = render_to_string(template, context)
        # Strip HTML để tạo plain text
        plain = f"{subject}\n\n" + "\n".join(
            line.strip() for line in html_message.splitlines() if line.strip()
        )
        t = threading.Thread(
            target=_send_async,
            args=(subject, plain, html_message, recipients),
            daemon=True
        )
        t.start()
    except Exception:
        pass


# ─── Notification Functions ────────────────────────────────────────────────────

def notify_new_route(route):
    """Gửi email khi Admin tạo mới một tuyến xe"""
    _notify(
        subject=f"🚌 [BusGIS] Tuyến mới: {route.route_number} - {route.name}",
        template='email/notify_new_route.html',
        context={'route': route},
    )


def notify_route_updated(route):
    """Gửi email khi Admin cập nhật tuyến xe"""
    _notify(
        subject=f"✏️ [BusGIS] Cập nhật tuyến: {route.route_number} - {route.name}",
        template='email/notify_route_updated.html',
        context={'route': route},
    )


def notify_new_stop(stop):
    """Gửi email khi Admin tạo mới trạm dừng"""
    _notify(
        subject=f"📍 [BusGIS] Trạm mới: {stop.name}",
        template='email/notify_new_stop.html',
        context={'stop': stop},
    )


def notify_stop_updated(stop):
    """Gửi email khi Admin cập nhật trạm dừng"""
    _notify(
        subject=f"✏️ [BusGIS] Cập nhật trạm: {stop.name}",
        template='email/notify_stop_updated.html',
        context={'stop': stop},
    )


def notify_item_deleted(item_type, item_name, item_id):
    """Gửi email khi Admin xóa tuyến hoặc trạm (soft delete)"""
    _notify(
        subject=f"🗑️ [BusGIS] Đã xóa {item_type}: {item_name}",
        template='email/notify_deleted.html',
        context={
            'item_type': item_type,
            'item_name': item_name,
            'item_id': item_id,
            'restore_url': f"/admin/bus/{item_type.lower().replace(' ', '')}/restore/",
        },
    )
