from django.contrib import admin

# Register your models here.
from core.models import EEGCheck, Settings


@admin.register(EEGCheck)
class EEGCheckAdmin(admin.ModelAdmin):
    # readonly_fields = ['check_time', 'accuracy']
    list_display = [field.name for field in EEGCheck._meta.get_fields()]


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['accuracy', 's_h_min', 's_h_max', 's_w_min', 's_w_max', 'w_h_min', 'w_h_max', 'w_w_min', 'w_w_max']
