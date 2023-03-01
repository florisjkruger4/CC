from django.db import models

class AthleteT(models.Model):
    fname = models.CharField(db_column='Fname', primary_key=True, max_length=30)  # Field name made lowercase.
    lname = models.CharField(db_column='Lname', max_length=30)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=10)  # Field name made lowercase.
    sportsteam = models.CharField(db_column='SportsTeam', max_length=30, blank=True, null=True)  # Field name made lowercase.
    position = models.CharField(db_column='Position', max_length=30, blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=15, blank=True, null=True)  # Field name made lowercase.
    height = models.FloatField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    weight = models.FloatField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Athlete_T'
        unique_together = (('fname', 'lname', 'dob'),)


class TeamT(models.Model):
    sport = models.CharField(db_column='Sport', primary_key=True, max_length=30)  # Field name made lowercase.
    tname = models.CharField(db_column='Tname', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team_T'
        unique_together = (('sport', 'tname'),)

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

    class Meta:
        managed = False
        db_table = 'Wellness_T'
        unique_together = (('fname', 'lname', 'dob', 'status', 'date'),)