from django import forms
from .models import Player, SelectedTeam, Team

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["name", "position", "age", "speed", "shooting", "passing", "defense", "stamina"]

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age < 16 or age > 40:
            raise forms.ValidationError("Age must be between 16 and 40.")
        return age

    def clean_speed(self):
        return self.validate_stat("speed")

    def clean_shooting(self):
        return self.validate_stat("shooting")

    def clean_passing(self):
        return self.validate_stat("passing")

    def clean_defense(self):
        return self.validate_stat("defense")

    def clean_stamina(self):
        return self.validate_stat("stamina")

    def validate_stat(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value < 0 or value > 100:
            raise forms.ValidationError(f"{field_name.capitalize()} must be between 0 and 100.")
        return value


class TeamSelectionForm(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.RadioSelect,
        label="Select Your Team"
    )

    class Meta:
        model = SelectedTeam
        fields = ["team"]

