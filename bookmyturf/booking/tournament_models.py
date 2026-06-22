from django.db import models
from django.contrib.auth.models import User


class Tournament(models.Model):
    SPORT_CHOICES = [
        ('football-5v5',   'Football 5v5'),
        ('football-10v10', 'Football 10v10'),
        ('futsal',         'Futsal'),
        ('snooker',        'Snooker'),
        ('carrom',         'Carrom'),
        ('ping-pong',      'Ping Pong'),
    ]
    STATUS_CHOICES = [
        ('upcoming',    'Upcoming'),
        ('live',        'Live'),
        ('completed',   'Completed'),
    ]

    name        = models.CharField(max_length=200)
    sport       = models.CharField(max_length=20, choices=SPORT_CHOICES)
    date        = models.DateField()
    venue       = models.CharField(max_length=200, default='BookMyTurf Arena')
    max_teams   = models.IntegerField(default=8)   # must be power of 2: 4, 8, 16
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_registered_teams_count(self):
        return self.teams.count()

    def is_full(self):
        return self.teams.count() >= self.max_teams


class Team(models.Model):
    tournament  = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name        = models.CharField(max_length=100)
    captain     = models.CharField(max_length=100)
    phone       = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"


class Player(models.Model):
    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    name        = models.CharField(max_length=100)
    jersey_no   = models.IntegerField()
    goals       = models.IntegerField(default=0)
    assists     = models.IntegerField(default=0)

    class Meta:
        ordering = ['jersey_no']

    def __str__(self):
        return f"#{self.jersey_no} {self.name} ({self.team.name})"


class Match(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live',      'Live'),
        ('completed', 'Completed'),
    ]

    tournament  = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_no    = models.IntegerField()       # 1 = QF, 2 = SF, 3 = Final
    match_no    = models.IntegerField()       # position in that round
    team_a      = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_a')
    team_b      = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_b')
    score_a     = models.IntegerField(default=0)
    score_b     = models.IntegerField(default=0)
    winner      = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['round_no', 'match_no']

    def __str__(self):
        a = self.team_a.name if self.team_a else 'TBD'
        b = self.team_b.name if self.team_b else 'TBD'
        return f"R{self.round_no}M{self.match_no}: {a} vs {b}"