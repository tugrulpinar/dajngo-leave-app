# Generated by Django 3.2.5 on 2021-07-21 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jr_notice', '0003_auto_20210720_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='filingparty',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='filingparty',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='submission',
            name='confirmation_number',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='due_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='secondary_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='submission_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
