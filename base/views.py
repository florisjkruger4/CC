from django.shortcuts import render, redirect
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import bar_graph, line_graph
from django.db.models import Count

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

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)
    wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).values()

    # Groups by test type name for specific athlete profile page
    testType = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values('testtype').annotate(dcount=Count('testtype')).order_by('testtype')

    all_dates = KpiT.objects.filter(fname=fname, lname=lname, dob=dob)

    # Gets the rows for 10yd Sprint for specific athlete
    TenYdSprint_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='10yd Sprint')
    # Gets dates for 10yd Sprint tests for specific athlete
    TenYdSprint_dates = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='10yd Sprint').distinct()
    # Sets x and y coordinate values
    TenYd_x = [x.datekpi for x in TenYdSprint_results]
    TenYd_y = [x.testresult for x in TenYdSprint_results]
    # Calls matplotlib bar graph with above data
    TenYd_chart = bar_graph(TenYd_x, TenYd_y)

    # Gets the rows for Barbell Bench Press 1RM for specific athlete
    Bench1RM_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='Barbell Bench Press 1RM')
    # Sets x and y coordinate values
    Bench1RM_x = [x.datekpi for x in Bench1RM_results]
    Bench1RM_y = [y.testresult for y in Bench1RM_results]
    # Calls matplotlib bar graph with above data
    Bench1RM_chart = bar_graph(Bench1RM_x, Bench1RM_y)

    # Gets the rows for CMJ for specific athlete
    CMJ_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='CMJ')
    # Sets x and y coordinate values
    CMJ_x = [x.datekpi for x in CMJ_results]
    CMJ_y = [y.testresult for y in CMJ_results]
    # Calls matplotlib bar graph with above data
    CMJ_chart = bar_graph(CMJ_x, CMJ_y)
    

    context = {
        'athleteProf':athleteProf,
        'wellness':wellness,

        'testType':testType,

        'all_dates':all_dates,

        'TenYdSprint_results':TenYdSprint_results,
        'TenYdSprint_dates':TenYdSprint_dates,
        'TenYd_chart':TenYd_chart,

        'Bench1RM_results':Bench1RM_results,
        'Bench1RM_chart':Bench1RM_chart,

        'CMJ_results':CMJ_results,
        'CMJ_chart':CMJ_chart,
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

    context = {}

    return render(request, 'html/analyze.html', context)

