from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team
from .forms import TeamForm, PlayerForm

# Create your views here.
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

def team_list(request):
    teams = Team.objects.all()
    return render(request, "league/team_list.html", {"teams": teams})

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    return render(request, "league/team_detail.html", {"team": team})

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
    team = Team.objects.get(id=team_id, user=request.user)
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
