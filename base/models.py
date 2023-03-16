from django.db import models

class AthleteT(models.Model):
    fname = models.CharField(db_column='Fname', primary_key=True, max_length=30)  # Field name made lowercase.
    lname = models.CharField(db_column='Lname', max_length=30)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=10)  # Field name made lowercase.
    sportsteam = models.CharField(db_column='SportsTeam', max_length=30, blank=True, null=True)  # Field name made lowercase.
    position = models.CharField(db_column='Position', max_length=30, blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=15, blank=True, null=True)  # Field name made lowercase.
    height = models.FloatField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    #upload_to='staticfiles/images'
    image = models.TextField(db_column='Image', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Athlete_T'
        unique_together = (('fname', 'lname', 'dob'),)

    # Overriding the string representation of an athlete to customize output when querying with the interactive shell
    def __str__(self):
        return f"Name:{self.fname} {self.lname} | DOB:{self.dob} | Team:{self.sportsteam} | Position:{self.position} | Year:{self.year} | Height:{self.height}"

class TeamT(models.Model):
    sport = models.CharField(db_column='Sport', primary_key=True, max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team_T'

    # Overriding the string representation of Team to customize output when querying with the interactive shell
    def __str__(self):
        return f"Name:{self.sport}"

class WellnessT(models.Model):
    fname = models.CharField(db_column='Fname', primary_key=True, max_length=30)  # Field name made lowercase.
    lname = models.CharField(db_column='Lname', max_length=30)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=10)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    sportsteam = models.CharField(db_column='SportsTeam', max_length=30, blank=True, null=True)  # Field name made lowercase.
    date = models.CharField(db_column='Date', max_length=10)  # Field name made lowercase.
    position = models.CharField(db_column='Position', max_length=30, blank=True, null=True)  # Field name made lowercase.
    hoursofsleep = models.IntegerField(db_column='HoursOfSleep', blank=True, null=True)  # Field name made lowercase.
    sleepquality = models.IntegerField(db_column='SleepQuality', blank=True, null=True)  # Field name made lowercase.
    breakfast = models.IntegerField(db_column='Breakfast', blank=True, null=True)  # Field name made lowercase.
    hydration = models.IntegerField(db_column='Hydration', blank=True, null=True)  # Field name made lowercase.
    soreness = models.IntegerField(db_column='Soreness', blank=True, null=True)  # Field name made lowercase.
    stress = models.IntegerField(db_column='Stress', blank=True, null=True)  # Field name made lowercase.
    mood = models.IntegerField(db_column='Mood', blank=True, null=True)  # Field name made lowercase.
    image = models.TextField(db_column='Image', max_length=60, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Wellness_T'
        unique_together = (('fname', 'lname', 'dob', 'status', 'date'),)

    # Overriding the string representation of a Wellness survery to customize output when querying with the interactive shell
    def __str__(self):
        return (f"Name:{self.fname} {self.lname} | DOB:{self.dob} | Status:{self.status} | Team:{self.sportsteam} | Date:{self.date} | Position:{self.position} | "
                f"HoursSleep:{self.hoursofsleep} | SleepQuality:{self.sleepquality} | Breakfast:{self.breakfast} | Hydration:{self.hydration} | soreness:{self.soreness} | "
                f"Stress:{self.stress} | Mood:{self.mood} ") 

class KpiT(models.Model):
    fname = models.CharField(db_column='Fname', primary_key=True, max_length=30)  # Field name made lowercase.
    lname = models.CharField(db_column='Lname', max_length=30)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=10)  # Field name made lowercase.
    datekpi = models.CharField(db_column='DateKPI', max_length=10)  # Field name made lowercase.
    testtype = models.CharField(db_column='TestType', max_length=30)  # Field name made lowercase.
    testresult = models.FloatField(db_column='TestResult', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'KPI_T'
        unique_together = (('fname', 'lname', 'dob', 'datekpi', 'testtype'),)

    # Overriding the string representation of a KPI to customize output when querying with the interactive shell
    def __str__(self):
        return f"Name:{self.fname} {self.lname} | DOB:{self.dob} | DateKPI:{self.datekpi} | TestType:{self.testtype} | TestResult:{self.testresult}"