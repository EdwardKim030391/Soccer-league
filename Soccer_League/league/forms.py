from django import forms
from .models import Team, Player, SelectedTeam

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "league"]

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["name", "position", "age"]

class TeamSelectionForm(forms.Form):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select 19 Teams"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teams'].queryset = Team.objects.all()

    def clean_teams(self):
        selected_teams = self.cleaned_data.get("teams")
        if len(selected_teams) != 19:
            raise forms.ValidationError("You must select exactly 19 teams.")
        return selected_teams
