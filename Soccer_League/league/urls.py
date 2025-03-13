from django.urls import path, include
from .views import (
    home_view, signup_view, team_list, team_detail, team_create, team_update,
    team_delete, add_player, select_teams, simulate_matches, simulate_season,
    dashboard, league_standings, match_list
)
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', home_view, name='home'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", signup_view, name="signup"),

    path("teams/", team_list, name="team_list"),
    path("teams/<int:team_id>/", team_detail, name="team_detail"),
    path("teams/create/", login_required(team_create), name="team_create"),
    path("teams/<int:team_id>/update/", login_required(team_update), name="team_update"),
    path("teams/<int:team_id>/delete/", login_required(team_delete), name="team_delete"),
    path("teams/<int:team_id>/add_player/", login_required(add_player), name="add_player"),

    path("matches/", login_required(match_list), name="match_list"),

    path("select_teams/", login_required(select_teams), name="select_teams"),
    path("simulate_matches/", login_required(simulate_matches), name="simulate_matches"),
    path("simulate_season/", login_required(simulate_season), name="simulate_season"),

    path("dashboard/", login_required(dashboard), name="dashboard"),
    path("standings/<int:league_id>/", login_required(league_standings), name="league_standings"),
]
