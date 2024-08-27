from django.contrib import admin, messages
from django.utils.translation import ngettext
from .models import Wager, WagerOption, WagerUser, Bet

# Register your models here.

class OptionInline(admin.TabularInline):
    model = WagerOption
    extra = 2

class WagerView(admin.ModelAdmin):
    model = Wager
    fieldsets = [
        (None, {"fields": ["name", "description", "pot", "open", "resolved"]})
    ]
    readonly_fields = ["open", "resolved"]
    inlines = [OptionInline]
    actions = ['close_bet']

    @admin.action(description="Close selected wagers")
    def close_bet(self, request, queryset):
        updated = queryset.update(open=False)
        self.message_user(
            request,
            ngettext(
                "%d wager was successfully closed.",
                "%d wagers were successfully closed.",
                updated
            ) % updated,
            messages.SUCCESS,
        )

class ReadOnly(admin.ModelAdmin):
    def has_change_permission(self, request, obj = None) -> bool:
        return False

admin.site.register(Wager, WagerView)
admin.site.register(WagerUser)
admin.site.register(Bet, ReadOnly)
