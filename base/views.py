import json
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT, TestTypeT
from .utils import bar_graph, line_graph, radar_chart
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import AthleteForm, ImageForm


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


@login_required(login_url='/')
def Dashboard(request):
    athletes = AthleteT.objects.all()
    teams = TeamT.objects.all()

    # session stuff...
    recentlyViewedAthletes = None
    sessionLength = None

    if 'recently_viewed' in request.session:
        Athletes = AthleteT.objects.filter(id__in=request.session['recently_viewed'])
        recentlyViewedAthletes = sorted(Athletes, key=lambda x: request.session['recently_viewed'].index(x.id))
        sessionLength = len(request.session['recently_viewed'])

    context = {
        'athletes': athletes,
        'teams':teams,
        'recentlyViewedAthletes':recentlyViewedAthletes,
        'sessionLength':sessionLength
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
        form = AthleteForm(request.POST, request.FILES) 

        if form.is_valid():  
            #form.validate_constraints()
            form.save() 

    else:  
        form = AthleteForm()

    context = {
            'form': form,
        }
  
    return render(request, "html/addathlete.html", context)


def kpiAjax(fname, lname, dob, date_one, date_two):

    # init/reset variables to 0 before next use
    kpi_bar = []
    kpi_line = []
    Date1_results = []
    Date2_results = []
    changes = []
    # List of True or False values indicating if a tests minimum score is better
    minBetter_list = []
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
        
        # Checking if the current test type's min is better ([0][0] is just indexing the first element of the list, true or false)
        minBetter = TestTypeT.objects.filter(tname=x).values_list('minbetter')[0][0]
        # Append the current tests minBetter result to the list of minBetter results
        minBetter_list.append(minBetter)

        # Calls matplotlib bar graph with above data
        kpi_line.append(line_graph(results_x, results_y, changes[iter], minBetter))
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
        # List of true or false values for each test type
        "minBetter": list(minBetter_list),
        "kpi_bar": list(kpi_bar),
        "kpi_line": list(kpi_line),
    })

    
def wellnessAjax(fname, lname, dob, wellnessdate):
    
    # Get the appropriate wellness report
    wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob, date=wellnessdate).values()

    # Return the list of athletes
    return JsonResponse({"wellness": list(wellness.values())})
    

@login_required(login_url='/')
def AthleteProf(request, fname, lname, dob, id):

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    # instance of an image in order to edit profile picture... (I have no idea what this means, it took me so long to get it working, if it works, it works. Django documentation says to use ._meta("field name") but that never worked for me)
    instanceImg = AthleteT.objects.filter(id=id).only("image").first()

    Radar_chart = None
    radar_date = None
    all_tests = None
    selected_radar_tests = None

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

        # session stuff...
        recentlyViewedAthletes = None

        if 'recently_viewed' in request.session:
            Athletes = AthleteT.objects.filter(id__in=request.session['recently_viewed'])
            recentlyViewedAthletes = sorted(Athletes, key=lambda x: request.session['recently_viewed'].index(x.id))

            request.session['recently_viewed'].insert(0, id)
            if (len(request.session['recently_viewed']) > 8):
                request.session['recently_viewed'].pop()
        else:
            request.session['recently_viewed'] = [id]

        request.session.modified = True

        kpi_count = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        wellness_count = int(
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).count()
        )

        # We don't have any wellness or kpi data, so just return 
        if kpi_count == 0 and wellness_count == 0:

            # Image handeling for if the is no data in an athletes profile (no kpi records or wellness records)
            if request.method == 'POST':
                form = ImageForm(request.POST, request.FILES, instance=instanceImg)
                if form.is_valid():  
                    #form.validate_constraints()
                    form.save()
                    newImgVal = AthleteT.objects.get(fname=fname, lname=lname, dob=dob).image
                    WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).update(image=newImgVal)
            else:
                form = ImageForm()

            context = {
                "athleteProf": athleteProf,
                "form":form
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
        else: #if there are no kpi records for this athlete but there are wellness records... still loads their page
            kpi_dates = None
            kpi_earliest = None
            kpi_most_recent = None
            kpi_count = None
                
        if wellness_count > 0:
            #Access and store all dates
            wellness_dates = (
            WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)
            .values("date")
            .annotate(dcount=Count("date"))
            .order_by("date")
            )

            wellness_most_recent = wellness_dates.last()["date"]
        else: #if there are no wellness records for this athlete but there are kpi records... still loads their page
            wellness_dates = None
            wellness_most_recent = None

    # Image handeling 
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=instanceImg)
        if form.is_valid():  
            #form.validate_constraints()
            form.save()
            newImgVal = AthleteT.objects.get(fname=fname, lname=lname, dob=dob).image
            WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).update(image=newImgVal)
    else:
        form = ImageForm()

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

        # dashboardd session stuff
        'recentlyViewedAthletes':recentlyViewedAthletes,

        # img form stuff
        'form':form
    }

    return render(request, "html/athleteProf.html", context)
    

@login_required(login_url='/')
def EditAthlete(request, fname, lname, dob, id):
    athlete = AthleteT.objects.get(id=id)

    # deletes entire athlete from database... along with their wellness and kpi records 
    if request.GET.get('delete') == 'delete':
        AthleteT.objects.filter(id=id).delete()
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).delete()
        KpiT.objects.filter(fname=fname, lname=lname, dob=dob).delete()

        return redirect('/athletes')

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
        WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).update(
            fname=editFname,
            lname=editLname,
            dob=editDOB,
            sportsteam=editTeam,
            position=editPosition,
        )
        KpiT.objects.filter(fname=fname, lname=lname, dob=dob).update(
            fname=editFname,
            lname=editLname,
            dob=editDOB,
        )

        return redirect('/athletes')

    context = {
        "athlete": athlete
        }

    return render(request, "html/editathlete.html", context)

    
@login_required(login_url='/')
def TeamDash(request):
    athletes = TeamT.objects.all()

    context = {"teams": athletes}

    return render(request, "html/teams.html", context)


@login_required(login_url='/')
def recordKPI(request):

    # Define teams
    teams = TeamT.objects.values("sport").order_by("sport").distinct()

    # All test type names in the TestTypeT table
    test_types = TestTypeT.objects.values_list('tname', flat=True)

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
    # Is this still being used after we implemented AJAX on this page? - unknown
    # Huh? Is what being used? lol - Floris


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


@login_required(login_url='/')
def WellnessDash(request):

    wellnessDates = WellnessT.objects.values("date").order_by("date").distinct()
    wellnessSportsTeams = TeamT.objects.values("sport").order_by("sport").distinct()

    # If parameter "request" is an XML request (AJAX)...
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # ...AND it's also a POST request...
        if request.method == "POST":

            data = json.load(request)
            selectedDate = data.get("wellnessdate")
            selectedSport = data.get("sportsteam")
            
            athletes = AthleteT.objects.filter(sportsteam__exact=selectedSport)

            all_wellness = {}
            athletes_img = []
            wellness_trends = []

            iter = 0
            for x in athletes:
                wellness_latest = {}

                wellness_relevant = WellnessT.objects.filter(
                    fname=x.fname,
                    lname=x.lname,
                    dob=x.dob,
                    sportsteam=selectedSport,
                    date__lte=selectedDate
                )

                result = wellness_relevant.order_by("date").last()

                athletes_img.append(x.image.url)

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

                if len(wellness_trend_data_x) > 1:
                    wellness_trends.append(line_graph(wellness_trend_data_x, wellness_trend_data_y, 0))
                else:
                    wellness_trends.append(None)
                
            """
            query = "SELECT * FROM Wellness_T WHERE sportsteam = \"Men\'s Swimming\""
            query += " AND (fname, lname, dob, date) IN (SELECT fname, lname, dob, MAX(date)"
            query += " FROM Wellness_T WHERE sportsteam = \"Men\'s Swimming\" GROUP BY fname, lname, dob)"

            results = WellnessT.objects.raw(query)
            """

            return JsonResponse({
                "athletes_img": list(athletes_img),
                "athletes": list(athletes.values("fname", "lname", "dob", "position")),
                "wellness": list(all_wellness.values()),
                "wellness_trends": list(wellness_trends),             
            })
        
        return JsonResponse({"status": "Invalid request"}, status=400)
        
    context = {
        "wellnessDates": wellnessDates,
        "wellnessSportsTeams": wellnessSportsTeams,
    }

    return render(request, "html/wellness.html", context)


@login_required(login_url='/')
def AddKPI(request, fname, lname, dob):

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    # All test type names in the TestTypeT table
    test_types = TestTypeT.objects.values_list('tname', flat=True)

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
        # TestTypeT table tname's
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
