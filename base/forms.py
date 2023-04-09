from django.db import models  
from django.forms import fields  
from .models import AthleteT  
from django import forms  
  
  
class AthleteForm(forms.ModelForm):  
    class Meta:  
        # To specify the model to be used to create form  
        model = AthleteT
        # It includes all the fields of model  
        fields = '__all__'  

class ImageForm(forms.ModelForm):
    class Meta:
        model = AthleteT
        fields = ['image']