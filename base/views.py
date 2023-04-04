import json
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import bar_graph, line_graph, radar_chart
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def LoginRegister(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try: 
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')

    context = {}
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


def Dashboard(request):
    athletes = AthleteT.objects.all()

    context = {
        "athletes": athletes,
    }

    return render(request, "html/dashboard.html", context)


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


def AthleteProf(request, fname, lname, sportsteam, position, gender, dob):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    # List of KPI table rows
    kpi_list = KpiT.objects.filter(fname=fname, lname=lname, dob=dob)
    kpi_count = len(kpi_list)

    # init / clear list
    kpi_test_data = []

    # ------------ KPI -------------

    if kpi_count > 0:
        # Access and store all dates
        all_dates = (
            KpiT.objects.filter(fname=fname, lname=lname, dob=dob)
            .values("datekpi")
            .order_by("datekpi")
            .distinct()
        )

        # Gets earlies and latest kpi dates for specific athlete
        kpi_earliest = all_dates.first()["datekpi"]
        kpi_most_recent = all_dates.last()["datekpi"]

        if request.method == "POST":
            # Takes user input through a Django form (in this case it takes the "select" option when user hits submit form btn)
            date_one = request.POST.get("date1")
            date_two = request.POST.get("date2")
        else:
            date_one = kpi_earliest
            date_two = kpi_most_recent

        # Groups by test type name for specific athlete profile page
        # Only gets test types within selected date range
        test_type = (
            KpiT.objects.filter(
                fname=fname, lname=lname, dob=dob, datekpi__range=(date_one, date_two)
            )
            .values_list("testtype", flat=True)
            .order_by("testtype")
            .distinct()
        )

        # init/reset variables to 0 before next use
        kpi_bar = 0
        kpi_line = 0
        Date1_result = 0
        Date2_result = 0
        change = 0

        for x in test_type:
            # Gets the rows for this test for specific athlete
            kpi_results = KpiT.objects.filter(
                fname=fname,
                lname=lname,
                dob=dob,
                testtype__exact=x,
                datekpi__range=(date_one, date_two),
            )

            # Sets x and y coordinate values
            results_x = [x.datekpi for x in kpi_results]
            results_y = [x.testresult for x in kpi_results]

            # Date 1 test score result
            if date_one:
                Date1_result = kpi_results.order_by("datekpi").first()

                if Date1_result:
                    Date1_result = Date1_result.testresult

            else:
                Date1_result = None

            # Date 2 test score result
            if date_two:
                Date2_result = kpi_results.order_by("datekpi").last()

                if Date2_result:
                    Date2_result = Date2_result.testresult

            else:
                Date2_result = None

            # If both give values (not null), calculate difference betweeen them
            if Date1_result and Date2_result:
                change = Date2_result - Date1_result
                change = round(change, 2)

            # Calls matplotlib bar graph with above data
            kpi_bar = bar_graph(results_x, results_y)
            kpi_line = line_graph(results_x, results_y, change)

            # Put all info being transferred to front end into tuple
            # 'x' is test type
            kpi_single = [x, kpi_bar, kpi_line, Date1_result, Date2_result, change]

            # Add KPI tuple to list of tuples
            kpi_test_data.append(kpi_single)

    # This code generates a radar/spider chart to display the latest KPI results for an athlete given a date
    if kpi_count > 2:    
        # All tests the athlete has taken
        all_tests = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values_list('testtype', flat=True).distinct()

        if request.method == "POST":
            # Selected KPI date
            radar_date = request.POST.get("radar_date")
            selected_radar_tests = request.POST.getlist('selected_radar_tests')
        else:
            radar_date = kpi_most_recent
            selected_radar_tests = all_tests

        # Athletes results for selected KPI's and Date
        athlete_radar_results = []
        for test in selected_radar_tests:
            # Get the kpi result <=/lte to the given date
            athlete_radar_results.append(KpiT.objects.filter(fname=fname, lname=lname, dob=dob, datekpi__lte=radar_date, testtype=test).order_by('datekpi').values_list('testresult', flat=True).first())

        # List specifying which averages to comapre to (Team, Position, or Gender)
        compare_avg = request.POST.getlist('compare_avg')

        # Gender (just returns athletes of the same team and position for now)
        if "gender_avg" in compare_avg:
            same_gender_athletes = AthleteT.objects.filter(gender=gender).exclude(fname=fname, lname=lname, dob=dob).values_list('fname', 'lname', 'dob')
            # same_gender_ruslts = []
            # for athlete in same_gender_athletes:
            #     fname, lname, dob = athlete
            #     for test in selected_radar_tests:
            #         same_gender_ruslts.append(KpiT.objects.filter(fname=fname, lname=lname, dob=dob, testtype=test, datekpi__lte=radar_date))

        # Position (just returns athletes of the same team and position for now)
        if "position_avg" in compare_avg:
            same_position_athletes = AthleteT.objects.filter(sportsteam=sportsteam, position=position).exclude(fname=fname, lname=lname, dob=dob).values_list('fname', 'lname', 'dob')

        # Sportsteam (just returns athletes of the same team and position for now)
        if "team_avg" in compare_avg:
            teammates = AthleteT.objects.filter(sportsteam=sportsteam).exclude(Q(fname=fname) & Q(lname=lname) & Q(dob=dob)).values_list('fname', 'lname', 'dob')

        # Render the graph if more than 2 graphs were selected 
        if len(selected_radar_tests) > 2:
            Radar_chart = radar_chart(selected_radar_tests, athlete_radar_results, radar_date)
        else:
            Radar_chart = None

    else:
        context = {
            "athleteProf": athleteProf,
        }

        return render(request, "html/athleteProf.html", context)

    # ------------ Wellness -------------

    wellness_count = int(
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).count()
    )

    if wellness_count > 0:
        wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).values()
        wellness_dates = (
            WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)
            .values("date")
            .annotate(dcount=Count("date"))
            .order_by("date")
        )
        wellness_most_recent = wellness_dates.last()["date"]

        # Takes user input through Django form (Wellness date selection)
        wellness_date = request.POST.get("wellnessdate")

        # Wellness Date selection
        if wellness_date:
            mostRecentWellnessReport = WellnessT.objects.filter(
                fname=fname, lname=lname, dob=dob, date__exact=wellness_date
            ).values()
        else:
            mostRecentWellnessReport = WellnessT.objects.filter(
                fname=fname, lname=lname, dob=dob, date__exact=wellness_most_recent
            ).values()

    else:
        context = {
            "athleteProf": athleteProf,
        }

        return render(request, "html/athleteProf.html", context)

    context = {
        "athleteProf": athleteProf,
        "numOfKPItests": kpi_count,
        "prev_val": Date1_result,
        "latest_val": Date2_result,
        "all_dates": all_dates,
        "kpi_test_data": kpi_test_data,
        "kpi_earliest": kpi_earliest,
        "kpi_most_recent": kpi_most_recent,
        "numOfWellnesReports": wellness_count,
        "wellness": wellness,
        "wellnessReportDates": wellness_dates,
        "mostRecentWellnessReportDate": wellness_most_recent,
        "wellness_date": wellness_date,
        "mostRecentWellnessReport": mostRecentWellnessReport,
        # Radar/Spider
        'Radar_chart': Radar_chart,
        'radar_date': radar_date,
        'all_tests': all_tests,
        'selected_radar_tests': selected_radar_tests,
    }

    return render(request, "html/athleteProf.html", context)


def TeamDash(request):
    athletes = TeamT.objects.all()

    context = {"teams": athletes}

    return render(request, "html/teams.html", context)


def recordKPI(request):
    teams = TeamT.objects.values("sport").order_by("sport").distinct()

    selectedSport = ""
    athletes = []

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if request.method == "POST":
            data = json.load(request)
            selectedSport = data.get("sportsteam")

            athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport).values(
                "fname", "lname"
            )

            return JsonResponse({"athletes": list(athletes.values())})
        return JsonResponse({"status": "Invalid request"}, status=400)

    context = {
        "athletes": athletes,
        "teams": teams,
        "selectedSport": selectedSport,
        "test_types": test_types,
    }

    return render(request, "html/recordKPI.html", context)


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
