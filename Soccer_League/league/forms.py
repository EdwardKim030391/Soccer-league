from django import forms
from .models import Player, SelectedTeam, Team

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["name", "position", "age", "speed", "shooting", "passing", "defense", "stamina"]

class TeamSelectionForm(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.RadioSelect,
        label="Select Your Team"
    )

    class Meta:
        model = SelectedTeam
        fields = ["team"]
