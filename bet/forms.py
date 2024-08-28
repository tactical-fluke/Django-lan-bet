from django import forms
from django.core.exceptions import ValidationError
from .models import Wager, WagerUser, WagerOption
from functools import partial

def validate_user_has_enough_points_for_bet(user: WagerUser, bet_value: int):
        if bet_value > user.balance:
            raise ValidationError("User does not have enough points for this bet")
        
def validate_non_negative(bet_value: int):
    if bet_value < 0:
        raise ValidationError("Bet must be non-negative")
    
class BetForm(forms.Form):
    selected_option = forms.ChoiceField(widget=forms.widgets.RadioSelect())
    bet_value = forms.IntegerField()

    def __init__(self, wager_instance: Wager, wager_user: WagerUser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["selected_option"] = forms.TypedChoiceField(
            choices=map(lambda option: (option.id, option.name), wager_instance.wageroption_set.all()),
            coerce=lambda id: WagerOption.objects.get(pk=int(id)),
            widget=forms.widgets.RadioSelect()
        )
        self.fields["bet_value"] = forms.IntegerField(validators=[partial(validate_user_has_enough_points_for_bet, wager_user), validate_non_negative])

class OptionForm(forms.Form):
    wager_instance_id = forms.IntegerField(widget=forms.HiddenInput)
    selected_option = forms.ChoiceField(widget=forms.widgets.RadioSelect())

    def __init__(self, *args, **kwargs):
        wager_instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        self.initial['wager_instance_id'] = wager_instance.id
        self.fields['selected_option'] = self.fields["selected_option"] = forms.TypedChoiceField(
            choices=map(lambda option: (option.id, option.name), wager_instance.wageroption_set.all()),
            coerce=lambda id: WagerOption.objects.get(pk=int(id)),
            widget=forms.widgets.RadioSelect()
        )

# Giga shoutout to https://stackoverflow.com/questions/36915740/set-instance-of-each-form-in-django-model-formset
class InstanceFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
          self.instances = kwargs.pop('instances')
          super(InstanceFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        form_kwargs = super(InstanceFormSet, self).get_form_kwargs(index)
        if index < len(self.instances):
             form_kwargs['instance'] = self.instances[index]
        return form_kwargs
