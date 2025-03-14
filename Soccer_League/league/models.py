from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class League(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")

    def average_skill_rating(self):
        avg_rating = self.players.aggregate(
            speed=Avg('speed'),
            shooting=Avg('shooting'),
            passing=Avg('passing'),
            defense=Avg('defense'),
            stamina=Avg('stamina')
        )
        return {key: avg_rating.get(key, 0) or 0 for key in avg_rating}

    def __str__(self):
        return self.name


class Player(models.Model):
    POSITION_CHOICES = [
        ('FW', 'Forward'),
        ('MF', 'Midfielder'),
        ('DF', 'Defender'),
        ('GK', 'Goalkeeper'),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)

    speed = models.IntegerField(default=50)
    shooting = models.IntegerField(default=50)
    passing = models.IntegerField(default=50)
    defense = models.IntegerField(default=50)
    stamina = models.IntegerField(default=50)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    age = models.IntegerField(default=18)

    def overall_rating(self):
        return round((self.speed + self.shooting + self.passing + self.defense + self.stamina) / 5)

    def __str__(self):
        return f"{self.name} ({self.position}) - OVR: {self.overall_rating()}"


class SelectedTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="selected_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"


class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")

    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date}"
