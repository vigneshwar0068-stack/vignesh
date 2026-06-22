import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .tournament_models import Tournament, Team, Player, Match


# ── Helper: build knockout bracket ────────────────────────────────────────

def generate_bracket(tournament):
    """
    Given a tournament with registered teams, create Match objects
    for a single-elimination bracket.
    """
    teams = list(tournament.teams.all())
    n = len(teams)

    # Calculate number of rounds needed
    rounds = math.ceil(math.log2(n))

    # Round 1 — seed teams into matches
    Match.objects.filter(tournament=tournament).delete()

    match_no = 1
    r1_matches = []
    for i in range(0, n, 2):
        team_a = teams[i]
        team_b = teams[i + 1] if i + 1 < n else None  # bye if odd team count
        m = Match.objects.create(
            tournament=tournament,
            round_no=1,
            match_no=match_no,
            team_a=team_a,
            team_b=team_b,
        )
        r1_matches.append(m)
        match_no += 1

    # Placeholder matches for subsequent rounds
    prev_round_count = len(r1_matches)
    for rnd in range(2, rounds + 1):
        next_count = math.ceil(prev_round_count / 2)
        for mn in range(1, next_count + 1):
            Match.objects.create(
                tournament=tournament,
                round_no=rnd,
                match_no=mn,
                team_a=None,
                team_b=None,
            )
        prev_round_count = next_count


def advance_winner(match):
    """
    After a match is completed, place the winner into the next round's
    correct slot automatically.
    """
    if not match.winner:
        return

    tournament = match.tournament
    next_round = match.round_no + 1
    next_match_no = math.ceil(match.match_no / 2)

    try:
        next_match = Match.objects.get(
            tournament=tournament,
            round_no=next_round,
            match_no=next_match_no,
        )
    except Match.DoesNotExist:
        return  # this was the final

    # Fill team_a or team_b slot
    if match.match_no % 2 == 1:
        next_match.team_a = match.winner
    else:
        next_match.team_b = match.winner
    next_match.save()


# ── Public views ───────────────────────────────────────────────────────────

def tournament_list(request):
    """All tournaments — upcoming, live, completed."""
    tournaments = Tournament.objects.all().order_by('-created_at')
    return render(request, 'tournament_list.html', {'tournaments': tournaments})


def tournament_detail(request, pk):
    """
    Live bracket view for a single tournament.
    The page polls /tournament/<pk>/updates/ every 5 seconds for score changes.
    """
    tournament = get_object_or_404(Tournament, pk=pk)
    teams      = tournament.teams.prefetch_related('players').all()
    matches    = tournament.matches.select_related('team_a', 'team_b', 'winner').all()

    # Group matches by round
    rounds = {}
    for m in matches:
        rounds.setdefault(m.round_no, []).append(m)

    # Player stats — top scorers across all teams
    all_players = Player.objects.filter(
        team__tournament=tournament
    ).order_by('-goals', '-assists')

    round_names = _round_names(tournament)

    return render(request, 'tournament_detail.html', {
        'tournament':  tournament,
        'teams':       teams,
        'rounds':      rounds,
        'all_players': all_players,
        'round_names': round_names,
    })


def tournament_updates(request, pk):
    """
    JSON endpoint polled every 5 sec by the live bracket page.
    Returns current scores + statuses for all matches.
    """
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.select_related('team_a', 'team_b', 'winner').all()

    data = {
        'tournament_status': tournament.status,
        'matches': [
            {
                'id':       m.id,
                'round':    m.round_no,
                'match_no': m.match_no,
                'team_a':   m.team_a.name if m.team_a else 'TBD',
                'team_b':   m.team_b.name if m.team_b else 'TBD',
                'score_a':  m.score_a,
                'score_b':  m.score_b,
                'status':   m.status,
                'winner':   m.winner.name if m.winner else None,
            }
            for m in matches
        ],
        'top_scorers': [
            {
                'name':    p.name,
                'team':    p.team.name,
                'jersey':  p.jersey_no,
                'goals':   p.goals,
                'assists': p.assists,
            }
            for p in Player.objects.filter(
                team__tournament=tournament
            ).order_by('-goals')[:10]
        ],
    }
    return JsonResponse(data)


# ── Registration ───────────────────────────────────────────────────────────

@login_required
def tournament_create(request):
    """Step 1 — create the tournament shell."""
    if request.method == 'POST':
        t = Tournament.objects.create(
            name       = request.POST.get('name'),
            sport      = request.POST.get('sport'),
            date       = request.POST.get('date'),
            venue      = request.POST.get('venue'),
            max_teams  = int(request.POST.get('max_teams', 8)),
            created_by = request.user,
        )
        return redirect('tournament_register', pk=t.pk)
    return render(request, 'tournament_create.html')


@login_required
def tournament_register(request, pk):
    """Step 2 — register a team + players for a tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if tournament.is_full():
        return render(request, 'tournament_full.html', {'tournament': tournament})

    if request.method == 'POST':
        team = Team.objects.create(
            tournament = tournament,
            name       = request.POST.get('team_name'),
            captain    = request.POST.get('captain_name'),
            phone      = request.POST.get('phone'),
        )

        # Dynamic player rows — form sends player_name_1, jersey_1, etc.
        i = 1
        while request.POST.get(f'player_name_{i}'):
            Player.objects.create(
                team      = team,
                name      = request.POST.get(f'player_name_{i}'),
                jersey_no = int(request.POST.get(f'jersey_{i}', i)),
            )
            i += 1

        # If tournament is now full, generate the bracket
        if tournament.is_full():
            generate_bracket(tournament)
            tournament.status = 'live'
            tournament.save()
            return redirect('tournament_detail', pk=tournament.pk)

        return redirect('tournament_detail', pk=tournament.pk)

    return render(request, 'tournament_register.html', {'tournament': tournament})


# ── Admin / score management ───────────────────────────────────────────────

@staff_member_required
def score_dashboard(request, pk):
    """Admin page to update match scores and player stats."""
    tournament = get_object_or_404(Tournament, pk=pk)
    matches    = tournament.matches.select_related('team_a', 'team_b').all()
    return render(request, 'score_dashboard.html', {
        'tournament': tournament,
        'matches':    matches,
    })


# ─────────────────────────────────────────────────────────────────────────────
# REPLACE your existing update_score function in tournament_views.py
# with this updated version. It redirects to winner page after final match.
# ─────────────────────────────────────────────────────────────────────────────

@staff_member_required
@require_POST
def update_score(request, match_id):
    """AJAX POST — update a match score."""
    match   = get_object_or_404(Match, pk=match_id)
    score_a = int(request.POST.get('score_a', 0))
    score_b = int(request.POST.get('score_b', 0))
    status  = request.POST.get('status', 'live')

    match.score_a = score_a
    match.score_b = score_b
    match.status  = status

    if status == 'completed':
        if score_a > score_b:
            match.winner = match.team_a
        elif score_b > score_a:
            match.winner = match.team_b
        match.save()
        advance_winner(match)

        # Check if all matches done
        remaining = Match.objects.filter(
            tournament=match.tournament,
            status__in=['scheduled', 'live']
        ).count()

        if remaining == 0:
            match.tournament.status = 'completed'
            match.tournament.save()

        # ── Check if THIS was the final match ──
        # Final = no next round exists
        next_round = match.round_no + 1
        is_final = not Match.objects.filter(
            tournament=match.tournament,
            round_no=next_round
        ).exists()

        if is_final and match.winner:
            # Tell the score dashboard JS to redirect
            return JsonResponse({
                'ok':          True,
                'winner':      match.winner.name,
                'is_final':    True,
                'redirect_url': f'/tournaments/{match.tournament.pk}/winner/',
            })
    else:
        match.save()

    return JsonResponse({
        'ok':       True,
        'winner':   match.winner.name if match.winner else None,
        'is_final': False,
    })

@staff_member_required
@require_POST
def update_player_stat(request, player_id):
    """AJAX POST — increment a player's goals or assists."""
    player  = get_object_or_404(Player, pk=player_id)
    stat    = request.POST.get('stat')   # 'goals' or 'assists'
    action  = request.POST.get('action') # 'add' or 'remove'

    if stat == 'goals':
        player.goals = max(0, player.goals + (1 if action == 'add' else -1))
    elif stat == 'assists':
        player.assists = max(0, player.assists + (1 if action == 'add' else -1))
    player.save()

    return JsonResponse({'goals': player.goals, 'assists': player.assists})


# ── Utility ────────────────────────────────────────────────────────────────

def _round_names(tournament):
    """Map round numbers to display names based on total teams."""
    n      = tournament.teams.count()
    rounds = max(1, math.ceil(math.log2(max(n, 2))))
    names  = {}
    for r in range(1, rounds + 1):
        remaining = rounds - r
        if remaining == 0:
            names[r] = 'Final'
        elif remaining == 1:
            names[r] = 'Semi-Final'
        elif remaining == 2:
            names[r] = 'Quarter-Final'
        else:
            names[r] = f'Round {r}'
    return names


# ── Winner page ────────────────────────────────────────────────────────────

def tournament_winner(request, pk):
    """
    Show the celebration page for a completed tournament.
    Finds the final match, the winner team, top scorers, total goals.
    """
    from django.db.models import Sum

    tournament = get_object_or_404(Tournament, pk=pk)

    # Final match = highest round number, match 1
    final_match = Match.objects.filter(
        tournament=tournament
    ).order_by('-round_no', 'match_no').first()

    winner = final_match.winner if final_match else None

    # Top 3 scorers across entire tournament
    top_scorers = Player.objects.filter(
        team__tournament=tournament,
        goals__gt=0
    ).order_by('-goals', '-assists')[:3]

    # Total goals in tournament
    total_goals = Match.objects.filter(
        tournament=tournament,
        status='completed'
    ).aggregate(
        total=Sum('score_a') + Sum('score_b')
    )['total'] or 0

    return render(request, 'winner.html', {
        'tournament':  tournament,
        'final_match': final_match,
        'winner':      winner,
        'top_scorers': top_scorers,
        'total_goals': total_goals,
    })