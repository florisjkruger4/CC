import json, time
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT, TestTypeT
from .utils import bar_graph, line_graph, z_score_graph, bar_graph_groups
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import AthleteForm, ImageForm, RegisterForm, UpdateUserForm
from django.utils import timezone
from datetime import timedelta

import numpy as np
import pandas as pd
import scipy.stats as stats



def LoginRegister(request):
    page = "login"

    # if user is loged in... redirect to dashboard (prevents from double logging in)
    if request.user.is_authenticated:
        return redirect("dash/")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dash/")
        else:
            messages.error(request, "Username or Password does not exist")

    context = {
        "page": page,
    }
    return render(request, "html/loginRegister.html", context)


@login_required(login_url="/")
def userProf(request, username):
    user = User.objects.get(username=username)

    form = RegisterForm()

    updateForm = UpdateUserForm(user)

    allUsers = User.objects.all()

    if request.method == 'POST':
        updateForm = UpdateUserForm(user, request.POST)
        if updateForm.is_valid():
            user = updateForm.save()
            user.save()
        else:
            messages.error(request, "An error occured when updating this profile")

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()

            return redirect(userProf, username=username)
        else:
            messages.error(request, "An error occured during registration")

    context = {
        "user": user,
        "form": form,
        "updateForm":updateForm,
        "allUsers":allUsers
    }

    return render(request, "html/userProf.html", context)

@login_required(login_url="/")
def DeleteUser(request, username, id):
    user_to_delete = User.objects.get(id=id)
    user_to_delete.delete()

    return redirect(userProf, username=username)

# deletes the session id token... meaning the user needs to log in once again to create a new session to be authenticated
def LogoutUser(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/")
def Dashboard(request):
    athletes = AthleteT.objects.all()
    addedKPIs = KpiT.objects.all().order_by('-id')[0:8]

    # session stuff...
    recentlyViewedAthletes = None
    sessionLength = None

    if "recently_viewed" in request.session:
        Athletes = AthleteT.objects.filter(id__in=request.session["recently_viewed"])
        recentlyViewedAthletes = sorted(
            Athletes, key=lambda x: request.session["recently_viewed"].index(x.id)
        )
        sessionLength = len(request.session["recently_viewed"])

    context = {
        "athletes": athletes,
        "addedKPIs":addedKPIs,
        "recentlyViewedAthletes": recentlyViewedAthletes,
        "sessionLength": sessionLength,
    }

    return render(request, "html/dashboard.html", context)

@login_required(login_url="/")
def DeleteKPI_Dash(request, id):
    kpi_to_delete = KpiT.objects.get(id=id)
    kpi_to_delete.delete()

    return redirect(Dashboard)

@login_required(login_url="/")
def AthletesDash(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    athletes = AthleteT.objects.filter(
        Q()
        | Q(fname__icontains=q)
        | Q(lname__icontains=q)
        | Q(sportsteam__icontains=q)
        | Q(position__icontains=q)
        | Q(year__icontains=q)
    ).order_by("fname");

    context = {
        "athletes": athletes,
    }

    return render(request, "html/athletes.html", context)

@login_required(login_url="/")
def MaleAthletes(request):
    q = request.GET.get("q")
    q = "M"

    athletes = AthleteT.objects.filter(
        Q()
        | Q(gender__icontains=q)
    ).order_by("fname")

    context = {
        "athletes": athletes,
    }

    return render(request, "html/athletes.html", context)

@login_required(login_url="/")
def FemaleAthletes(request):
    q = request.GET.get("q")
    q = "F"

    athletes = AthleteT.objects.filter(
        Q()
        | Q(gender__icontains=q)
    ).order_by("fname")

    context = {
        "athletes": athletes,
    }

    return render(request, "html/athletes.html", context)

@login_required(login_url="/")
def TeamSpecificAthletes(request, sport):
    q = request.GET.get("q")
    q = sport

    athletes = AthleteT.objects.filter(
        Q()
        | Q(sportsteam__icontains=q)
    ).order_by("fname")

    context = {
        "athletes": athletes,
        "sport": sport,
    }

    return render(request, "html/athletes.html", context)

@login_required(login_url="/")
def AddAthlete(request):
    if request.method == "POST":
        form = AthleteForm(request.POST, request.FILES)

        if form.is_valid():
            # form.validate_constraints()
            messages.info(request, 'Athlete Added Successfully')
            form.save()
        else:
            messages.info(request, 'Athlete Profile Already Exists')

    else:
        form = AthleteForm()

    context = {
        "form": form,
    }

    return render(request, "html/addathlete.html", context)

def graphData(athlete, date_one, date_two):

    return list(
        KpiT.objects.filter(
            fname=athlete.fname, 
            lname=athlete.lname, 
            dob=athlete.dob, 
            datekpi__range=(date_one, date_two)
        ).values('testtype', 'datekpi', 'testresult')
        .order_by("testtype", "datekpi")
    )

def trendsAjax(all_kpi):

    # Dictionaries for each kpi result of each test type
    # x stores k/v pairs: { <test_type>: dates[] }
    # y stores k/v pairs: { <test_type>: values[] }
    raw_results_x = {}
    raw_results_y = {}

    # List of all test types recorded for this athlete within specified date range
    test_types = []

    # Get kpi results & corresponding dates for each test type
    for x in all_kpi:

        # We've encountered a new test type, init array within dict
        if x['testtype'] not in test_types:

            test_types.append(x['testtype'])

            raw_results_x[x['testtype']] = []
            raw_results_y[x['testtype']] = []
        
        raw_results_x[x['testtype']].append(x['datekpi'])
        raw_results_y[x['testtype']].append(x['testresult'])
    
    #raw_results_x, raw_results_y, test_types = graphData(athlete, date_one, date_two)
    
    minBetter = list(
        TestTypeT.objects.all()   
    )
    
    kpi_line = []
    changes = []
    minBetter_list = []
    Date1_results = []
    Date2_results = [] 
    
    for x in test_types:

        # first and last value of this test type for this athlete
        first_result = raw_results_y[x][0]
        last_result = raw_results_y[x][len(raw_results_x[x])-1]

        Date1_results.append(first_result)
        Date2_results.append(last_result)

        change = round(last_result - first_result, 2)
        changes.append(change)

        # Determine whether minimum is better or not for this test type
        minBetterValue = False

        for y in minBetter:
            if y.tname == x:
                minBetterValue = y.minbetter
                minBetter_list.append(minBetterValue)
                break

        kpi_line.append(line_graph(raw_results_x[x], raw_results_y[x], change, minBetterValue))

    # Objects returned to frontend:
    # Date1_results = list of floating point values of kpis on first date selected
    # Date2_results = list of floating point values of kpis on second date selected
    # changes = list of floating point values of difference between date1 and date2 results
    # minBetter = list of boolean values to control visuals in front end regarding test types
    # kpi_line = list of line graphs representing trend in kpi data results
    return JsonResponse(
        {
            "test_types": test_types,
            "Date1_results": Date1_results,
            "Date2_results": Date2_results,
            "changes": changes,
            "minBetter": minBetter_list,
            "kpi_line": kpi_line,
        }
    )

def tScoreAjax(all_kpi, athlete, date_one, date_two, rad):

    # Dictionaries for each kpi result of each test type
    # x stores k/v pairs: { <test_type>: dates[] }
    # y stores k/v pairs: { <test_type>: values[] }
    raw_results_x = {}
    raw_results_y = {}

    # List of all test types recorded for this athlete within specified date range
    test_types = []

    # Get kpi results & corresponding dates for each test type
    for x in all_kpi:

        # We've encountered a new test type, init array within dict
        if x['testtype'] not in test_types:

            test_types.append(x['testtype'])

            raw_results_x[x['testtype']] = []
            raw_results_y[x['testtype']] = []
        
        raw_results_x[x['testtype']].append(x['datekpi'])
        raw_results_y[x['testtype']].append(x['testresult'])

    #raw_results_x, raw_results_y, test_types = graphData(athlete, date_one, date_two)

    z_score_bar = []

    for x in test_types:


        if (rad == '1'):
            # Z-SCORE GRAPH'S IN RELATION TO TEAM AVERAGE (RADIO BUTTON 1)
            # find all the athletes on the same team and get their kpi reports
            same_team_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam).values('fname', 'lname', 'dob')
            kpi_results = KpiT.objects.filter(fname__in=same_team_athletes.values_list('fname', flat=True),
                                        lname__in=same_team_athletes.values_list('lname', flat=True),
                                        dob__in=same_team_athletes.values_list('dob', flat=True),
                                        datekpi__range=(date_one, date_two)).values('fname', 'lname', 'dob', 'testtype', 'testresult').order_by('datekpi')
            
            # Loop through kpi_results to find all tests that relate to the z-score graph that needs to be generated
            # keeps track of all tests from athletes on the same team relating to this test type
            indiv_tests = []
            # keeps track of the indexes where the test result belongs to this athlete
            index_Tracker = []
            for result in kpi_results:
                athFname = result['fname']
                athLname = result['lname']
                athDOB = result['dob']
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                    indiv_tests.append(test_result)
                    # if this test result belongs to the current athlete.. store the index val
                    if (athFname == athlete.fname and athLname == athlete.lname and athDOB == athlete.dob):
                        index_Tracker.append(indiv_tests.index(test_result))

            # gets the z-scores for all the tests relating to this test type, date selection, and sports team 
            z_score_teamAVG_results = stats.zscore(indiv_tests, nan_policy='omit')
            # converts to list type
            z_score_teamAVG_list = z_score_teamAVG_results.tolist()
            # checks if z_score_list is nan or not
            if (np.any(np.isnan(z_score_teamAVG_list))):
                # if it is nan, then initialize to 0
                z_score_teamAVG_list = [0]
            
            # finds the indexes from array above to pick out the z-score results that belong to the current athlete
            athlete_z_scores_relation_to_teamAVG = [z_score_teamAVG_list[x] for x in index_Tracker]

            # Convert to t-scores
            T_Scores_TeamAVG = []
            for i in range(0, len(athlete_z_scores_relation_to_teamAVG)):
                calc = ((athlete_z_scores_relation_to_teamAVG[i]*10)+50)
                T_Scores_TeamAVG.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(raw_results_x[x], T_Scores_TeamAVG))

        elif (rad == '2'):
            # Z-SCORE GRAPH'S IN RELATION TO GENDER AVERAGE (RADIO BUTTON 2)
            # Queryset of athletes of the same gender 
            same_gender_athletes = AthleteT.objects.filter(gender=athlete.gender).values_list('fname', 'lname', 'dob')
            # Queryset of KPI data for each athlete of the same gender 
            kpi_results = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                                lname__in=same_gender_athletes.values_list('lname', flat=True),
                                dob__in=same_gender_athletes.values_list('dob', flat=True),
                                datekpi__range=(date_one, date_two)).values('fname', 'lname', 'dob', 'testtype', 'testresult').order_by('datekpi')

            # Loop through kpi_results to find all tests that relate to the z-score graph that needs to be generated
            # keeps track of all tests from athletes on the same team relating to this test type
            indiv_tests = []
            # keeps track of the indexes where the test result belongs to this athlete
            index_Tracker = []
            for result in kpi_results:
                athFname = result['fname']
                athLname = result['lname']
                athDOB = result['dob']
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                        indiv_tests.append(test_result)
                        # if this test result belongs to the current athlete.. store the index val
                        if (athFname == athlete.fname and athLname == athlete.lname and athDOB == athlete.dob):
                            index_Tracker.append(indiv_tests.index(test_result))

            # gets the z-scores for all the tests relating to this test type, date selection, and sports team 
            z_score_genderAVG_results = stats.zscore(indiv_tests, nan_policy='omit')
            # converts to list type
            z_score_genderAVG_list = z_score_genderAVG_results.tolist()
            # checks if z_score_list is nan or not
            if (np.any(np.isnan(z_score_genderAVG_list))):
                # if it is nan, then initialize to 0
                z_score_genderAVG_list = [0]
        
            # finds the indexes from array above to pick out the z-score results that belong to the current athlete
            athlete_z_scores_relation_to_genderAVG = [z_score_genderAVG_list[x] for x in index_Tracker]

            # Convert to t-scores
            T_Scores_GenderAVG = []
            for i in range(0, len(athlete_z_scores_relation_to_genderAVG)):
                calc = ((athlete_z_scores_relation_to_genderAVG[i]*10)+50)
                T_Scores_GenderAVG.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(raw_results_x[x], T_Scores_GenderAVG))

        elif (rad == '3'):
            # Z-SCORE GRAPH'S IN RELATION TO POSITION AVERAGE (RADIO BUTTON 3)
            # Queryset of athletes of the same position 
            same_position_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam, position=athlete.position).values_list('fname', 'lname', 'dob')
            # Queryset of KPI data for each athlete of the same position where test type is in the selected tests
            kpi_results = KpiT.objects.filter(fname__in=same_position_athletes.values_list('fname', flat=True),
                                lname__in=same_position_athletes.values_list('lname', flat=True),
                                dob__in=same_position_athletes.values_list('dob', flat=True),
                                datekpi__range=(date_one, date_two)).values('fname', 'lname', 'dob', 'testtype', 'testresult')

            # Loop through kpi_results to find all tests that relate to the z-score graph that needs to be generated
            # keeps track of all tests from athletes on the same team relating to this test type
            indiv_tests = []
            # keeps track of the indexes where the test result belongs to this athlete
            index_Tracker = []
            for result in kpi_results:
                athFname = result['fname']
                athLname = result['lname']
                athDOB = result['dob']
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                        indiv_tests.append(test_result)
                        # if this test result belongs to the current athlete.. store the index val
                        if (athFname == athlete.fname and athLname == athlete.lname and athDOB == athlete.dob):
                            index_Tracker.append(indiv_tests.index(test_result))

            # gets the z-scores for all the tests relating to this test type, date selection, and sports team 
            z_score_positionAVG_results = stats.zscore(indiv_tests, nan_policy='omit')
            # converts to list type
            z_score_positionAVG_list = z_score_positionAVG_results.tolist()
            # checks if z_score_list is nan or not
            if (np.any(np.isnan(z_score_positionAVG_list))):
                # if it is nan, then initialize to 0
                z_score_positionAVG_list = [0]
        
            # finds the indexes from array above to pick out the z-score results that belong to the current athlete
            athlete_z_scores_relation_to_positionAVG = [z_score_positionAVG_list[x] for x in index_Tracker]

            # Convert to t-scores
            T_Scores_PositionAVG = []
            for i in range(0, len(athlete_z_scores_relation_to_positionAVG)):
                calc = ((athlete_z_scores_relation_to_positionAVG[i]*10)+50)
                T_Scores_PositionAVG.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(raw_results_x[x], T_Scores_PositionAVG))

    return JsonResponse(
        {
            "test_types": test_types,
            "z_score_bar": z_score_bar,
        }
    )
         
def rawScoreAjax(all_kpi, athlete, date_one, date_two, t_avg, g_avg, p_avg):

    # Dictionaries for each kpi result of each test type
    # x stores k/v pairs: { <test_type>: dates[] }
    # y stores k/v pairs: { <test_type>: values[] }
    raw_results_x = {}
    raw_results_y = {}

    # List of all test types recorded for this athlete within specified date range
    test_types = []

    # Get kpi results & corresponding dates for each test type
    for x in all_kpi:

        # We've encountered a new test type, init array within dict
        if x['testtype'] not in test_types:

            test_types.append(x['testtype'])

            raw_results_x[x['testtype']] = []
            raw_results_y[x['testtype']] = []
        
        raw_results_x[x['testtype']].append(x['datekpi'])
        raw_results_y[x['testtype']].append(x['testresult'])
    
    # init/reset variables to 0 before next use
    kpi_bar = []
    
    for x in test_types:

        if (t_avg == '1'):
            # find all the athletes on the same team and get their kpi reports
            same_team_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam).values('fname', 'lname', 'dob')
            kpi_results = KpiT.objects.filter(fname__in=same_team_athletes.values_list('fname', flat=True),
                                        lname__in=same_team_athletes.values_list('lname', flat=True),
                                        dob__in=same_team_athletes.values_list('dob', flat=True),
                                        datekpi__range=(date_one, date_two)).values('fname', 'lname', 'dob', 'testtype', 'testresult').order_by('datekpi')
            indiv_tests = []
            for result in kpi_results:
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                        indiv_tests.append(test_result)

            # gets average of all the athletes on the same team with respect to the dates selected
            T_AVG = (sum(indiv_tests) / len(indiv_tests))
            print("Team Avg: " + x) 
            print(T_AVG)
        else:
            T_AVG = None
        
        if (g_avg == '1'):
            # find all the athletes of the gender and get their kpi reports
            same_gender_athletes = AthleteT.objects.filter(gender=athlete.gender).values_list('fname', 'lname', 'dob')
            kpi_results = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                                lname__in=same_gender_athletes.values_list('lname', flat=True),
                                dob__in=same_gender_athletes.values_list('dob', flat=True),
                                datekpi__range=(date_one, date_two)).values('fname', 'testtype', 'testresult').order_by('datekpi')
            indiv_tests = []
            for result in kpi_results:
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                        indiv_tests.append(test_result)

            # gets average of all the athletes on the same gender with respect to the dates selected
            G_AVG = (sum(indiv_tests) / len(indiv_tests))
            print("Gender Avg: " + x) 
            print(G_AVG)
        else:
            G_AVG = None

        if (p_avg == '1'):
            # find all the athletes of the position and get their kpi reports
            same_position_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam, position=athlete.position).values_list('fname', 'lname', 'dob')
            kpi_results = KpiT.objects.filter(fname__in=same_position_athletes.values_list('fname', flat=True),
                                lname__in=same_position_athletes.values_list('lname', flat=True),
                                dob__in=same_position_athletes.values_list('dob', flat=True),
                                datekpi__range=(date_one, date_two)).values('fname', 'lname', 'dob', 'testtype', 'testresult')
            indiv_tests = []
            for result in kpi_results:
                testType = result['testtype']
                test_result = result['testresult']
                if testType == x:
                        indiv_tests.append(test_result)

            # gets average of all the athletes on the same position with respect to the dates selected
            P_AVG = (sum(indiv_tests) / len(indiv_tests))
            print("Position Avg: " + x) 
            print(P_AVG)
        else:
            P_AVG = None
            
        # Calls matplotlib bar graph with above data
        kpi_bar.append(bar_graph(raw_results_x[x], raw_results_y[x], T_AVG, G_AVG, P_AVG))

    # Objects returned to frontend:
    # test_types = list of all test types for this athlete
    # kpi_bar: raw values bar graphs
    # z_score_bar: t-scores bar graphs

    return JsonResponse(
        {
            "test_types": test_types,
            "kpi_bar": kpi_bar,
        }
    )

def wellnessAjax(athlete, wellnessdate):
    # Get the appropriate wellness report

    wellness = list(
        WellnessT.objects.filter(
        fname=athlete.fname, lname=athlete.lname, dob=athlete.dob, date=wellnessdate
        ).values()
    )

    # Return the list of athletes
    return JsonResponse({"wellness": wellness})

def spiderAjax(athlete, spider_date, selected_spider_tests, compare_avg):


    # Athletes results for selected KPI's and Date
    # Dictioanry of test_type and result key:value pairs
    # Dictioanry of test_type and result key:value pairs
    athlete_spider_results = {}
    for test in selected_spider_tests:
        # Get the kpi result <=/lte to the given date
        result = KpiT.objects.filter(fname=athlete.fname, lname=athlete.lname, dob=athlete.dob, datekpi__lte=spider_date, testtype=test).order_by('datekpi').values_list('testresult', flat=True).first()
        athlete_spider_results[test] = result

    # List to hold nested dictionaries of averages test data
    average_spider_results = []

    # Sportsteam: generate averages in each selected test for athletes of the same Sportsteam 
    if "team_avg" in compare_avg:
        same_team_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam).exclude(fname=athlete.fname, lname=athlete.lname, dob=athlete.dob).values_list('fname', 'lname', 'dob')
        # Queryset of KPI data for each athlete of the same team where test type is in the selected tests and datekpi is less than or equal to the specified spider date
        kpi_results = KpiT.objects.filter(fname__in=same_team_athletes.values_list('fname', flat=True),
                            lname__in=same_team_athletes.values_list('lname', flat=True),
                            dob__in=same_team_athletes.values_list('dob', flat=True),
                            testtype__in=selected_spider_tests,
                            datekpi__lte=spider_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
        # Loop through kpi_results and add up the test results for each test type
        test_results = {}
        for result in kpi_results:
            test_type = result['testtype']
            test_result = result['testresult']
            if test_type in test_results:
                # If test_type already exists, add the new test result to the existing value
                test_results[test_type]['total'] += test_result
                test_results[test_type]['count'] += 1
            else:
                # If test_type doesn't exist, create a new dictionary entry for it
                test_results[test_type] = {'total': test_result, 'count': 1}
        # Loop through test_results and calculate the average for each test type rounded to the nearest whole number
        for test_type, result in test_results.items():
            average = round(result['total'] / result['count'])
            test_results[test_type] = average
        # Append the test_type and average result key:value pair to the result
        average_spider_results.append({'group': 'team', 'results': test_results})

    # Position: generate averages in each selected test for athletes of the same position 
    if "position_avg" in compare_avg:
        same_position_athletes = AthleteT.objects.filter(sportsteam=athlete.sportsteam, position=athlete.position).exclude(fname=athlete.fname, lname=athlete.lname, dob=athlete.dob).values_list('fname', 'lname', 'dob')
        # Queryset of KPI data for each athlete of the same position where test type is in the selected tests and datekpi is less than or equal to the specified spider date
        kpi_results = KpiT.objects.filter(fname__in=same_position_athletes.values_list('fname', flat=True),
                            lname__in=same_position_athletes.values_list('lname', flat=True),
                            dob__in=same_position_athletes.values_list('dob', flat=True),
                            testtype__in=selected_spider_tests,
                            datekpi__lte=spider_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
        # Loop through kpi_results and add up the test results for each test type
        test_results = {}
        for result in kpi_results:
            test_type = result['testtype']
            test_result = result['testresult']
            if test_type in test_results:
                # If test_type already exists, add the new test result to the existing value
                test_results[test_type]['total'] += test_result
                test_results[test_type]['count'] += 1
            else:
                # If test_type doesn't exist, create a new dictionary entry for it
                test_results[test_type] = {'total': test_result, 'count': 1}
        # Loop through test_results and calculate the average for each test type rounded to the nearest whole number
        for test_type, result in test_results.items():
            average = round(result['total'] / result['count'])
            test_results[test_type] = average
        # Append the test_type and average result key:value pair to the result
        average_spider_results.append({'group': 'position', 'results': test_results})

    # Gender: generate averages in each selected test for athletes of the same gender 
    if "gender_avg" in compare_avg:
        # Queryset of athletes of the same gender not including the current athlete
        same_gender_athletes = AthleteT.objects.filter(gender=athlete.gender).exclude(fname=athlete.fname, lname=athlete.lname, dob=athlete.dob).values_list('fname', 'lname', 'dob')
        # Queryset of KPI data for each athlete of the same gender where test type is in the selected tests and datekpi is less than or equal to the specified spider date
        kpi_results = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                            lname__in=same_gender_athletes.values_list('lname', flat=True),
                            dob__in=same_gender_athletes.values_list('dob', flat=True),
                            testtype__in=selected_spider_tests,
                            datekpi__lte=spider_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
        # Loop through kpi_results and add up the test results for each test type
        test_results = {}
        for result in kpi_results:
            test_type = result['testtype']
            test_result = result['testresult']
            if test_type in test_results:
                # If test_type already exists, add the new test result to the existing value
                test_results[test_type]['total'] += test_result
                test_results[test_type]['count'] += 1
            else:
                # If test_type doesn't exist, create a new dictionary entry for it
                test_results[test_type] = {'total': test_result, 'count': 1}
        # Loop through test_results and calculate the average for each test type rounded to the nearest whole number
        for test_type, result in test_results.items():
            average = round(result['total'] / result['count'])
            test_results[test_type] = average
        # Append the test_type and average result key:value pair to the result
        average_spider_results.append({'group': 'gender', 'results': test_results})

    return JsonResponse({
        "spider_date": spider_date, 
        # "spider_chart": spider_chart,
        "athlete_spider_results": athlete_spider_results,
        "average_spider_results": average_spider_results,
        #"athlete_spider_results": athlete_spider_results,
        })

@login_required(login_url="/")
def AthleteProf(request, fname, lname, dob, id):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob, id=id)

    # instance of an image in order to edit profile picture...
    # (I have no idea what this means, it took me so long to get it working, if it works, it works.
    # Django documentation says to use ._meta("field name") but that never worked for me)
    instanceImg = AthleteT.objects.filter(id=id).only("image").first()

    spider_date = None
    kpi_dates = []

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            all_kpi = []

            # load data from AJAX
            data = json.load(request)
            date_one = data.get("date1")
            date_two = data.get("date2")
            req_type = data.get("req_type")

            # AJAX requests
            if req_type == "raw-score":
                all_kpi = graphData(athleteProf, date_one, date_two)
                return rawScoreAjax(all_kpi, athleteProf, date_one, date_two, data.get("T_AVG_BTN"), data.get("G_AVG_BTN"), data.get("P_AVG_BTN"))
            
            elif req_type == "t-score":
                all_kpi = graphData(athleteProf, date_one, date_two)
                return tScoreAjax(all_kpi, athleteProf, date_one, date_two, data.get("AVG_Radio_BTN"))
            
            elif req_type == "trend":
                all_kpi = graphData(athleteProf, date_one, date_two)
                return trendsAjax(all_kpi)

            elif req_type == "wellness":
                return wellnessAjax(athleteProf, data.get("wellnessdate"))
            
            elif req_type == "spider":
                return spiderAjax(athleteProf, data.get("spider_date"), data.get("selected_spider_tests"), data.get("compare_avg"))

            # data passed did not fit criteria above, so it is invalid
            else:
                return JsonResponse({"status": "Invalid request"}, status=400)
        else:
            return JsonResponse({"status": "Invalid request"}, status=400)

    # Not an AJAX call... page is likely initially loading
    # Init page will contain Athlete Profile info (fname, lname, sport, pos...) +
    # all kpi dates and all wellness dates.
    else:
        # session stuff...
        recentlyViewedAthletes = None

        if "recently_viewed" in request.session:
            Athletes = AthleteT.objects.filter(
                id__in=request.session["recently_viewed"]
            )
            recentlyViewedAthletes = sorted(
                Athletes, key=lambda x: request.session["recently_viewed"].index(x.id)
            )

            request.session["recently_viewed"].insert(0, id)
            if len(request.session["recently_viewed"]) > 6:
                request.session["recently_viewed"].pop()
        else:
            request.session["recently_viewed"] = [id]

        request.session.modified = True

        kpi_count = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        wellness_count = int(
            WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        )

        # We don't have any wellness or kpi data, so just return
        if kpi_count == 0 and wellness_count == 0:
            all_dates = None
            # Image handling for if there is no data in an athletes profile (no kpi records or wellness records)
            if request.method == "POST":
                form = ImageForm(request.POST, request.FILES, instance=instanceImg)
                if form.is_valid():
                    # form.validate_constraints()
                    form.save()
            else:
                form = ImageForm()

            context = {"athleteProf": athleteProf, "form": form}

            return render(request, "html/athleteProf.html", context)

        if kpi_count > 0:

            # Access and store all dates athlete has KPIs on
            kpi_dates = (
                KpiT.objects.filter(fname=fname, lname=lname, dob=dob)
                .values("datekpi")
                .order_by("datekpi")
                .distinct()
            )

            # Get list (array) of all dates; will be used by JS
            all_dates = list(kpi_dates.values_list("datekpi", flat=True))

            # Get date 6 months ago today 
            six_months_ago = timezone.now() - timedelta(days=30*6)
            six_months_ago_str = six_months_ago.strftime('%Y-%m-%d')

            # If an athlete only has records before 6 months ago, just grab the
            # first recorded kpi
            if all_dates[0] <= six_months_ago_str:
                kpi_earliest = six_months_ago_str
            else:
                kpi_earliest = kpi_dates.first()["datekpi"]

            # Get most recent kpi date
            kpi_most_recent = kpi_dates.last()["datekpi"]

            # Get all test types recorded for athlete
            all_tests = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values_list('testtype', flat=True).distinct()

        else: #if there are no kpi records for this athlete but there are wellness records... still loads their page
            kpi_dates = None
            kpi_earliest = None
            kpi_most_recent = None
            kpi_count = None

            all_tests = None
            all_dates = None

        if wellness_count > 0:
            # Access and store all dates
            wellness_dates = (
                WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)
                .values("date")
                .annotate(dcount=Count("date"))
                .order_by("date")
            )

            wellness_most_recent = wellness_dates.last()["date"]
        else:  # if there are no wellness records for this athlete but there are kpi records... still loads their page
            wellness_dates = None
            wellness_most_recent = None

    # Image handeling
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=instanceImg)
        if form.is_valid():
            # form.validate_constraints()
            form.save()
    else:
        form = ImageForm()

    context = {
        "athleteProf": athleteProf,
        # KPI
        "all_dates": json.dumps(all_dates),
        "kpi_dates": kpi_dates,
        "kpi_earliest": kpi_earliest,
        "kpi_most_recent": kpi_most_recent,
        "kpi_count": kpi_count,
        # Wellness
        "wellnessReportDates": wellness_dates,
        "mostRecentWellnessReportDate": wellness_most_recent,
        "wellness_count": wellness_count,
        # Spider
        "all_tests": all_tests,
        # dashboard session stuff
        "recentlyViewedAthletes": recentlyViewedAthletes,
        # img form stuff
        "form": form,
    }

    return render(request, "html/athleteProf.html", context)


@login_required(login_url="/")
def EditAthlete(request, fname, lname, dob, id):
    athlete = AthleteT.objects.get(id=id)
    teams = TeamT.objects.all

    # deletes entire athlete from database... along with their wellness and kpi records
    if request.GET.get("delete") == "delete":
        AthleteT.objects.filter(id=id).delete()
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).delete()
        KpiT.objects.filter(fname=fname, lname=lname, dob=dob).delete()

        return redirect("/athletes")

    # updates changes made to athlete across all tables
    if request.method == "POST":
        editFname = request.POST["fname"]
        editLname = request.POST["lname"]
        editGender = request.POST["gender"]
        editYear = request.POST["year"]
        editHeight = request.POST["height"]
        editDOB = request.POST["dob"]
        editTeam = request.POST["sportsteam"]
        editPosition = request.POST["position"]

        # what the new edit looks like
        newEdit = AthleteT(
            fname=editFname,
            lname=editLname,
            gender=editGender,
            dob=editDOB,
            sportsteam=editTeam,
            position=editPosition,
            year=editYear,
            height=editHeight,
        )

        if ((athlete.fname == editFname and athlete.lname == editLname and athlete.dob == editDOB) and (athlete.gender != editGender or athlete.height != editHeight or athlete.sportsteam != editTeam or athlete.position != editPosition or athlete.year != editYear)):
            athlete = AthleteT.objects.filter(id=id).update(
                fname=editFname,
                lname=editLname,
                gender=editGender,
                dob=editDOB,
                sportsteam=editTeam,
                position=editPosition,
                year=editYear,
                height=editHeight,
            )
        else:
            # checks if this is even allowedd before the update queries get sent
            newEdit.validate_constraints()

            athlete = AthleteT.objects.filter(id=id).update(
                fname=editFname,
                lname=editLname,
                gender=editGender,
                dob=editDOB,
                sportsteam=editTeam,
                position=editPosition,
                year=editYear,
                height=editHeight,
            )

        #redirect info
        x = AthleteT.objects.get(id=id)

        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).update(
            fname=editFname,
            lname=editLname,
            dob=editDOB,
        )

        KpiT.objects.filter(fname=fname, lname=lname, dob=dob).update(
            fname=editFname,
            lname=editLname,
            dob=editDOB,
        )

        return redirect(AthleteProf, fname=x.fname, lname=x.lname, dob=x.dob, id=x.id)

    context = {
        "athlete": athlete,
        "teams": teams
        }

    return render(request, "html/editathlete.html", context)

def teamsAjax(date1, date2, selection, rad, t_avg, g_avg):

    kpi_bar = []
    z_score_bar = []

    # Gets test types within selected date range for all athletes
    if selection == "allAthletes":
        rad = '0'
        all_testTypes = (
            KpiT.objects.filter(
                datekpi__range=(date1, date2),
            )
            .values_list("testtype", flat=True)
            .order_by("testtype")
            .distinct()
        )

    # gets all the male athletes
    male_athletes = AthleteT.objects.filter(gender="M").values_list('fname', 'lname', 'dob')
    # gets all test types within selected date range for male athletes
    if selection == "allMales":
        rad = '0'
        all_testTypes = (
            KpiT.objects.filter(
            fname__in=male_athletes.values_list('fname', flat=True),
            lname__in=male_athletes.values_list('lname', flat=True),
            dob__in=male_athletes.values_list('dob', flat=True),
            datekpi__range=(date1, date2),
        )
        .values_list("testtype", flat=True)
        .order_by("testtype")
        .distinct()
    )
        
    # gets all the female athletes
    female_athletes = AthleteT.objects.filter(gender="F").values_list('fname', 'lname', 'dob')
    # gets all test types within selected date range for female athletes
    if selection == "allFemales":
        rad = '0'
        all_testTypes = (
            KpiT.objects.filter(
            fname__in=female_athletes.values_list('fname', flat=True),
            lname__in=female_athletes.values_list('lname', flat=True),
            dob__in=female_athletes.values_list('dob', flat=True),
            datekpi__range=(date1, date2),
        )
        .values_list("testtype", flat=True)
        .order_by("testtype")
        .distinct()
    )
    
    # selection was made for a specific sports team
    if (selection != "allAthletes" and selection != "allMales" and selection != "allFemales"):
        # gets all the athletes on selected team
        team_athletes = AthleteT.objects.filter(sportsteam=selection).values_list('fname', 'lname', 'dob')

        all_testTypes = (
            KpiT.objects.filter(
            fname__in=team_athletes.values_list('fname', flat=True),
            lname__in=team_athletes.values_list('lname', flat=True),
            dob__in=team_athletes.values_list('dob', flat=True),
            datekpi__range=(date1, date2),
        )
        .values_list("testtype", flat=True)
        .order_by("testtype")
        .distinct()
    )
        
    for x in all_testTypes:

        # array to hold all the average values tests done by different athletes on the same day
        averages = []

        if selection == "allAthletes":
            gender_avg = None
            team_average = None

            # selects all the dates relavant to to the specific test type
            all_dates = KpiT.objects.filter(datekpi__range=(date1, date2), testtype__exact=x).values_list("datekpi", flat=True).order_by("datekpi").distinct()

            kpi_results = (KpiT.objects.filter(
                    testtype__exact=x,
                    datekpi__range=(date1, date2),
                )
                .order_by("datekpi")
            )

            for y in all_dates:
                vals = []
                for z in kpi_results:
                    if z.datekpi == y:
                        vals.append(z.testresult)
                if len(vals) > 0:
                    avg = (sum(vals) / len(vals))
                else:
                    avg = (sum(vals) / 1)
                averages.append(avg)

        elif selection == "allMales":
            gender_avg = None
            team_average = None

            # selects all the dates relavant to to the specific test type
            all_dates = (KpiT.objects.filter(
                fname__in=male_athletes.values_list('fname', flat=True),
                lname__in=male_athletes.values_list('lname', flat=True),
                dob__in=male_athletes.values_list('dob', flat=True),
                datekpi__range=(date1, date2), 
                testtype__exact=x)
                .values_list("datekpi", flat=True)
                .order_by("datekpi")
                .distinct()
            )

            # gets all the male athlete's kpi record's in respected date
            kpi_results = (KpiT.objects.filter(
                    fname__in=male_athletes.values_list('fname', flat=True),
                    lname__in=male_athletes.values_list('lname', flat=True),
                    dob__in=male_athletes.values_list('dob', flat=True),
                    testtype__exact=x,
                    datekpi__range=(date1, date2),
                )
                .order_by("datekpi")
            )

            for y in all_dates:
                vals = []
                for z in kpi_results:
                    if z.datekpi == y:
                        vals.append(z.testresult)
                if len(vals) > 0:
                    avg = (sum(vals) / len(vals))
                else:
                    avg = (sum(vals) / 1)
                averages.append(avg)

        elif selection == "allFemales":
            gender_avg = None
            team_average = None

            # selects all the dates relavant to to the specific test type
            all_dates = (KpiT.objects.filter(
                fname__in=female_athletes.values_list('fname', flat=True),
                lname__in=female_athletes.values_list('lname', flat=True),
                dob__in=female_athletes.values_list('dob', flat=True),
                datekpi__range=(date1, date2), 
                testtype__exact=x)
                .values_list("datekpi", flat=True)
                .order_by("datekpi")
                .distinct()
            )

            # gets all the female athlete's kpi record's in respected date
            kpi_results = (KpiT.objects.filter(
                    fname__in=female_athletes.values_list('fname', flat=True),
                    lname__in=female_athletes.values_list('lname', flat=True),
                    dob__in=female_athletes.values_list('dob', flat=True),
                    testtype__exact=x,
                    datekpi__range=(date1, date2),
                )
                .order_by("datekpi")
            )

            for y in all_dates:
                vals = []
                for z in kpi_results:
                    if z.datekpi == y:
                        vals.append(z.testresult)
                if len(vals) > 0:
                    avg = (sum(vals) / len(vals))
                else:
                    avg = (sum(vals) / 1)
                averages.append(avg)

        else:
            # selects all the dates relavant to to the specific test type
            all_dates = (KpiT.objects.filter(
                fname__in=team_athletes.values_list('fname', flat=True),
                lname__in=team_athletes.values_list('lname', flat=True),
                dob__in=team_athletes.values_list('dob', flat=True),
                datekpi__range=(date1, date2), 
                testtype__exact=x)
                .values_list("datekpi", flat=True)
                .order_by("datekpi")
                .distinct()
            )

            # gets all the team specific athlete's kpi record's in respected date
            kpi_results = (KpiT.objects.filter(
                    fname__in=team_athletes.values_list('fname', flat=True),
                    lname__in=team_athletes.values_list('lname', flat=True),
                    dob__in=team_athletes.values_list('dob', flat=True),
                    testtype__exact=x,
                    datekpi__range=(date1, date2),
                )
                .order_by("datekpi")
            )

            for y in all_dates:
                vals = []
                for z in kpi_results:
                    if z.datekpi == y:
                        vals.append(z.testresult)
                if len(vals) > 0:
                    avg = (sum(vals) / len(vals))
                else:
                    avg = (sum(vals) / 1)
                averages.append(avg)

            if t_avg == '1':
                indiv_tests = []
                for q in kpi_results:
                    indiv_tests.append(q.testresult)
                team_average = sum(indiv_tests) / len(indiv_tests)
                
            else:
                team_average = None
                
            if g_avg == '1':
                # gets all athletes on team to determine gender
                athlete_on_team = AthleteT.objects.filter(sportsteam=selection).values_list('gender')
                # gets all the gender of selected teams's kpi record's in respected date
                same_gender_athletes = AthleteT.objects.filter(gender__in=athlete_on_team.values_list('gender', flat=True)).values_list('fname', 'lname', 'dob')
                # Queryset of KPI data for each athlete of the same gender as selected team gender
                kpi_results_same_gender = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                                    lname__in=same_gender_athletes.values_list('lname', flat=True),
                                    dob__in=same_gender_athletes.values_list('dob', flat=True),
                                    testtype__exact=x,
                                    datekpi__range=(date1, date2)).order_by('datekpi')
                
                same_gender_kpi_results = []
                for z in kpi_results_same_gender:
                    same_gender_kpi_results.append(z.testresult)

                gender_avg = sum(same_gender_kpi_results) / len(same_gender_kpi_results)

            else:
                gender_avg = None

        if rad == "1":

            indiv_tests = []
            for q in kpi_results:
                indiv_tests.append(q.testresult)

            team_z_scores = []
            for i in averages:
                indiv_tests.append(i)
                z = stats.zscore(indiv_tests, nan_policy='omit')
                z_list = z.tolist()
                if (np.any(np.isnan(z_list))):
                # if it is nan, then initialize to 0
                    z_list = [0];
                team_z_scores.append(z_list[-1])
                indiv_tests.pop()

            # Convert to t-scores
            T_Scores = []
            for i in range(0, len(team_z_scores)):
                calc = ((team_z_scores[i]*10)+50)
                T_Scores.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(all_dates, T_Scores))

        elif rad == "2":

            # gets all athletes on team to determine gender
            athlete_on_team = AthleteT.objects.filter(sportsteam=selection).values_list('gender')
            # gets all the gender of selected teams's kpi record's in respected date
            same_gender_athletes = AthleteT.objects.filter(gender__in=athlete_on_team.values_list('gender', flat=True)).values_list('fname', 'lname', 'dob')
            # Queryset of KPI data for each athlete of the same gender as selected team gender
            kpi_results = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                                lname__in=same_gender_athletes.values_list('lname', flat=True),
                                dob__in=same_gender_athletes.values_list('dob', flat=True),
                                testtype__exact=x,
                                datekpi__range=(date1, date2)).order_by('datekpi')
            
            indiv_tests = []
            for q in kpi_results:
                indiv_tests.append(q.testresult)

            gender_z_scores = []
            for i in averages:
                indiv_tests.append(i)
                z = stats.zscore(indiv_tests, nan_policy='omit')
                z_list = z.tolist()
                if (np.any(np.isnan(z_list))):
                # if it is nan, then initialize to 0
                    z_list = [0];
                gender_z_scores.append(z_list[-1])
                indiv_tests.pop()

            # Convert to t-scores
            T_Scores = []
            for i in range(0, len(gender_z_scores)):
                calc = ((gender_z_scores[i]*10)+50)
                T_Scores.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(all_dates, T_Scores))

       # elif rad == "3": not applicable for the groups page...

        else:   # rad == '0'
            z_scores = stats.zscore(averages, nan_policy='omit')
            # converts to list type
            z_scores_list = z_scores.tolist()
            # checks if z_score_list is nan or not
            if (np.any(np.isnan(z_scores_list))):
                # if it is nan, then initialize to 0
                z_scores_list = [0];

            # Convert to t-scores
            T_Scores = []
            for i in range(0, len(z_scores_list)):
                calc = ((z_scores_list[i]*10)+50)
                T_Scores.append(calc)

            # Calls matplotlib t-score graph
            z_score_bar.append(z_score_graph(all_dates, T_Scores))

        results_x = all_dates
        results_y = averages
        
        kpi_bar.append(bar_graph_groups(results_x, results_y, team_average, gender_avg))

    return JsonResponse({
        "all_testTypes": list(all_testTypes),
        "kpi_bar": list(kpi_bar),
        "z_score_bar": list(z_score_bar),
        })

@login_required(login_url="/")
def GroupDash(request):
    athletes = TeamT.objects.all()

    # Access and store all dates
    all_dates = KpiT.objects.values("datekpi").order_by("datekpi").distinct()

     # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            # load data from AJAX
            data = json.load(request)

            # if we have data for "date1" and "date2", we have a kpi update request
            if data.get("date1") and data.get("date2") and data.get("radiotest"):
                return teamsAjax(data.get("date1"), data.get("date2"), data.get("radiotest"), data.get("AVG_Radio_BTN"), data.get("t_AVG"), data.get("g_AVG"))

        else:
            return JsonResponse({"status": "Invalid request"}, status=400)
    
    context = {
        "teams": athletes,
        "all_dates": all_dates,
        }

    return render(request, "html/groups.html", context)

@login_required(login_url="/")
def recordKPI(request):
    # Define teams
    teams = TeamT.objects.values("sport").order_by("sport").distinct()

    # All test type names in the TestTypeT table
    test_types = TestTypeT.objects.values_list("tname", flat=True)

    # Initialise selectedSport and athletes to null and empty set respectively
    selectedSport = ""
    athletes = []

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            # Get the JSON data from the request
            data = json.load(request)
            selectedSport = data.get("sportsteam")

            # Get the first names and last names of all the athletes whose team matches requested team
            athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport).values(
                "fname", "lname"
            ).order_by("fname")

            # Gets the JSON data to hold info containig all tests selected
            if data.get("InputCellArray"):

                date = data.get("date_selector")
                print(date)

                testType = data.get("TestTypeArray")

                selectedSport = data.get("sportsteam")
                athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport).values_list("fname", "lname", "dob").order_by("fname")

                testResult = data.get("InputCellArray")

                index = 0
                for x in testType:
                    for y in athletes:
                        newKPI = KpiT(
                            fname=y[0],
                            lname=y[1],
                            dob=y[2],
                            datekpi=date,
                            testtype=x,
                            testresult=testResult[index],
                        )
                        if (float(testResult[index]) >= 0):
                            print(y[0] + " " + y[1] + " " + y[2] + " " + date + " " + x + " " + testResult[index])
                            newKPI.validate_constraints()
                            newKPI.save()
                        index+=1


            # Return the list of athletes
            return JsonResponse({"athletes": list(athletes.values())})
        return JsonResponse({"status": "Invalid request"}, status=400)

    # Other (non-AJAX) requests will recieve a response with a whole HTML document. This requires a page reload.


    if request.method == 'POST':
        print("test")

    context = {
        "athletes": athletes,
        "teams": teams,
        "selectedSport": selectedSport,

        # TestTypeT table tname's
        "test_types": test_types,
    }

    return render(request, "html/recordKPI.html", context)


@login_required(login_url="/")
def addTestType(request):
    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            # Get the JSON data from the request
            data = json.load(request)
            tname = data.get('Tname')
            minBetter = data.get('minBetter')

            # If minBetter is true, set minBetter = 1
            if minBetter:
                minBetter = 1
            # Otherwise set minBetter = 0
            else:
                minBetter = 0

            # Make a data entry for the the new test 
            TestTypeT.objects.create(
                    tname=tname,
                    minbetter=minBetter,
                )

            return JsonResponse({'success': True})


@login_required(login_url="/")
def WellnessDash(request):
    wellnessDates = WellnessT.objects.values("date").order_by("date").distinct()
    wellnessSportsTeams = TeamT.objects.values("sport").order_by("sport").distinct()

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":

            # Get date and sport passed from front end
            data = json.load(request)
            selectedDate = data.get("wellnessdate")
            selectedSport = data.get("sportsteam")
            show_trends = data.get("show_trends")

            # Get all athletes on this team
            athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport).order_by("fname")

            all_wellness = {}
            athletes_img = []
            wellness_trends = []
            iter = 0

            for x in athletes:
                wellness_latest = {}

                # Get wellness reports relevant to this athlete
                wellness_relevant = WellnessT.objects.filter(
                    fname=x.fname, lname=x.lname, dob=x.dob, date__lte=selectedDate
                )

                # ...then order them by date
                result = wellness_relevant.order_by("date").last()

                # ...if the athlete does not have an image uploaded
                if (x.image == ''):
                    x.image = "/media/placeholder.jpg"
                    athletes_img.append(str(x.image))
                else:
                    # Get athlete image from AthleteT
                    athletes_img.append(x.image.url)

                # If there are wellness reports for this athlete, get each resulting data point
                if wellness_relevant:
                    wellness_latest["hoursofsleep"] = result.hoursofsleep
                    wellness_latest["sleepquality"] = result.sleepquality
                    wellness_latest["breakfast"] = result.breakfast
                    wellness_latest["hydration"] = result.hydration
                    wellness_latest["soreness"] = result.soreness
                    wellness_latest["stress"] = result.stress
                    wellness_latest["mood"] = result.mood

                    wellness_latest["status"] = result.status
                    wellness_latest["date"] = result.date

                    all_wellness[iter] = wellness_latest

                # ... Otherwise, set them to all zeroes (front end will interpret this as an athlete that has
                # no Wellness reports and will adjust the view accordingly)
                else:
                    wellness_latest["hoursofsleep"] = 0
                    wellness_latest["sleepquality"] = 0
                    wellness_latest["breakfast"] = 0
                    wellness_latest["hydration"] = 0
                    wellness_latest["soreness"] = 0
                    wellness_latest["stress"] = 0
                    wellness_latest["mood"] = 0

                    wellness_latest["status"] = None
                    wellness_latest["date"] = None

                    all_wellness[iter] = wellness_latest

                iter += 1

                wellness_trend_data_x = []
                wellness_trend_data_y = []

                # Calculate total readiness score to construct a trend graph
                for y in wellness_relevant:
                    total = y.hoursofsleep
                    total += y.sleepquality
                    total += y.breakfast
                    total += y.hydration
                    total += y.soreness
                    total += y.stress
                    total += y.mood

                    wellness_trend_data_y.append(total)
                    wellness_trend_data_x.append(y.date)

                # If there is more than one wellness report, create trend graph
                if len(wellness_trend_data_x) > 1 and show_trends:
                    wellness_trends.append(
                        line_graph(
                            wellness_trend_data_x, wellness_trend_data_y, 0, None
                        )
                    )
                else:
                    wellness_trends.append(None)

            return JsonResponse(
                {
                    "athletes_img": list(athletes_img),
                    "athletes": list(
                        athletes.values("fname", "lname", "dob", "position")
                    ),
                    "wellness": list(all_wellness.values()),
                    "wellness_trends": list(wellness_trends),
                }
            )

        return JsonResponse({"status": "Invalid request"}, status=400)

    context = {
        "wellnessDates": wellnessDates,
        "wellnessSportsTeams": wellnessSportsTeams,
    }

    return render(request, "html/wellness.html", context)

@login_required(login_url="/")
def AddTeam(request):

    if request.method == "POST":
        team = request.POST["teamname"]

        newTeam = TeamT(
            sport=team
        )

        newTeam.validate_unique()
        newTeam.save()

    return render(request, "html/addteam.html")

@login_required(login_url="/")
def AddKPI(request, fname, lname, dob):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    # All test type names in the TestTypeT table
    test_types = TestTypeT.objects.values_list("tname", flat=True)

    # All KPI reports for this specific athlete
    athlete_KPI_Reports = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).order_by("-datekpi")

    Fname = fname
    Lname = lname
    DOB = dob

    if request.method == "POST":
        newdate = request.POST["datekpi"]
        newtest = request.POST["testtype"]
        newresult = request.POST["testresult"]

        newKPI = KpiT(
            fname=Fname,
            lname=Lname,
            dob=DOB,
            datekpi=newdate,
            testtype=newtest,
            testresult=newresult,
        )

        newKPI.validate_constraints()
        newKPI.save()

    context = {
        "athleteProf": athleteProf,
        "athlete_KPI_Reports":athlete_KPI_Reports,
        "test_types": test_types,
    }

    return render(request, "html/addkpi.html", context)

@login_required(login_url="/")
def EditKPI(request, id):

    # gets id of kpi record
    editKPI = KpiT.objects.get(id=id)

    # All test type names in the TestTypeT table
    test_types = TestTypeT.objects.values_list("tname", flat=True)

    # initiallizes for initial page load
    newkpi = None

     # updates changes made to kpi in kpi table
    if request.method == "POST":
        editTestType = request.POST["testtype"]
        editTestResult = request.POST["testresult"]
        editDatekpi = request.POST["datekpi"]

        # what the new edit looks like
        newEdit = KpiT(
            fname=editKPI.fname,
            lname=editKPI.lname,
            dob=editKPI.dob,
            testtype=editTestType,
            testresult=editTestResult,
            datekpi=editDatekpi,
        )

        if editKPI.testtype == editTestType and editKPI.datekpi == editDatekpi and editKPI.testresult != editTestResult:
            newkpi = KpiT.objects.filter(id=id).update(
                testresult=editTestResult,
            )
        else:
            # checks if this is even allowed before reaching the update queries
            newEdit.validate_constraints()

            newkpi = KpiT.objects.filter(id=id).update(
                testtype=editTestType,
                testresult=editTestResult,
                datekpi=editDatekpi,
            )

        return redirect(AddKPI, fname=editKPI.fname, lname=editKPI.lname, dob=editKPI.dob)

    context = {
        "editKPI":editKPI,
        "test_types":test_types,
        "newkpi":newkpi
    }

    return render(request, "html/editkpi.html", context)

@login_required(login_url="/")
def DeleteKPI(request, id):
    kpi_to_delete = KpiT.objects.get(id=id)
    kpi_to_delete.delete()

    return redirect(AddKPI, fname=kpi_to_delete.fname, lname=kpi_to_delete.lname, dob=kpi_to_delete.dob)

@login_required(login_url="/")
def DeleteTeam(request, sport):
    team_to_delete = TeamT.objects.get(sport=sport)
    team_to_delete.delete()
    
    return redirect(GroupDash)

@login_required(login_url="/")
def AddWellness(request, fname, lname, dob):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    Fname = fname
    Lname = lname
    DOB = dob

    if request.method == "POST":
        newhoursofsleep = request.POST["hoursofsleep"]
        newsleepquality = request.POST["sleepquality"]
        newbreakfast = request.POST["breakfast"]
        newhydration = request.POST["hydration"]
        newsoreness = request.POST["soreness"]
        newstress = request.POST["stress"]
        newmood = request.POST["mood"]
        newstatus = request.POST["status"]
        newdate = request.POST["date"]

        newWellness = WellnessT(
            fname=Fname,
            lname=Lname,
            dob=DOB,
            status=newstatus,
            date=newdate,
            hoursofsleep=newhoursofsleep,
            sleepquality=newsleepquality,
            breakfast=newbreakfast,
            hydration=newhydration,
            soreness=newsoreness,
            stress=newstress,
            mood=newmood,
        )

        newWellness.validate_constraints()
        newWellness.save()

    context = {
        "athleteProf": athleteProf,
    }

    return render(request, "html/addwellness.html", context)


@login_required(login_url="/")
def wellnessForm(request):

    # This is here so we can retrieve a list of athletes for the name selector
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    athletes = AthleteT.objects.filter(
        Q()
        | Q(fname__icontains=q)
        | Q(lname__icontains=q)
        | Q(sportsteam__icontains=q)
        | Q(position__icontains=q)
        | Q(year__icontains=q)
    )

    # This is for adding a new wellness entry
    if request.method == "POST":

        selectedAthlete = request.POST.get("name")
        Fname, Lname, DOB = selectedAthlete.split(' ')

        newhoursofsleep = request.POST["hoursofsleep"]
        newsleepquality = request.POST["sleepquality"]
        newbreakfast = request.POST["breakfast"]
        newhydration = request.POST["hydration"]
        newsoreness = request.POST["soreness"]
        newstress = request.POST["stress"]
        newmood = request.POST["mood"]
        newstatus = request.POST["status"]
        newdate = request.POST["date"]

        newWellness = WellnessT(

            fname=Fname,
            lname=Lname,
            dob=DOB,

            status=newstatus,
            date=newdate,
            hoursofsleep=newhoursofsleep,
            sleepquality=newsleepquality,
            breakfast=newbreakfast,
            hydration=newhydration,
            soreness=newsoreness,
            stress=newstress,
            mood=newmood,
        )

        newWellness.validate_constraints()
        newWellness.save()


    context = {
        #"athleteProf": athleteProf,
        "athletes": athletes,
    }


    return render(request, "html/wellnessForm.html", context)
