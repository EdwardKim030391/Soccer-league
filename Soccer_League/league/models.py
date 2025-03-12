from django.db import models

from django.contrib.auth.models import User

class League(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams", null=True, blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    age = models.IntegerField(default=18)

    def __str__(self):
        return f"{self.name} ({self.position})"

class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    date = models.DateField()

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date}"
