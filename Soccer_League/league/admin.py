from django.contrib import admin
from .models import League, Team, Player, Match, UserTeam, SelectedTeam

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "league")
    list_filter = ("league",)
    search_fields = ("name",)

@admin.register(UserTeam)
class UserTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "league", "user")
    list_filter = ("league",)
    search_fields = ("name", "user__username")

@admin.register(SelectedTeam)
class SelectedTeamAdmin(admin.ModelAdmin):
    list_display = ("user", "team")
    list_filter = ("team",)
    search_fields = ("user__username", "team__name")

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "age", "team")
    list_filter = ("team", "position")
    search_fields = ("name",)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("league", "home_team", "away_team", "home_score", "away_score", "date", "completed")
    list_filter = ("league", "date", "completed")
    search_fields = ("home_team__name", "away_team__name")
