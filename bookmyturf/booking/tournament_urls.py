# Add these URL patterns to your booking/urls.py
# (or include this file from your main urls.py)

from django.urls import path
from . import tournament_views

urlpatterns = [
    path('tournaments/',                          tournament_views.tournament_list,     name='tournament_list'),
    path('tournaments/create/',                   tournament_views.tournament_create,   name='tournament_create'),
    path('tournaments/<int:pk>/',                 tournament_views.tournament_detail,   name='tournament_detail'),
    path('tournaments/<int:pk>/register/',        tournament_views.tournament_register, name='tournament_register'),
    path('tournaments/<int:pk>/updates/',         tournament_views.tournament_updates,  name='tournament_updates'),
    path('tournaments/<int:pk>/score-dashboard/', tournament_views.score_dashboard,     name='score_dashboard'),
    path('matches/<int:match_id>/update-score/',  tournament_views.update_score,        name='update_score'),
    path('players/<int:player_id>/stat/',         tournament_views.update_player_stat,  name='update_player_stat'),
    path('tournaments/<int:pk>/winner/',          tournament_views.tournament_winner,    name='tournament_winner'),
]