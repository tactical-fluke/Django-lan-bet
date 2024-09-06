from typing import Any
from django.db.models.query import QuerySet
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .models import Wager, WagerOption, Bet, WagerUser
from .forms import OptionForm, BetForm, InstanceFormSet

class WagerListView(generic.ListView):
    context_object_name = 'all_wagers'
    template_name = 'bet/home.html'

    def get_queryset(self) -> QuerySet[Wager]:
        return Wager.objects.all()
    

@login_required
def wager_view(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    options = wager.wageroption_set.all()
    user = request.user
    form = BetForm(wager, user)
    try:
        placed_bet = Bet.objects.get(user=request.user.id, wager=wager_id)
    except:
        placed_bet = None

    return render(request, "bet/wager.html", context={
        "wager": wager,
        "form": form,
        "placed_bet": placed_bet,
        "options": options,
    })

@login_required
def place_bet(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    # reject placing a bet against a wager that is already closed or resolved
    if not wager.open or wager.resolved:
        return HttpResponseForbidden()
    user: WagerUser = request.user
    # Reject attempting to place a bet on a wager that the user has already bet on
    if bool(Bet.objects.filter(user=user.id, wager=wager_id)):
        return HttpResponseForbidden()
    
    form = BetForm(wager, user, data=request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        option = cleaned_data['selected_option']
        bet_value = cleaned_data['bet_value']

        bet = Bet(option=option, user=request.user, value=bet_value, wager=wager)
        bet.save()
        user.balance = F("balance") - bet_value
        user.save()
        return redirect(reverse('bet:home'))
    else:
        return render(
            request,
            "bet/wager.html",
            context={
                "wager": wager,
                "form": form,
            }
        )
    
def _resolve_wager(winning_option: WagerOption):
    wager = winning_option.wager
    winning_option_value = float(winning_option.total_value())
    if winning_option_value > 0.0:
        winning_ratio = float(wager.total_value()) / winning_option_value
        for bet in winning_option.bet_set.all():
            user: WagerUser = bet.user
            user.balance = F('balance') + (bet.value * winning_ratio)
            user.save()
    wager.resolved = True
    wager.open = False
    wager.save()
    
@staff_member_required
def resolve_wager_view(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    if request.method == "GET":
        form = OptionForm(instance=wager)
    else:
        form = OptionForm(instance=wager, data=request.POST)
        if form.is_valid():
            winning_option: WagerOption = form.cleaned_data["selected_option"]
            _resolve_wager(winning_option)
            return redirect(reverse('bet:home'))
        
    return render(request, "bet/wager_resolve.html",context={"wager": wager, "form": form})

@staff_member_required
def resolve_wagers_view(request):
    if request.method == "GET":
        wager_ids = request.GET.getlist('wager')
        wagers = [get_object_or_404(Wager, pk=id) for id in wager_ids]
        OptionFormSet = formset_factory(form=OptionForm, formset=InstanceFormSet, min_num=len(wagers)-1)
        formset = OptionFormSet(instances=wagers, )
    else:
        total_forms = int(request.POST['form-TOTAL_FORMS'])
        wagers = [get_object_or_404(Wager, pk=int(request.POST[f"form-{i}-wager_instance_id"])) for i in range(total_forms)]
        OptionFormSet = formset_factory(form=OptionForm, formset=InstanceFormSet, min_num=len(wagers)-1)
        formset = OptionFormSet(instances=wagers, data=request.POST)
        if formset.is_valid():
            for form in formset.forms:
                winning_option = form.cleaned_data['selected_option']
                _resolve_wager(winning_option)
            return redirect('bet:home')

    return render(
        request,
        "bet/multi_resolve_wager.html",
        context={
            "forms": formset
        }
    )
