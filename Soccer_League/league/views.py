from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team, SelectedTeam, Match, League, Player
from .forms import PlayerForm, TeamSelectionForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.http import JsonResponse
import random
from collections import defaultdict

def home_view(request):
    return render(request, 'league/home.html')

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def dashboard(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    matches = Match.objects.filter(
        Q(home_team=selected_team.team) | Q(away_team=selected_team.team)
    ) if selected_team else []

    return render(request, 'league/dashboard.html', {
        'selected_team': selected_team,
        'matches': matches
    })

@login_required
def your_team(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()

    if not selected_team:
        print("DEBUG: No selected team found for user:", request.user.username)
    else:
        print("DEBUG: Selected team:", selected_team.team.name, "League:", selected_team.team.league.id)

    return render(request, "league/your_team.html", {
        "selected_team": selected_team,
    })

@login_required
def select_your_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    selected_team, created = SelectedTeam.objects.update_or_create(
        user=request.user, defaults={"team": team}
    )

    return redirect("your_team")

@login_required
def select_teams(request):
    leagues = League.objects.prefetch_related("teams").all()
    selected_team = SelectedTeam.objects.filter(user=request.user).first()

    if not selected_team:
        return redirect("team_list")

    if request.method == "POST":
        selected_team_ids = request.POST.getlist("teams")

        if len(selected_team_ids) != 19:
            return render(request, "league/select_teams.html", {
                "leagues": leagues,
                "error": "You must select exactly 19 teams.",
                "selected_team": selected_team.team
            })

        Match.objects.filter(league=selected_team.team.league).delete()
        selected_teams = [selected_team.team.id] + list(map(int, selected_team_ids))
        generate_league_matches(selected_team.team.league, selected_teams)

        return redirect("match_list")

    return render(request, "league/select_teams.html", {
        "leagues": leagues,
        "selected_team": selected_team.team
    })

def team_list(request):
    leagues = League.objects.prefetch_related("teams").all()
    return render(request, "league/team_list.html", {"leagues": leagues})

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all()
    avg_ratings = team.average_skill_rating()

    return render(request, "league/team_detail.html", {
        "team": team,
        "players": players,
        "avg_ratings": avg_ratings
    })

@login_required
def add_player(request, team_id):
    selected_team = SelectedTeam.objects.filter(user=request.user, team_id=team_id).first()
    if not selected_team:
        return redirect("team_detail", team_id=team_id)

    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.team = selected_team.team
            player.save()
            return redirect("team_detail", team_id=team_id)
    else:
        form = PlayerForm()

    return render(request, "league/add_player.html", {"form": form, "team": selected_team.team})

@login_required
def edit_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect("team_detail", team_id=player.team.id)
    else:
        form = PlayerForm(instance=player)

    return render(request, "league/edit_player.html", {"form": form, "player": player})

@login_required
def delete_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    selected_team = SelectedTeam.objects.filter(user=request.user).first()

    if not selected_team or selected_team.team != player.team:
        return redirect("team_detail", team_id=player.team.id)

    if request.method == "POST":
        player.delete()
        return redirect("team_detail", team_id=player.team.id)

    return render(request, "league/delete_player.html", {"player": player})

def match_list(request):
    matches = Match.objects.all().order_by("date")
    return render(request, "league/match_list.html", {"matches": matches})

def generate_league_matches(league, teams):
    match_date = timezone.now().date()
    total_teams = len(teams)

    if total_teams % 2 != 0:
        teams.append(None)

    for round_number in range(total_teams - 1):
        for i in range(total_teams // 2):
            home_team = teams[i]
            away_team = teams[-(i + 1)]

            if home_team and away_team:
                Match.objects.create(
                    league=league,
                    home_team_id=home_team,
                    away_team_id=away_team,
                    date=match_date
                )

        teams.insert(1, teams.pop())
        match_date += timedelta(days=7)

@login_required
def simulate_matches(request, match_id):
    match = get_object_or_404(Match, id=match_id, completed=False)

    home_team = match.home_team
    away_team = match.away_team

    home_avg = home_team.average_skill_rating() or {}
    away_avg = away_team.average_skill_rating() or {}

    home_avg = {key: home_avg.get(key, 50) for key in ["speed", "shooting", "passing", "defense", "stamina"]}
    away_avg = {key: away_avg.get(key, 50) for key in ["speed", "shooting", "passing", "defense", "stamina"]}

    home_attack = (home_avg["shooting"] + home_avg["passing"]) / 2
    away_attack = (away_avg["shooting"] + away_avg["passing"]) / 2
    home_defense = (home_avg["defense"] + home_avg["stamina"]) / 2
    away_defense = (away_avg["defense"] + away_avg["stamina"]) / 2

    home_score = max(0, int(random.gauss(home_attack - away_defense + 2, 1.5)))
    away_score = max(0, int(random.gauss(away_attack - home_defense + 2, 1.5)))

    match.home_score = home_score
    match.away_score = away_score
    match.completed = True
    match.save()

    return JsonResponse({"message": f"Match {match_id} simulated!"})

@login_required
def simulate_season(request):
    simulate_matches(request)
    return redirect('match_list')

def calculate_standings(league):
    standings = {}

    matches = Match.objects.filter(league=league, completed=True)

    for match in matches:
        home_team = match.home_team
        away_team = match.away_team

        if home_team.id not in standings:
            standings[home_team.id] = {"team": home_team, "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_scored": 0, "goals_conceded": 0, "goal_difference": 0}
        if away_team.id not in standings:
            standings[away_team.id] = {"team": away_team, "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_scored": 0, "goals_conceded": 0, "goal_difference": 0}

        standings[home_team.id]["goals_scored"] += match.home_score
        standings[home_team.id]["goals_conceded"] += match.away_score
        standings[away_team.id]["goals_scored"] += match.away_score
        standings[away_team.id]["goals_conceded"] += match.home_score

        standings[home_team.id]["goal_difference"] = standings[home_team.id]["goals_scored"] - standings[home_team.id]["goals_conceded"]
        standings[away_team.id]["goal_difference"] = standings[away_team.id]["goals_scored"] - standings[away_team.id]["goals_conceded"]

        if match.home_score > match.away_score:
            standings[home_team.id]["points"] += 3
            standings[home_team.id]["wins"] += 1
            standings[away_team.id]["losses"] += 1
        elif match.home_score < match.away_score:
            standings[away_team.id]["points"] += 3
            standings[away_team.id]["wins"] += 1
            standings[home_team.id]["losses"] += 1
        else:
            standings[home_team.id]["points"] += 1
            standings[away_team.id]["points"] += 1
            standings[home_team.id]["draws"] += 1
            standings[away_team.id]["draws"] += 1

    sorted_standings = sorted(
        standings.values(),
        key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_scored"])
    )

    return sorted_standings

@login_required
def league_standings(request, league_id):
    league = get_object_or_404(League, id=league_id)
    standings = calculate_standings(league)

    return render(request, "league/league_standings.html", {"standings": standings, "league": league})

def base_context(request):
    selected_team = None
    if request.user.is_authenticated:
        selected_team = SelectedTeam.objects.filter(user=request.user).first()
    return {"selected_team": selected_team}

@login_required
def change_team(request, team_id):
    new_team = get_object_or_404(Team, id=team_id)

    selected_team, created = SelectedTeam.objects.update_or_create(
        user=request.user, defaults={"team": new_team}
    )

    return redirect("your_team")
