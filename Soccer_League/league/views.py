from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team, SelectedTeam, Match, League, Player
from .forms import PlayerForm
from datetime import datetime, timedelta
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Q
import random

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
def your_team(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    return render(request, "league/your_team.html", {
        "selected_team": selected_team,
    })

@login_required
def select_team(request):
    leagues = League.objects.prefetch_related("teams").all()

    if request.method == "POST":
        team_id = request.POST.get("team")
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            SelectedTeam.objects.update_or_create(user=request.user, defaults={"team": team})

        return redirect("your_team")

    return render(request, "league/select_team.html", {"leagues": leagues})

def team_list(request):
    leagues = League.objects.prefetch_related("teams").all()
    return render(request, "league/team_list.html", {"leagues": leagues})

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all()
    return render(request, "league/team_detail.html", {
        "team": team,
        "players": players,
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

def match_list(request):
    matches = Match.objects.all().order_by("date")
    return render(request, "league/match_list.html", {"matches": matches})

def generate_matches(user):
    selected_team = SelectedTeam.objects.filter(user=user).first()
    if not selected_team:
        return

    teams = list(Team.objects.filter(league=selected_team.team.league))

    match_date = datetime.today()
    for i in range(len(teams) - 1):
        for j in range(i + 1, len(teams)):
            Match.objects.create(
                league=selected_team.team.league,
                home_team=teams[i],
                away_team=teams[j],
                date=match_date
            )
            match_date += timedelta(days=3)

@login_required
def simulate_matches(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    if not selected_team:
        return JsonResponse({"error": "No team selected"}, status=400)

    matches = Match.objects.filter(completed=False).filter(
        Q(home_team=selected_team.team) | Q(away_team=selected_team.team)
    )

    for match in matches:
        match.home_score = random.randint(0, 5)
        match.away_score = random.randint(0, 5)
        match.completed = True
        match.save()

    return JsonResponse({"message": "Simulation completed!"})

@login_required
def simulate_season(request):
    simulate_matches(request)
    return redirect('match_list')

def calculate_standings(league):
    standings = defaultdict(lambda: {"team": None, "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals": 0})

    matches = Match.objects.filter(league=league, completed=True)

    for match in matches:
        home_team = match.home_team
        away_team = match.away_team

        standings[home_team.id]["team"] = home_team
        standings[away_team.id]["team"] = away_team

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

    sorted_standings = sorted(standings.values(), key=lambda x: -x["points"])

    return sorted_standings

def league_standings(request, league_id):
    league = League.objects.get(id=league_id)
    standings = calculate_standings(league)

    return render(request, "league/standings.html", {"standings": standings, "league": league})
