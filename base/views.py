from django.shortcuts import render, redirect
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import get_plot

def Dashboard(request):

    context = {}

    return render(request, 'html/dashboard.html', context)

def AthletesDash(request):

    athletes = AthleteT.objects.all()

    context = {
        'athletes':athletes
    }
    
    return render(request, 'html/athletes.html', context)

def AthleteProf(request, fname, lname, dob):

    athleteProf = AthleteT.objects.get(fname=fname)
    wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).values()
    kpi = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values()
    name = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values_list('testtype', flat=True).distinct()

    context = {
        'athleteProf':athleteProf,
        'wellness':wellness,
        'kpi':kpi,
        'name':name
    }
    
    return render(request, 'html/athleteProf.html', context)


def TeamDash(request):

    athletes = TeamT.objects.all()

    context = {
        'teams':athletes
    }
    
    return render(request, 'html/teams.html', context)

def CreateDash(request):

    context = {}

    return render(request, 'html/create.html', context)

def AnalyzeDash(request):

    athletes = AthleteT.objects.all()
    x = [x.height for x in athletes]
    y = [y.weight for y in athletes]

    chart = get_plot(x,y)

    context = {
        'chart':chart
    }

    return render(request, 'html/analyze.html', context)

