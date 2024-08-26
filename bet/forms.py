from django import forms
from django.core.exceptions import ValidationError
from .models import Wager, WagerUser, WagerOption


def wager_bet_form(wager: int | Wager, user: WagerUser):
    wager = Wager.objects.get(pk=wager) if isinstance(wager, int) else wager

    def validate_user_has_enough_points_for_bet(bet_value: int):
        if bet_value > user.balance:
            raise ValidationError("User does not have enough points for this bet")
        
    def validate_non_negative(bet_value: int):
        if bet_value < 0:
            raise ValidationError("Bet must be non-negative")

    class WagerBetForm(forms.Form):
        selected_option = forms.TypedChoiceField(
            choices=map(lambda option: (option.id, option.name), wager.wageroption_set.all()),
            coerce=lambda id: WagerOption.objects.get(pk=int(id)),
            widget=forms.widgets.RadioSelect()
        )
        bet_value = forms.IntegerField(validators=[validate_user_has_enough_points_for_bet, validate_non_negative])

    return WagerBetForm
        
def wager_resolve_form(wager: int | Wager):
    wager = Wager.objects.get(pk=wager) if isinstance(wager, int) else wager

    class WagerResolveForm(forms.Form):
        selected_option = forms.TypedChoiceField(
            choices=map(lambda option: (option.id, option.name), wager.wageroption_set.all()),
            coerce=lambda id: WagerOption.objects.get(pk=int(id)),
            widget=forms.widgets.RadioSelect(),
            label="Winning option"
        )

    return WagerResolveForm
