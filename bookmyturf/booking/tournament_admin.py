# booking/admin.py — add these lines to register tournament models

from django.contrib import admin
from .tournament_models import Tournament, Team, Player, Match

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1

class TeamInline(admin.TabularInline):
    model = Team
    extra = 0

class MatchInline(admin.TabularInline):
    model = Match
    extra = 0
    readonly_fields = ('updated_at',)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'sport', 'date', 'status', 'get_registered_teams_count')
    list_filter   = ('status', 'sport')
    inlines       = [TeamInline, MatchInline]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'captain', 'phone')
    inlines      = [PlayerInline]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'jersey_no', 'team', 'goals', 'assists')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'status', 'score_a', 'score_b', 'winner')
    list_filter  = ('status', 'tournament')