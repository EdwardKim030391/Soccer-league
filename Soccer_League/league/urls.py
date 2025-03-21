from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import (
    home_view, signup_view, your_team, team_list, team_detail,
    add_player, edit_player, delete_player, select_your_team, select_teams,change_team,
    simulate_matches, simulate_season, check_season_completion, start_new_season, dashboard, league_standings, match_list
)

urlpatterns = [
    path('', home_view, name='home'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", signup_view, name="signup"),

    path("your_team/", login_required(your_team), name="your_team"),
    path("select_your_team/<int:team_id>/", login_required(select_your_team), name="select_your_team"),
    path("select_teams/", login_required(select_teams), name="select_teams"),
    path("change_team/<int:team_id>/", login_required(change_team), name="change_team"),


    path("teams/", team_list, name="team_list"),
    path("teams/<int:team_id>/", team_detail, name="team_detail"),
    path("teams/<int:team_id>/add_player/", login_required(add_player), name="add_player"),
    path("players/<int:player_id>/edit/", login_required(edit_player), name="edit_player"),
    path("players/<int:player_id>/delete/", login_required(delete_player), name="delete_player"),


    path("matches/", login_required(match_list), name="match_list"),
    path("simulate_matches/<int:match_id>/", login_required(simulate_matches), name="simulate_matches"),
    path("simulate_season/", login_required(simulate_season), name="simulate_season"),
    path("season_status/", check_season_completion, name="season_status"),
    path("start_new_season/", start_new_season, name="start_new_season"),

    path("dashboard/", login_required(dashboard), name="dashboard"),
    path("standings/<int:league_id>/", login_required(league_standings), name="league_standings"),
]
