from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from .models import Wager, WagerOption, Bet

# Create your views here.
class WagerListView(generic.ListView):
    context_object_name = 'all_wagers'
    template_name = 'bet/home.html'

    def get_queryset(self) -> QuerySet[Wager]:
        return Wager.objects.all()
    
class WagerDetailView(generic.DetailView):
    model = Wager
    template_name = 'bet/wager.html'

def place_bet(request, wager_id: int):
    wager = get_object_or_404(Wager, pk=wager_id)
    try:
        selected_option = wager.wageroption_set.get(pk=request.POST['option'])
    except (KeyError, WagerOption.DoesNotExist):
        return render(
            request,
            "bet/wager.html",
            {
                "wager": wager,
            }
        )
    else:
        try:
            bet_value = request.POST['bet_value']
        except KeyError:
            return render(
                request,
                "bet/wager.html",
                {
                    "wager": wager,
                }
            )
        else:
            bet = Bet(option=selected_option, user=request.user, value=bet_value)
            bet.save()
            return redirect(reverse('bet:home'))
