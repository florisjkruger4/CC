from django.db import models  
from django.forms import fields  
from .models import AthleteT
from django import forms  
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
  
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

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")