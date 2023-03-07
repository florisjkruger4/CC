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

    # Access all dates
    all_dates = KpiT.objects.filter(fname=fname, lname=lname, dob=dob)

    # Takes user input through a Django form (in this case it takes the "select" option when user hits submit form btn)
    date_one = request.POST.get("date1")
    date_two = request.POST.get("date2")

    # Gets the rows for 10yd Sprint for specific athlete
    TenYdSprint_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='10yd Sprint', datekpi__range=(date_one, date_two))
    # Sets x and y coordinate values
    TenYd_x = [x.datekpi for x in TenYdSprint_results]
    TenYd_y = [x.testresult for x in TenYdSprint_results]
    # Calls matplotlib bar graph with above data
    TenYd_chart = bar_graph(TenYd_x, TenYd_y)
    TenYd_chart_line = line_graph(TenYd_x, TenYd_y)

    # Gets the rows for Barbell Bench Press 1RM for specific athlete
    Bench1RM_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='Barbell Bench Press 1RM', datekpi__range=(date_one, date_two))
    # Sets x and y coordinate values
    Bench1RM_x = [x.datekpi for x in Bench1RM_results]
    Bench1RM_y = [y.testresult for y in Bench1RM_results]
    # Calls matplotlib bar graph with above data
    Bench1RM_chart = bar_graph(Bench1RM_x, Bench1RM_y)
    Bench1RM_chart_line = line_graph(Bench1RM_x, Bench1RM_y)

    # Gets the rows for CMJ for specific athlete
    CMJ_results = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype__exact='CMJ', datekpi__range=(date_one, date_two))
    # Sets x and y coordinate values
    CMJ_x = [x.datekpi for x in CMJ_results]
    CMJ_y = [y.testresult for y in CMJ_results]
    # Calls matplotlib bar graph with above data
    CMJ_chart = bar_graph(CMJ_x, CMJ_y)
    CMJ_chart_line = line_graph(CMJ_x, CMJ_y)

    context = {
        'athleteProf':athleteProf,
        'wellness':wellness,

        'testType':testType,

        'all_dates':all_dates,

        'TenYdSprint_results':TenYdSprint_results,
        'TenYd_chart':TenYd_chart,
        'TenYd_chart_line':TenYd_chart_line,
        'TenYd_y':TenYd_y,

        'Bench1RM_results':Bench1RM_results,
        'Bench1RM_chart':Bench1RM_chart,
        'Bench1RM_chart_line':Bench1RM_chart_line,
        'Bench1RM_y':Bench1RM_y,

        'CMJ_results':CMJ_results,
        'CMJ_chart':CMJ_chart,
        'CMJ_chart_line':CMJ_chart_line,
        'CMJ_y':CMJ_y,

        'date_one':date_one,
        'date_two':date_two
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

