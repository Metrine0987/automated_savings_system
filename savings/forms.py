from django import forms
from .models import SavingsGoal
from .models import RecurringSavings

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'current_amount']


class RecurringSavingsForm(forms.ModelForm):
    class Meta:
        model = RecurringSavings
        fields = ['goal', 'amount', 'frequency', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
