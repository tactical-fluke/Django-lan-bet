from django.contrib import admin

from .models import Wager, WagerOption

# Register your models here.

class OptionInline(admin.TabularInline):
    model = WagerOption
    extra = 2

class WagerView(admin.ModelAdmin):
    model = Wager
    fieldsets = [
        (None, {"fields": ["name", "description", "pot"]})
    ]
    inlines = [OptionInline]

admin.site.register(Wager, WagerView)
