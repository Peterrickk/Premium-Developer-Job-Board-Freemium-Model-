from .models import AuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def create_audit_log(request, action):
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)

    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address
    )