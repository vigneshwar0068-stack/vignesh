from django.contrib import admin
from .models import Booking
from .tournament_models import Tournament, Team, Player, Match

admin.site.register(Booking)
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)