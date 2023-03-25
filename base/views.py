from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import bar_graph, line_graph
from django.db.models import Count


def Dashboard(request):
    context = {}

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
        newYear = request.POST["year"]
        newHeight = request.POST["height"]
        newImage = request.POST["image"]
        newDOB = request.POST["dob"]
        newTeam = request.POST["sportsteam"]
        newPosition = request.POST["position"]

        newAthlete = AthleteT(
            fname=newFname,
            lname=newLname,
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


def AthleteProf(request, fname, lname, dob):
    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)
    img = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)[0]

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
            .distinct()
        )

        # Takes user input through a Django form (in this case it takes the "select" option when user hits submit form btn)
        date_one = request.POST.get("date1")
        date_two = request.POST.get("date2")

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

        for x in test_type:
            # init/reset variables to 0 before next use
            kpi_bar = 0
            kpi_line = 0
            Date1_result = 0
            Date2_result = 0
            change = 0

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
            kpi_single = [x, kpi_bar, kpi_line, Date1_result, Date2_result, change]

            # Add KPI tuple to list of tuples
            kpi_test_data.append(kpi_single)

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
        "img": img,
        "numOfKPItests": kpi_count,
        "prev_val": Date1_result,
        "latest_val": Date2_result,
        "all_dates": all_dates,
        "kpi_test_data": kpi_test_data,
        "numOfWellnesReports": wellness_count,
        "wellness": wellness,
        "wellnessReportDates": wellness_dates,
        "mostRecentWellnessReportDate": wellness_most_recent,
        "wellness_date": wellness_date,
        "mostRecentWellnessReport": mostRecentWellnessReport,
    }

    return render(request, "html/athleteProf.html", context)


def TeamDash(request):
    athletes = TeamT.objects.all()

    context = {"teams": athletes}

    return render(request, "html/teams.html", context)


def recordKPI(request):
    teams = TeamT.objects.values("sport")
    
    context = {
        "teams": teams,
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
