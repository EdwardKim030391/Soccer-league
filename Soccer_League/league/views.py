from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team, SelectedTeam, UserTeam, Match, League, Player
from .forms import TeamForm, PlayerForm, TeamSelectionForm
from datetime import datetime, timedelta
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Q

import random

# Create your views here.
def home_view(request):
    return render(request, 'league/home.html')

def dashboard(request):
    selected_teams = SelectedTeam.objects.filter(user=request.user).values_list('team', flat=True)

    matches = Match.objects.filter(
        Q(home_team__in=selected_teams) | Q(away_team__in=selected_teams)
    )

    return render(request, 'league/dashboard.html', {'selected_teams': selected_teams, 'matches': matches})

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
    leagues = League.objects.all()
    user_team = UserTeam.objects.filter(user=request.user)  # ✅ 유저가 만든 팀만 가져오기

    # ✅ 리그별 팀 목록을 딕셔너리 형태로 저장
    league_teams = {}
    for league in leagues:
        league_teams[league.id] = Team.objects.filter(league=league)

    return render(request, "league/your_team.html", {
        "leagues": leagues,
        "user_team": user_team,
        "league_teams": league_teams  # ✅ 딕셔너리 전달
    })

@login_required
def select_teams(request):
    leagues = League.objects.prefetch_related("league_teams").all()

    if request.method == "POST":
        selected_teams = request.POST.getlist("teams")

        # 기존 선택한 팀 삭제
        SelectedTeam.objects.filter(user=request.user).delete()

        # 최대 19개 팀 선택
        for team_id in selected_teams[:19]:
            team = get_object_or_404(Team, id=team_id)
            SelectedTeam.objects.create(user=request.user, team=team)

        return redirect("your_team")

    return render(request, "league/select_teams.html", {"leagues": leagues})


@login_required
def team_list(request):
    leagues = League.objects.prefetch_related("league_teams").all()
    user_teams = UserTeam.objects.filter(user=request.user)
    return render(request, "league/team_list.html", {"leagues": leagues, "user_teams": user_teams})


@login_required
def team_detail(request, team_id):

    user_team = UserTeam.objects.filter(id=team_id, user=request.user).first()
    if user_team:
        is_user_team = True
        team = user_team
    else:
        is_user_team = False
        team = get_object_or_404(Team, id=team_id)

    players = team.players.all()

    return render(request, "league/team_detail.html", {
        "team": team,
        "players": players,
        "is_user_team": is_user_team
    })

@login_required
def team_create(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.user = request.user
            team.save()
            return redirect("team_list")
    else:
        form = TeamForm()
    return render(request, "league/team_form.html", {"form": form})

@login_required
def team_update(request, team_id):
    team = get_object_or_404(Team, id=team_id, user=request.user)
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect("team_detail", team_id=team.id)
    else:
        form = TeamForm(instance=team)
    return render(request, "league/team_form.html", {"form": form})

@login_required
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id, user=request.user)
    if request.method == "POST":
        team.delete()
        return redirect("team_list")
    return render(request, "league/team_confirm_delete.html", {"team": team})

@login_required
def add_player(request, team_id):
    team = get_object_or_404(UserTeam, id=team_id, user=request.user)

    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.team = team
            player.save()
            return redirect("team_list")
    else:
        form = PlayerForm()

    return render(request, "league/add_player.html", {"form": form, "team": team})

def match_list(request):
    matches = Match.objects.all().order_by("date")
    return render(request, "league/match_list.html", {"matches": matches})

def generate_matches(user):
    user_team = UserTeam.objects.get(user=user)
    selected_teams = SelectedTeam.objects.filter(user=user).values_list('team', flat=True)
    teams = list(selected_teams) + [user_team.id]

    match_date = timezone.now().date()

    for i in range(len(teams) - 1):
        for j in range(i + 1, len(teams)):
            Match.objects.create(
                league=user_team.league,
                home_team_id=teams[i],
                away_team_id=teams[j],
                date=match_date
            )
            match_date += timedelta(days=3)

def simulate_matches(request):
    selected_teams = SelectedTeam.objects.filter(user=request.user).values_list('team', flat=True)

    matches = Match.objects.filter(completed=False).filter(home_team__in=selected_teams) | Match.objects.filter(completed=False).filter(away_team__in=selected_teams)

    for match in matches:
        match.home_score = random.randint(0, 5)
        match.away_score = random.randint(0, 5)
        match.completed = True
        match.save()

    return JsonResponse({"message": "Simulation completed!"})

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
