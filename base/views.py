from django.shortcuts import render, redirect
from django.db.models import Q
from .models import AthleteT, TeamT, WellnessT, KpiT
from .utils import bar_graph, line_graph
from django.db.models import Count

def Dashboard(request):

    context = {}

    return render(request, 'html/dashboard.html', context)

def AthletesDash(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    athletes = AthleteT.objects.filter(Q() | Q(fname__icontains=q) | Q(lname__icontains=q) | Q(sportsteam__icontains=q) | Q(position__icontains=q) | Q(year__icontains=q))

    context = {
        'athletes':athletes,
    }
    
    return render(request, 'html/athletes.html', context)

def AddAthlete(request):

    if request.method == 'POST':

        newFname = request.POST['fname']
        newLname = request.POST['lname']
        newGender = request.POST['gender']
        newYear = request.POST['year']
        newHeight = request.POST['height']
        newImage = request.POST['image']
        newDOB = request.POST['dob']
        newTeam = request.POST['sportsteam']
        newPosition = request.POST['position']

        newAthlete = AthleteT(fname=newFname, lname=newLname, gender=newGender, dob=newDOB, sportsteam=newTeam, position=newPosition, year=newYear, height=newHeight, image=newImage)

        newAthlete.validate_constraints()
        newAthlete.save()
        
    return render(request, 'html/addathlete.html')

def AthleteProf(request, fname, lname, dob):

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    numOfKPItests = int( KpiT.objects.filter(fname=fname, lname=lname, dob=dob).count())
    numOfWellnesReports = int(WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).count())

    if numOfKPItests > 0 and numOfWellnesReports > 0:

        img = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob)[0]
        wellness = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).values()
        wellnessReportDates = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob).values('date').annotate(dcount=Count('date')).order_by('date')
        mostRecentWellnessReportDate = wellnessReportDates.last()['date']

        # Groups by test type name for specific athlete profile page
        testType = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values('testtype').annotate(dcount=Count('testtype')).order_by('testtype')

        # Access all dates
        all_dates = KpiT.objects.filter(fname=fname, lname=lname, dob=dob).values('datekpi').distinct()

        # Takes user input through Django form (Wellness date selection)
        wellness_date = request.POST.get("wellnessdate")
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

        # Wellness Date selection
        if (wellness_date):
            mostRecentWellnessReport = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob, date__exact=wellness_date).values()
        else:
            mostRecentWellnessReport = WellnessT.objects.filter(fname=fname, lname=lname, dob=dob, date__exact=mostRecentWellnessReportDate).values()

        # Date 1 test score result
        if (date_one):
            TenYd_Date1_result = TenYdSprint_results.order_by('datekpi').first()
            Bench1RM_Date1_result = Bench1RM_results.order_by('datekpi').first()
            CMJ_Date1_result = CMJ_results.order_by('datekpi').first()
        else:
            TenYd_Date1_result = None
            Bench1RM_Date1_result = None
            CMJ_Date1_result = None

        # Date 2 test score result 
        if (date_two):
            TenYd_Date2_result = TenYdSprint_results.order_by('datekpi').last()
            Bench1RM_Date2_result = Bench1RM_results.order_by('datekpi').last()
            CMJ_Date2_result = CMJ_results.order_by('datekpi').last()
        else:
            TenYd_Date2_result = None
            Bench1RM_Date2_result = None
            CMJ_Date2_result = None
        
        context = {
            'athleteProf':athleteProf,
            'numOfKPItests':numOfKPItests,
            'numOfWellnesReports':numOfWellnesReports,

            'img':img,
            'wellness':wellness,
            'wellnessReportDates':wellnessReportDates,
            'mostRecentWellnessReportDate':mostRecentWellnessReportDate,
            'wellness_date':wellness_date,
            'mostRecentWellnessReport':mostRecentWellnessReport,

            'testType':testType,

            'all_dates':all_dates,

            'TenYdSprint_results':TenYdSprint_results,
            'TenYd_chart':TenYd_chart,
            'TenYd_chart_line':TenYd_chart_line,
            'TenYd_y':TenYd_y,
            'TenYd_Date1_result':TenYd_Date1_result,
            'TenYd_Date2_result':TenYd_Date2_result,

            'Bench1RM_results':Bench1RM_results,
            'Bench1RM_chart':Bench1RM_chart,
            'Bench1RM_chart_line':Bench1RM_chart_line,
            'Bench1RM_y':Bench1RM_y,
            'Bench1RM_Date1_result':Bench1RM_Date1_result,
            'Bench1RM_Date2_result':Bench1RM_Date2_result,

            'CMJ_results':CMJ_results,
            'CMJ_chart':CMJ_chart,
            'CMJ_chart_line':CMJ_chart_line,
            'CMJ_y':CMJ_y,
            'CMJ_Date1_result':CMJ_Date1_result,
            'CMJ_Date2_result':CMJ_Date2_result,

            'date_one':date_one,
            'date_two':date_two,
        }

        return render(request, 'html/athleteProf.html', context)
    
    else:
        context = {
            'athleteProf':athleteProf,
        }

        return render(request, 'html/athleteProf.html', context)


def TeamDash(request):

    athletes = TeamT.objects.all()

    context = {
        'teams':athletes
    }
    
    return render(request, 'html/teams.html', context)

def recordKPI(request):

    context = {}

    return render(request, 'html/recordKPI.html', context)

def WellnessDash(request):

    athleteProf = AthleteT.objects.all()

    wellnessDates = WellnessT.objects.values('date').order_by('date').distinct()
    wellnessSportsTeams = TeamT.objects.values('sport').order_by('sport').distinct()

    selectedDate = request.POST.get("wellnessdate")
    selectedSport =  request.POST.get("sportsteam")

    allWellnessReports = WellnessT.objects.filter(date__exact=selectedDate, sportsteam__exact=selectedSport)

    context = {
        'athleteProf':athleteProf,
        'wellnessDates':wellnessDates,
        'wellnessSportsTeams':wellnessSportsTeams,
        'allWellnessReports':allWellnessReports,

        'selectedDate':selectedDate,
        'selectedSport':selectedSport,
    }

    return render(request, 'html/wellness.html', context)

def AddWellness(request, fname, lname, dob):

    athleteProf = AthleteT.objects.get(fname=fname, lname=lname, dob=dob)

    Fname = fname
    Lname = lname
    DOB = dob

    Sports = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values('sportsteam')
    for x in Sports:
        SportsTeam = x['sportsteam']

    Positions = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values('position')
    for x in Positions:
        Position = x['position']

    Images = AthleteT.objects.filter(fname=fname, lname=lname, dob=dob).values('image')
    for x in Images:
        Img = x['image']

    if request.method == 'POST':
        newhoursofsleep = request.POST['hoursofsleep']
        newsleepquality = request.POST['sleepquality']
        newbreakfast = request.POST['breakfast']
        newhydration = request.POST['hydration']
        newsoreness = request.POST['soreness']
        newstress = request.POST['stress']
        newmood = request.POST['mood']
        newstatus = request.POST['status']
        newdate = request.POST['date']

        newWellness = WellnessT(fname=Fname, lname=Lname, dob=DOB, status=newstatus, sportsteam=SportsTeam, date=newdate, position=Position, hoursofsleep=newhoursofsleep, sleepquality=newsleepquality, breakfast=newbreakfast, hydration=newhydration, soreness=newsoreness, stress=newstress, mood=newmood, image=Img)

        newWellness.validate_constraints()
        newWellness.save()

    context = {
        'athleteProf':athleteProf,
    }

    return render(request, 'html/addwellness.html', context)

