from typing import Any
from django.db.models.query import QuerySet
from django.db.models import F
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from .models import Wager, WagerOption, Bet, WagerUser

from enum import Enum

# Create your views here.
class WagerListView(generic.ListView):
    context_object_name = 'all_wagers'
    template_name = 'bet/home.html'

    def get_queryset(self) -> QuerySet[Wager]:
        return Wager.objects.all()
    
class WagerDetailView(generic.DetailView):
    model = Wager
    template_name = 'bet/wager.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        try:
            placed_bet = Bet.objects.get(user=request.user.id, wager=kwargs['pk'])
        except:
            placed_bet = None
        context = self.get_context_data(object=self.object, placed_bet=placed_bet)
        return self.render_to_response(context)



def place_bet(request, wager_id: int):
    class BetErrorType(Enum):
        NO_OPTION = "no_option"
        NOT_ENOUGH_POINTS = "no_points"
        INVALID_BET_VALUE = "invalid_bet"

    def show_error(request, error_type: BetErrorType):
        return render(
            request,
            "bet/wager.html",
            {
                "wager": wager,
                error_type.value: "a" # just need it to exist
            }
        )

    wager = get_object_or_404(Wager, pk=wager_id)
    if bool(Bet.objects.filter(user=request.user.id, wager=wager_id)):
        return HttpResponseForbidden()
    try:
        selected_option = wager.wageroption_set.get(pk=request.POST['option'])
    except (KeyError, WagerOption.DoesNotExist):
        return show_error(request, BetErrorType.NO_OPTION)
    else:
        try:
            bet_value = int(request.POST['bet_value'])
        except (KeyError, ValueError):
            return show_error(request, BetErrorType.INVALID_BET_VALUE)
        else:
            user: WagerUser = request.user
            if bet_value < 0:
                return show_error(request, BetErrorType.INVALID_BET_VALUE)
            if bet_value > user.balance:
                return show_error(request, BetErrorType.NOT_ENOUGH_POINTS)

            bet = Bet(option=selected_option, user=request.user, value=bet_value, wager=wager)
            bet.save()
            user.balance = F("balance") - bet_value
            user.save()
            return redirect(reverse('bet:home'))
