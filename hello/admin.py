from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Company)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(PremiumSubscription)

admin.site.register(AuditLog)