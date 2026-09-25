from django import forms
from .models import CareSchedule, CareLog, CareType


class CareScheduleForm(forms.ModelForm):
    class Meta:
        model = CareSchedule
        fields = ['care_type', 'frequency', 'interval_days',
                  'start_date', 'end_date', 'time_of_day', 'notes']
        widgets = {
            'care_type': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'interval_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_of_day': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CareLogForm(forms.ModelForm):
    class Meta:
        model = CareLog
        fields = ['care_type', 'performed_at', 'amount', 'product', 'note', 'image']
        widgets = {
            'care_type': forms.Select(attrs={'class': 'form-select'}),
            'performed_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'amount': forms.TextInput(attrs={'class': 'form-control'}),
            'product': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }