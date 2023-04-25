from django import forms
from .models import Crop


class CropForm(forms.ModelForm):

    # Define the fields to include in the form, including the new optional fields
    soil_type = forms.CharField(required=False)
    soil_pH_level = forms.FloatField(required=False)

    class Meta:
        model = Crop
        fields = ['crop', 'postal_code']

