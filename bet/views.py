from typing import Any
from django.db.models.query import QuerySet
from django.db.models import F
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from .models import Wager, WagerOption, Bet, WagerUser
from .forms import wager_bet_form

from enum import Enum

# Create your views here.
class WagerListView(generic.ListView):
    context_object_name = 'all_wagers'
    template_name = 'bet/home.html'

    def get_queryset(self) -> QuerySet[Wager]:
        return Wager.objects.all()
    

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
    
