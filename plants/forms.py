from django import forms
from .models import Plant, PlantPhoto


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = [
            'name', 'scientific_name', 'category', 'description',
            'image', 'location', 'status', 'light_need',
            'temperature', 'humidity', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'scientific_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'light_need': forms.TextInput(attrs={'class': 'form-control'}),
            'temperature': forms.TextInput(attrs={'class': 'form-control'}),
            'humidity': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PlantPhotoForm(forms.ModelForm):
    class Meta:
        model = PlantPhoto
        fields = ['image', 'caption']