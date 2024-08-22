from django.contrib import admin

from .models import Wager, WagerOption, WagerUser, Bet

# Register your models here.

class OptionInline(admin.TabularInline):
    model = WagerOption
    extra = 2

class WagerView(admin.ModelAdmin):
    model = Wager
    fieldsets = [
        (None, {"fields": ["name", "description", "pot", "open"]})
    ]
    readonly_fields = ["open"]
    inlines = [OptionInline]

class ReadOnly(admin.ModelAdmin):
    def has_change_permission(self, request, obj = None) -> bool:
        return False

admin.site.register(Wager, WagerView)
admin.site.register(WagerUser)
admin.site.register(Bet, ReadOnly)
