from django.urls import path, include
from .views import home_view, signup_view, team_list, team_detail, team_create, team_update, team_delete, add_player

urlpatterns = [
    path('', home_view, name='home'),
    path("accounts/", include("django.contrib.auth.urls")),
     path("accounts/signup/", signup_view, name="signup"),
    path("teams/", team_list, name="team_list"),
    path("teams/<int:team_id>/", team_detail, name="team_detail"),
    path("teams/create/", team_create, name="team_create"),
    path("teams/<int:team_id>/update/", team_update, name="team_update"),
    path("teams/<int:team_id>/delete/", team_delete, name="team_delete"),
    path("teams/<int:team_id>/add_player/", add_player, name="add_player"),
]
