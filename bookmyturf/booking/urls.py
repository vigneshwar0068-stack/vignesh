from django.urls import path
from . import views
from . import tournament_views

urlpatterns = [

    # Main pages
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('turfs/', views.turfs, name='turfs'),
    path('booking/', views.booking, name='booking'),

    # Tournament URLs
    path('tournaments/', tournament_views.tournament_list, name='tournament_list'),
    path('tournaments/create/', tournament_views.tournament_create, name='tournament_create'),
    path('tournaments/<int:pk>/', tournament_views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:pk>/register/', tournament_views.tournament_register, name='tournament_register'),
    path('tournaments/<int:pk>/updates/', tournament_views.tournament_updates, name='tournament_updates'),
    path('tournaments/<int:pk>/score-dashboard/', tournament_views.score_dashboard, name='score_dashboard'),
    path('tournaments/<int:pk>/winner/', tournament_views.tournament_winner, name='tournament_winner'),  # ← NEW
    path('matches/<int:match_id>/update-score/', tournament_views.update_score, name='update_score'),
    path('players/<int:player_id>/stat/', tournament_views.update_player_stat, name='update_player_stat'),
]