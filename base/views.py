import json
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import bar_graph, line_graph, radar_chart
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def LoginRegister(request):

    page = 'login'

    # if user is loged in... redirect to dashboard (prevents from double logging in)
    if request.user.is_authenticated:
        return redirect('dash/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        print(user)

        if user is not None:
            login(request, user)
            return redirect('dash/')
        else:
            messages.error(request, "Username or Password does not exist")

    context = {
        'page':page,
    }
    return render(request, 'html/loginRegister.html', context)

@login_required(login_url='/')
def userProf(request, username):

    user = User.objects.get(username=username)

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # do we care about case sensitive usernames??
            user = form.save()
            user.save()

            # log in created user
            login(request, user)
            return redirect('/dash')
        else:
            messages.error(request, 'An error occured during registration')

    context = {
        'user':user,
        'form':form,
    }

    return render(request, 'html/userProf.html', context)

# deletes the session id token... meaning the user needs to log in once again to create a new session to be authenticated
def LogoutUser(request):

    logout(request)
    return redirect('/')

def RegisterUser(request):

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # do we care about case sensitive usernames??
            user = form.save()
            user.save()

            # log in created user
            login(request, user)
            return redirect('/dash')
        else:
            messages.error(request, 'An error occured during registration')

    context = {
        'form':form,
    }

    return render(request, 'html/loginRegister.html', context)

test_types = [
    "5m Sprint",
    "10m Sprint",
    "10m Fly",
    "15m Sprint",
    "15m Fly",
    "20m Sprint",
    "20m Fly",
    "25m Sprint",
    "30m Sprint",
    "40m Sprint",
    "60m Sprint",
    "5yd Sprint",
    "10yd Sprint",
    "10yd Fly",
    "15yd Sprint",
    "15yd Fly",
    "20yd Sprint",
    "20yd Fly",
    "25yd Sprint",
    "30yd Sprint",
    "40yd Sprint",
    "60yd Sprint",
    "110yd Sprint",
    "Broad Jump",
    "Double Broad Jump",
    "Triple Broad Jump",
    "Standing Triple Jump",
    "Countermovement Jump (Hands-on-Hips Force Plate)",
    "Countermovement Rebound Jump (Hands-on-Hips Force Plate)",
    "Countermovement Jump (Vertec)",
    "Approach Jump (Vertec)",
    "10-5 RSI",
    "5-0-5 Agility",
    "5-10-5 Pro Agility",
    "60yd Shuttle",
    "300yd Shuttle",
    "Beep Test (Traditional)",
    "Beep Test (Yo-Yo Intermittent Recovery Test)",
    "Max Aerobic Speed",
    "Clean 1RM",
    "Snatch 1RM",
    "Jerk 1RM",
    "Clean & Jerk 1RM",
    "Barbell Bench Press 1RM",
    "Barbell Bench Press Max Reps (135lbs)",
    "Barbell Bench Press Max Reps (185lbs)",
    "Barbell Bench Press Max Reps (225lbs)",
    "Dumbbell Bench Press 1RM",
    "Barbell Back Squat 1RM",
    "Barbell Front Squat 1RM",
    "Barbell Deadlift 1RM",
    "Hex Bar Deadlift 1RM",
    "Pull-Up 1RM",
    "Pull-Up Max Reps (60 sec)",
    "Push-Up Max Reps (60 sec)",
    "Isometric Mid-Thigh Pull",
    "Isometric Belt Squat",
    "Bodyweight",
    "Body Composition",
    "Fat Mass",
    "Fat Free Mass",
    "Lean Body Mass",
    "Braking RFD",
    "Average Relative Propulsive Force",
    "Propulsive Net Impulse",
]


@login_required(login_url='/')
def Dashboard(request):
    athletes = AthleteT.objects.all()

    context = {
        "athletes": athletes,
    }

    return render(request, "html/dashboard.html", context)

@login_required(login_url='/')
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

@login_required(login_url='/')
def AddAthlete(request):
    if request.method == "POST":
        newFname = request.POST["fname"]
        newLname = request.POST["lname"]
        newGender = request.POST["gender"]
        newYear = request.POST["year"]
        newHeight = request.POST["height"]
        newImage = request.POST["image"]
        newDOB = request.POST["dob"]
        newTeam = request.POST["sportsteam"]
        newPosition = request.POST["position"]

        newAthlete = AthleteT(
            fname=newFname,
            lname=newLname,
            gender=newGender,
            dob=newDOB,
            sportsteam=newTeam,
            position=newPosition,
            year=newYear,
            height=newHeight,
            image=newImage,
        )

        newAthlete.validate_constraints()
        newAthlete.save()

    return render(request, "html/addathlete.html")


def kpiAjax(fname, lname, dob, date_one, date_two):

    # init/reset variables to 0 before next use
    kpi_bar = []
    kpi_line = []
    Date1_results = []
    Date2_results = []
    changes = []
    iter = 0

    # Gets test types within selected date range
    test_type = (
        KpiT.objects.filter(
            fname=fname,
            lname=lname,
            dob=dob,
            datekpi__range=(date_one, date_two),
        )
        .values_list("testtype", flat=True)
        .order_by("testtype")
        .distinct()
    )

    # Get kpi results for each test type 
    for x in test_type:
        # Gets the rows for this test for specific athlete
        kpi_results = KpiT.objects.filter(
            fname=fname,
            lname=lname,
            dob=dob,
            testtype__exact=x,
            datekpi__range=(date_one, date_two),
        ).order_by("datekpi")

        # Sets x and y coordinate values
        results_x = [x.datekpi for x in kpi_results]
        results_y = [x.testresult for x in kpi_results]

        # Date 1 test score result
        if date_one:
            Date1_result = kpi_results.order_by("datekpi").first()
                    
            if Date1_result:
                Date1_results.append(Date1_result.testresult)

        else:
            Date1_results.append(None)

        # Date 2 test score result
        if date_two:
            Date2_result = kpi_results.order_by("datekpi").last()

            if Date2_result:
                Date2_results.append(Date2_result.testresult)

        else:
            Date2_results.append(None)

        # If both give values (not null), calculate difference betweeen them
        if Date1_results[iter] and Date2_results[iter]:
                    
            change = Date2_results[iter] - Date1_results[iter]
            changes.append(round(change, 2))

        # Calls matplotlib bar graph with above data
        kpi_line.append(line_graph(results_x, results_y, changes[iter]))
        kpi_bar.append(bar_graph(results_x, results_y))

        iter += 1

    # Objects returned to frontend:
    # test_types = list of all test types for this athlete
    # Date1_results = list of floating point values of kpis on first date selected 
    # Date2_results = list of floating point values of kpis on second date selected 
    # changes = list of floating point values of difference between date1 and date2 results
    # kpi_bar and kpi_line: bar and line graphs respectively 
    return JsonResponse({
        "test_types": list(test_type),
        "Date1_results": list(Date1_results),
        "Date2_results": list(Date2_results),
        "changes": list(changes),
        "kpi_bar": list(kpi_bar),
        "kpi_line": list(kpi_line),
    })

    
def wellnessAjax(fname, lname, dob, wellnessdate):
    
    # Get the appropriate wellness report
    wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob, date=wellnessdate).values()

    # Return the list of athletes
    return JsonResponse({"wellness": list(wellness.values())})

def spider(request, athleteProf):
    # This code generates a radar/spider chart to display the latest KPI results for an athlete given a date 
        # All tests the athlete has taken

        fname = athleteProf.fname
        lname = athleteProf.lname
        dob = athleteProf.dob
        


@login_required(login_url='/')
def AthleteProf(request, fname, lname, dob,):

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":
            # load data from AJAX 
            data = json.load(request)

            # if we have data for "date1" and "date2", we have a kpi update request
            if data.get("date1") and data.get("date2"):
                return kpiAjax(fname, lname, dob, data.get("date1"), data.get("date2"))
            
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
        kpi_count = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        wellness_count = int(
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        )

        # We don't have any wellness or kpi data, so just return 
        if kpi_count == 0 and wellness_count == 0:

            context = {
                "athleteProf": athleteProf,
            }

            return render(request, "html/athleteProf.html", context)

        if kpi_count > 0:
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

        if kpi_count > 2:
            sportsteam = athleteProf.sportsteam
            gender = athleteProf.gender
            position = athleteProf.position

            all_tests = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values_list('testtype', flat=True).distinct()

            if request.method == "POST":
                # Selected KPI date and tests
                radar_date = request.POST.get("radar_date")
                selected_radar_tests = request.POST.getlist('selected_radar_tests')
            else:
                radar_date = kpi_most_recent
                selected_radar_tests = all_tests

            # Athletes results for selected KPI's and Date
            # Dictioanry of test_type and result key:value pairs
            athlete_radar_results = {}
            for test in selected_radar_tests:
                # Get the kpi result <=/lte to the given date
                result = KpiT.objects.filter(fname=fname, lname=lname, dob=dob, datekpi__lte=radar_date, testtype=test).order_by('datekpi').values_list('testresult', flat=True).first()
                athlete_radar_results[test] = result

            # List specifying which averages to comapre to (Team, Position, or Gender)
            compare_avg = request.POST.getlist('compare_avg')

            # List to hold nested dictionaries of averages test data
            average_radar_results = []

            # Sportsteam: generate averages in each selected test for athletes of the same Sportsteam 
            if "team_avg" in compare_avg:
                same_team_athletes = AthleteT.objects.filter(sportsteam=sportsteam).exclude(fname=fname, lname=lname, dob=dob).values_list('fname', 'lname', 'dob')
                # Queryset of KPI data for each athlete of the same team where test type is in the selected tests and datekpi is less than or equal to the specified radar date
                kpi_results = KpiT.objects.filter(fname__in=same_team_athletes.values_list('fname', flat=True),
                                    lname__in=same_team_athletes.values_list('lname', flat=True),
                                    dob__in=same_team_athletes.values_list('dob', flat=True),
                                    testtype__in=selected_radar_tests,
                                    datekpi__lte=radar_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
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
                average_radar_results.append({'group': 'team', 'results': test_results})

            # Position: generate averages in each selected test for athletes of the same position 
            if "position_avg" in compare_avg:
                same_position_athletes = AthleteT.objects.filter(sportsteam=sportsteam, position=position).exclude(fname=fname, lname=lname, dob=dob).values_list('fname', 'lname', 'dob')
                # Queryset of KPI data for each athlete of the same position where test type is in the selected tests and datekpi is less than or equal to the specified radar date
                kpi_results = KpiT.objects.filter(fname__in=same_position_athletes.values_list('fname', flat=True),
                                    lname__in=same_position_athletes.values_list('lname', flat=True),
                                    dob__in=same_position_athletes.values_list('dob', flat=True),
                                    testtype__in=selected_radar_tests,
                                    datekpi__lte=radar_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
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
                average_radar_results.append({'group': 'position', 'results': test_results})

            # Gender: generate averages in each selected test for athletes of the same gender 
            if "gender_avg" in compare_avg:
                # Queryset of athletes of the same gender not including the current athlete
                same_gender_athletes = AthleteT.objects.filter(gender=gender).exclude(fname=fname, lname=lname, dob=dob).values_list('fname', 'lname', 'dob')
                # Queryset of KPI data for each athlete of the same gender where test type is in the selected tests and datekpi is less than or equal to the specified radar date
                kpi_results = KpiT.objects.filter(fname__in=same_gender_athletes.values_list('fname', flat=True),
                                    lname__in=same_gender_athletes.values_list('lname', flat=True),
                                    dob__in=same_gender_athletes.values_list('dob', flat=True),
                                    testtype__in=selected_radar_tests,
                                    datekpi__lte=radar_date).values('fname', 'lname', 'dob', 'testtype', 'testresult')
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
                average_radar_results.append({'group': 'gender', 'results': test_results})

            # Render the graph if 3 or more tests were selected 
            if len(selected_radar_tests) >= 3:
                Radar_chart = radar_chart(athlete_radar_results, average_radar_results, radar_date)
            else:
                Radar_chart = None
                
        if wellness_count > 0:
            #Access and store all dates
            wellness_dates = (
            WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)
            .values("date")
            .annotate(dcount=Count("date"))
            .order_by("date")
            )

            wellness_most_recent = wellness_dates.last()["date"]

    context = {
        "athleteProf": athleteProf,

        "all_dates": kpi_dates,
        "kpi_earliest": kpi_earliest,
        "kpi_most_recent": kpi_most_recent,
        "kpi_count": kpi_count,
        
        "wellnessReportDates": wellness_dates,
        "mostRecentWellnessReportDate": wellness_most_recent,
        "wellness_count": wellness_count,

        # Radar/Spider
        'Radar_chart': Radar_chart,
        'radar_date': radar_date,
        'all_tests': all_tests,
        'selected_radar_tests': selected_radar_tests,
    }

    return render(request, "html/athleteProf.html", context)
    
@login_required(login_url='/')
def TeamDash(request):
    athletes = TeamT.objects.all()

    context = {"teams": athletes}

    return render(request, "html/teams.html", context)

@login_required(login_url='/')
def recordKPI(request):

    # Define teams
    teams = TeamT.objects.values("sport").order_by("sport").distinct()

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

            # Return the list of athletes
            return JsonResponse({"athletes": list(athletes.values())})
        return JsonResponse({"status": "Invalid request"}, status=400)

    # Other (non-AJAX) requests will recieve a response with a whole HTML document. This requires a page reload.
    #      Is this still being used after we implemented AJAX on this page?
    context = {
        "athletes": athletes,
        "teams": teams,
        "selectedSport": selectedSport,
        "test_types": test_types,
    }

    return render(request, "html/recordKPI.html", context)

@login_required(login_url='/')
def WellnessDash(request):
    athleteProf = AthleteT.objects.all()

    wellnessDates = WellnessT.objects.values("date").order_by("date").distinct()
    wellnessSportsTeams = TeamT.objects.values("sport").order_by("sport").distinct()

    selectedDate = request.POST.get("wellnessdate")
    selectedSport = request.POST.get("sportsteam")

    allWellnessReports = WellnessT.objects.filter(
        date__exact=selectedDate, sportsteam__exact=selectedSport
    )

    context = {
        "athleteProf": athleteProf,
        "wellnessDates": wellnessDates,
        "wellnessSportsTeams": wellnessSportsTeams,
        "allWellnessReports": allWellnessReports,
        "selectedDate": selectedDate,
        "selectedSport": selectedSport,
    }

    return render(request, "html/wellness.html", context)

@login_required(login_url='/')
def AddKPI(request, fname, lname, dob):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

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
        "test_types": test_types,
    }

    return render(request, "html/addkpi.html", context)

@login_required(login_url='/')
def AddWellness(request, fname, lname, dob):
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

    return render(request, "html/addwellness.html", context)
