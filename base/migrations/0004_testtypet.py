# Generated by Django 4.1.7 on 2023-03-31 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_kpit'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestTypeT',
            fields=[
                ('tname', models.CharField(db_column='Tname', max_length=30, primary_key=True, serialize=False)),
                ('minbetter', models.BooleanField(db_column='MinBetter')),
            ],
            options={
                'db_table': 'TestType_T',
                'managed': False,
            },
        ),
    ]
