from django.db import models  
from django.forms import fields  
from .models import AthleteT, TeamT
from django import forms  
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

  
class AthleteForm(forms.ModelForm):  
    DEFAULT = ''
    FRESHMAN = 'Freshman'
    SOPHOMORE = 'Sophomore'
    JUNIOR = 'Junior'
    SENIOR = 'Senior'
    SCHOOL_YEARS = [
        (DEFAULT, ('')),
        (FRESHMAN, ('Freshman')),
        (SOPHOMORE, ('Sophomore')),
        (JUNIOR, ('Junior')),
        (SENIOR, ('Senior')),
    ]

    MALE = 'M'
    FEMALE = 'F'
    GENDER = [
        (DEFAULT, ('')),
        (MALE, ('M')),
        (FEMALE, ('F')),
    ]

    TEAMS = [
        (DEFAULT, ('')),
    ]
    SportsTeams = TeamT.objects.all()
    for x in SportsTeams:
        TEAMS.append((x.sport, (str(x.sport))),)

    fname = forms.CharField(max_length=30, required=True)
    lname = forms.CharField(max_length=30, required=True)
    year = forms.ChoiceField(widget=forms.Select, choices=SCHOOL_YEARS)
    dob = forms.DateField(required=True)
    height = forms.CharField(max_length=15, required=True)
    gender = forms.ChoiceField(widget=forms.Select, choices=GENDER)
    image = forms.FileField(required=False)
    sportsteam = forms.ChoiceField(widget=forms.Select, choices=TEAMS)
    position = forms.CharField(max_length=30, required=True)

    class Meta:  
        # To specify the model to be used to create form  
        model = AthleteT
        # It includes all the fields of model  
        fields = ("fname", "lname", "year", "dob", "height", "gender", "image", "sportsteam", "position")  

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

class UpdateUserForm(PasswordChangeForm):
    #first_name = forms.CharField(max_length=50, required=True)
    #last_name = forms.CharField(max_length=50, required=True)
    #username = forms.CharField(max_length=50, required=True)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "old_password", "new_password1", "new_password2")