from typing import Any
from django.db.models.query import QuerySet
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Wager, WagerOption, Bet, WagerUser
from .forms import wager_bet_form, wager_resolve_form

class WagerListView(generic.ListView):
    context_object_name = 'all_wagers'
    template_name = 'bet/home.html'

    def get_queryset(self) -> QuerySet[Wager]:
        return Wager.objects.all()
    

@login_required
def wager_view(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    user = request.user
    form = wager_bet_form(wager, user)()
    try:
        placed_bet = Bet.objects.get(user=request.user.id, wager=wager_id)
    except:
        placed_bet = None

    return render(request, "bet/wager.html", context={
        "wager": wager,
        "form": form,
        "placed_bet": placed_bet,
    })

@login_required
def place_bet(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    user: WagerUser = request.user
    # Reject attempting to place a bet on a wager that the user has already bet on
    if bool(Bet.objects.filter(user=user.id, wager=wager_id)):
        return HttpResponseForbidden()
    
    form = wager_bet_form(wager, request.user)
    form = form(data=request.POST)
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
    
@staff_member_required
def resolve_wager_view(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    if request.method == "GET":
        form = wager_resolve_form(wager)()
    else:
        form = wager_resolve_form(wager)(data=request.POST)
        if form.is_valid():
            winning_option: WagerOption = form.cleaned_data["selected_option"]
            winning_ratio = float(wager.total_wager_value()) / float(winning_option.option_total_value())
            for bet in winning_option.bet_set.all():
                user: WagerUser = bet.user
                user.balance = F('balance') + (bet.value * winning_ratio)
                user.save()
            wager.resolved = True
            wager.open = False
            wager.save()
            return redirect(reverse('bet:home'))
        
    return render(request, "bet/wager_resolve.html",context={"wager": wager, "form": form})
    
    
