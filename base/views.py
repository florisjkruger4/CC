import json, time
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT, TestTypeT
from .utils import bar_graph, line_graph, radar_chart, z_score_graph
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import AthleteForm, ImageForm, RegisterForm, UpdateUserForm
import concurrent.futures

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
    )

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
    )

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
    )

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
    )

    context = {
        "athletes": athletes,
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


start_time = 0
end_time = 0

"""
#def kpiTScoreAjax(fname, lname, dob, date_one, date_two, t_avg, g_avg, p_avg):
        """

"""
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
            z_score_teamAVG_list = [0];
        
        # finds the indexes from array above to pick out the z-score results that belong to the current athlete
        athlete_z_scores_relation_to_teamAVG = [z_score_teamAVG_list[x] for x in index_Tracker]

        # Convert to t-scores
        T_Scores_TeamAVG = []
        for i in range(0, len(athlete_z_scores_relation_to_teamAVG)):
            calc = ((athlete_z_scores_relation_to_teamAVG[i]*10)+50)
            T_Scores_TeamAVG.append(calc)

        # Calls matplotlib t-score graph
        #z_score_bar.append(z_score_graph(results_x, T_Scores_TeamAVG))

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
            z_score_genderAVG_list = [0];
    
        # finds the indexes from array above to pick out the z-score results that belong to the current athlete
        athlete_z_scores_relation_to_genderAVG = [z_score_genderAVG_list[x] for x in index_Tracker]

        # Convert to t-scores
        T_Scores_GenderAVG = []
        for i in range(0, len(athlete_z_scores_relation_to_genderAVG)):
            calc = ((athlete_z_scores_relation_to_genderAVG[i]*10)+50)
            T_Scores_GenderAVG.append(calc)

        # Calls matplotlib t-score graph
        #z_score_bar.append(z_score_graph(results_x, T_Scores_GenderAVG))

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
            z_score_positionAVG_list = [0];
    
        # finds the indexes from array above to pick out the z-score results that belong to the current athlete
        athlete_z_scores_relation_to_positionAVG = [z_score_positionAVG_list[x] for x in index_Tracker]

        # Convert to t-scores
        T_Scores_PositionAVG = []
        for i in range(0, len(athlete_z_scores_relation_to_positionAVG)):
            calc = ((athlete_z_scores_relation_to_positionAVG[i]*10)+50)
            T_Scores_PositionAVG.append(calc)

        # Calls matplotlib t-score graph
        #z_score_bar.append(z_score_graph(results_x, T_Scores_PositionAVG))
        
    # Calls matplotlib bar graph with above data
    
    #kpi_bar.append(bar_graph(results_x, results_y, T_AVG, G_AVG, P_AVG))



    # Checking if the current test type's min is better ([0][0] is just indexing the first element of the list, true or false)
    #minBetter = TestTypeT.objects.filter(tname=x).values_list() #.values_list('minbetter')[0][0]
    #print(minBetter.minbetter)
    # Append the current tests minBetter result to the list of minBetter results
    #minBetter_list.append(minBetter.values_list("minbetter")[0][0])


    """

def kpiAjax(athlete, date_one, date_two, rad, t_avg, g_avg, p_avg):

    start_time = time.time()

    all_kpi = list(
        KpiT.objects.filter(
            fname=athlete.fname, 
            lname=athlete.lname, 
            dob=athlete.dob, 
            datekpi__range=(date_one, date_two)
        ).values('testtype', 'datekpi', 'testresult')
        .order_by("testtype", "datekpi")
    )

    minBetter = list(
        TestTypeT.objects.all()   
    )
    
    # init/reset variables to 0 before next use
    test_types = []
    kpi_line = []
    changes = []
    minBetter_list = []
    trend_vals = {}

    team_avgs = []
    gender_avgs = []
    pos_avgs = []

    # Dictionaries for each kpi result of each test type
    # x stores k/v pairs: { <test_type>: dates[] }
    # y stores k/v pairs: { <test_type>: values[] }
    raw_results_x = {}
    raw_results_y = {}

    # Get kpi results & corresponding dates for each test type
    for x in all_kpi:

        # We've encountered a new test type, init array within dict
        if x['testtype'] not in test_types:

            test_types.append(x['testtype'])

            raw_results_x[x['testtype']] = []
            raw_results_y[x['testtype']] = []
        
        raw_results_x[x['testtype']].append(x['datekpi'])
        raw_results_y[x['testtype']].append(x['testresult'])
    
    for x in test_types:

        minBetterValue = False

        # first and last value of this test type for this athlete
        first_result = raw_results_y[x][0]
        last_result = raw_results_y[x][len(raw_results_x[x])-1]

        trend_vals[x] = []
        trend_vals[x].append(first_result)
        trend_vals[x].append(last_result)

        change = round(last_result - first_result, 2)
        changes.append(change)

        # Determine whether minimum is better or not for this test type
        for y in minBetter:
            if y.tname == x:
                minBetterValue = y.minbetter
                minBetter_list.append(minBetterValue)
                break

        # make line graph for previous test type
        kpi_line.append(line_graph(raw_results_x[x], raw_results_y[x], change, minBetterValue))

        # handles average values
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
            team_avgs.append(T_AVG)
            #print("Team Avg: " + x) 
            #print(T_AVG)

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
            gender_avgs.append(T_AVG)
            #print("Gender Avg: " + x) 
            #print(G_AVG)

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
            pos_avgs.append(T_AVG)
            #print("Position Avg: " + x) 
            #print(P_AVG)

    end_time = time.time()
    print(f"Elapsed: {end_time - start_time: }")
    # Objects returned to frontend:
    # test_types = list of all test types for this athlete
    # Date1_results = list of floating point values of kpis on first date selected
    # Date2_results = list of floating point values of kpis on second date selected
    # changes = list of floating point values of difference between date1 and date2 results
    # kpi_bar and kpi_line: bar and line graphs respectively
    return JsonResponse(
        {
            "test_types": test_types,
            "trend_vals": trend_vals,
            "changes": changes,
            "raw_results_x": raw_results_x,
            "raw_results_y": raw_results_y,

            # List of true or false values for each test type
            "minBetter": minBetter_list,
            #"kpi_bar": list(kpi_bar),
            "kpi_line": kpi_line,
            "team_avgs": team_avgs,
            "gender_avgs": gender_avgs,
            "pos_avgs": pos_avgs,
            #"z_score_bar": list(z_score_bar),
        }
    )


def wellnessAjax(fname, lname, dob, wellnessdate):
    # Get the appropriate wellness report

    wellness = WellnessT.objects.filter(
        fname=fname, lname=lname, dob=dob, date=wellnessdate
    ).values()

    # Return the list of athletes
    return JsonResponse({"wellness": list(wellness.values())})


@login_required(login_url="/")
def AthleteProf(request, fname, lname, dob, id):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob, id=id)

    # instance of an image in order to edit profile picture...
    # (I have no idea what this means, it took me so long to get it working, if it works, it works.
    # Django documentation says to use ._meta("field name") but that never worked for me)
    instanceImg = AthleteT.objects.filter(id=id).only("image").first()

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            # load data from AJAX
            data = json.load(request)

            # if we have data for "date1" and "date2", we have a kpi update request
            if data.get("date1") and data.get("date2" or data.get("AVG_Radio_BTN") or data.get("T_AVG_BTN") or data.get("G_AVG_BTN") or data.get("P_AVG_BTN")):
                return kpiAjax(
                    athleteProf, 
                    data.get("date1"), 
                    data.get("date2"),
                    data.get("AVG_Radio_BTN"),
                    data.get("T_AVG_BTN"), 
                    data.get("G_AVG_BTN"), 
                    data.get("P_AVG_BTN")
                )

            # if we have data for "wellnessdate", we have a wellness update request
            elif data.get("wellnessdate"):
                return wellnessAjax(fname, lname, dob, data.get("wellnessdate"))

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

            #start_time = time.time()

            # Access and store all dates
            kpi_dates = (
                KpiT.objects.filter(fname=fname, lname=lname, dob=dob)
                .values("datekpi")
                .order_by("datekpi")
                .distinct()
            )

            # Gets earlies and latest kpi dates for specific athlete
            kpi_earliest = kpi_dates.first()["datekpi"]
            kpi_most_recent = kpi_dates.last()["datekpi"]
        
        else: #if there are no kpi records for this athlete but there are wellness records... still loads their page
            kpi_dates = None
            kpi_earliest = None
            kpi_most_recent = None
            kpi_count = None

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

    # Image handling
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
        "all_dates": kpi_dates,
        "kpi_earliest": kpi_earliest,
        "kpi_most_recent": kpi_most_recent,
        "kpi_count": kpi_count,
        # Wellness
        "wellnessReportDates": wellness_dates,
        "mostRecentWellnessReportDate": wellness_most_recent,
        "wellness_count": wellness_count,
        # Radar/Spider
        #"Radar_chart": Radar_chart,
        #"radar_date": radar_date,
        #"all_tests": all_tests,
        #"selected_radar_tests": selected_radar_tests,
        # dashboardd session stuff
        "recentlyViewedAthletes": recentlyViewedAthletes,
        # img form stuff
        "form": form,
    }

    return render(request, "html/athleteProf.html", context)


@login_required(login_url="/")
def EditAthlete(request, fname, lname, dob, id):
    athlete = AthleteT.objects.get(id=id)

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

    context = {"athlete": athlete}

    return render(request, "html/editathlete.html", context)


@login_required(login_url="/")
def TeamDash(request):
    athletes = TeamT.objects.all()

    context = {"teams": athletes}

    return render(request, "html/teams.html", context)


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
            )

            # Gets the JSON data to hold info containig all tests selected
            if data.get("InputCellArray"):
                
                date = data.get("date_selector")
                print(date)
                
                testType = data.get("TestTypeArray")

                selectedSport = data.get("sportsteam")
                athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport).values_list("fname", "lname", "dob")

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
                        if (testResult[index] != "-1"):
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

            # Get all athletes on this team
            athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport)

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
                if len(wellness_trend_data_x) > 1:
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
    """
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    Fname = fname
    Lname = lname
    DOB = dob

    Sports = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values(
        "sportsteam"
    )
    for x in Sports:
        SportsTeam = x["sportsteam"]

    Positions = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values(
        "position"
    )
    for x in Positions:
        Position = x["position"]

    Images = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values("image")
    for x in Images:
        Img = x["image"]

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
            sportsteam=SportsTeam,
            date=newdate,
            position=Position,
            hoursofsleep=newhoursofsleep,
            sleepquality=newsleepquality,
            breakfast=newbreakfast,
            hydration=newhydration,
            soreness=newsoreness,
            stress=newstress,
            mood=newmood,
            image=Img,
        )

        newWellness.validate_constraints()
        newWellness.save()

    context = {
        "athleteProf": athleteProf,
    }

    """

    return render(request, "html/wellnessForm.html")
