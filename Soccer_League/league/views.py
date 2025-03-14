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

# 홈 페이지
def home_view(request):
    return render(request, 'league/home.html')

# 회원가입 뷰
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

# 대시보드 - 유저의 경기 정보 보기
@login_required
def dashboard(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    matches = Match.objects.filter(
        Q(home_team=selected_team.team) | Q(away_team=selected_team.team)
    ) if selected_team else []

    return render(request, 'league/dashboard.html', {'selected_team': selected_team, 'matches': matches})

# 유저가 선택한 팀 보기
@login_required
def your_team(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    return render(request, "league/your_team.html", {
        "selected_team": selected_team,
    })

# 유저가 자신의 팀을 선택하는 기능
@login_required
def select_your_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # 기존 선택 팀이 있다면 업데이트
    selected_team, created = SelectedTeam.objects.update_or_create(
        user=request.user, defaults={"team": team}
    )

    return redirect("your_team")

# 리그에서 19개의 추가 팀을 선택하는 기능
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

        # 기존 경기 삭제 후 새롭게 리그 경기 생성
        Match.objects.filter(league=selected_team.team.league).delete()
        selected_teams = [selected_team.team.id] + list(map(int, selected_team_ids))
        generate_league_matches(selected_team.team.league, selected_teams)

        return redirect("match_list")

    return render(request, "league/select_teams.html", {
        "leagues": leagues,
        "selected_team": selected_team.team
    })

# 팀 목록 보기
def team_list(request):
    leagues = League.objects.prefetch_related("teams").all()
    return render(request, "league/team_list.html", {"leagues": leagues})

# 팀 상세 페이지
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

# 선수 추가
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

# 선수 수정
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

# 경기 일정
def match_list(request):
    matches = Match.objects.all().order_by("date")
    return render(request, "league/match_list.html", {"matches": matches})

# 리그 경기 생성
def generate_league_matches(league, teams):
    match_date = timezone.now().date()

    for i in range(len(teams) - 1):
        for j in range(i + 1, len(teams)):
            Match.objects.create(
                league=league,
                home_team_id=teams[i],
                away_team_id=teams[j],
                date=match_date
            )
            match_date += timedelta(days=3)

# 경기 시뮬레이션
@login_required
def simulate_matches(request):
    selected_team = SelectedTeam.objects.filter(user=request.user).first()
    if not selected_team:
        return JsonResponse({"error": "You must select a team first."}, status=400)

    matches = Match.objects.filter(completed=False).filter(
        Q(home_team=selected_team.team) | Q(away_team=selected_team.team)
    )

    for match in matches:
        home_team = match.home_team
        away_team = match.away_team

        home_avg = home_team.average_skill_rating() or {}
        away_avg = away_team.average_skill_rating() or {}

        home_score = max(0, int(random.gauss(home_avg.get("shooting", 50) - away_avg.get("defense", 50) + 2, 1.5)))
        away_score = max(0, int(random.gauss(away_avg.get("shooting", 50) - home_avg.get("defense", 50) + 2, 1.5)))

        match.home_score = home_score
        match.away_score = away_score
        match.completed = True
        match.save()

    return JsonResponse({"message": "Simulation completed!"})

@login_required
def simulate_season(request):
    simulate_matches(request)
    return redirect('match_list')

# 리그 순위 계산
def calculate_standings(league):
    standings = defaultdict(lambda: {
        "team": None, "points": 0, "wins": 0, "draws": 0, "losses": 0,
        "goals_scored": 0, "goals_conceded": 0, "goal_difference": 0
    })

    matches = Match.objects.filter(league=league, completed=True)

    for match in matches:
        home_team = match.home_team
        away_team = match.away_team

        standings[home_team.id]["team"] = home_team
        standings[away_team.id]["team"] = away_team

        if match.home_score > match.away_score:
            standings[home_team.id]["points"] += 3
            standings[home_team.id]["wins"] += 1
        elif match.home_score < match.away_score:
            standings[away_team.id]["points"] += 3
            standings[away_team.id]["wins"] += 1
        else:
            standings[home_team.id]["points"] += 1
            standings[away_team.id]["points"] += 1
            standings[home_team.id]["draws"] += 1
            standings[away_team.id]["draws"] += 1

    return sorted(standings.values(), key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_scored"]))

# 리그 순위 페이지
def league_standings(request, league_id):
    league = get_object_or_404(League, id=league_id)
    standings = calculate_standings(league)
    return render(request, "league/standings.html", {"standings": standings, "league": league})
