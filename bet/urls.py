from django.urls import path

from . import views

app_name = "bet"
urlpatterns = [
    path('', views.WagerListView.as_view(), name="home"),
    path('wager/<int:wager_id>/', views.wager_view, name="wager"),
    path('wager/<int:wager_id>/place_bet/', views.place_bet, name="place_bet"),
    path('wager/<int:wager_id>/resolve/', views.resolve_wager_view, name="resolve_bet"),
    path('resolve/', views.resolve_wagers_view, name="multi_resolve_wager")
]