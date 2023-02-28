from django.db import models

class AthleteT(models.Model):
    fname = models.CharField(db_column='Fname', primary_key=True, max_length=30)  # Field name made lowercase.
    lname = models.CharField(db_column='Lname', max_length=30)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=10)  # Field name made lowercase.
    sportsteam = models.CharField(db_column='SportsTeam', max_length=30, blank=True, null=True)  # Field name made lowercase.
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
    gender = models.CharField(db_column='Gender', max_length=7)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team_T'
        unique_together = (('sport', 'tname', 'gender'),)