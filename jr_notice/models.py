from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, PROTECT
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey


class FilingParty(models.Model):

    REGISTRY_OFFICES = (
        ("Calgary", "Calgary"),
        ("Charlottetown", "Charlottetown"),
        ("Edmonton", "Edmonton"),
        ("Fredericton", "Fredericton"),
        ("Halifax", "Halifax"),
        ("Iqaluit", "Iqaluit"),
        ("Montreal", "Montreal"),
        ("Ottowa", "Ottowa"),
        ("Quebec", "Quebec"),
        ("Regina", "Regina"),
        ("Saint John", "Saint John"),
        ("Saskatoon", "Saskatoon"),
        ("St. John's", "St. John's"),
        ("Toronto", "Toronto"),
        ("Vancouver", "Vancouver"),
        ("Whitehorse", "Whitehorse"),
        ("Winnipeg", "Winnipeg"),
        ("Yellowknife", "Yellowknife"),
    )

    PROVINCES = (
        ("Alberta", "Alberta"),
        ("British Columbia", "British Columbia"),
        ("Manitoba", "Manitoba"),
        ("New Brunswick", "New Brunswick"),
        ("Newfoundland and Labrador", "Newfoundland and Labrador"),
        ("Nova Scotia", "Nova Scotia"),
        ("Nunavut", "Nunavut"),
        ("Ontario", "Ontario"),
        ("Quebec", "Quebec"),
        ("Saskatchewan", "Saskatchewan"),
    )

    LANGUAGES = models.TextChoices('Language', 'English French')

    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    province = models.CharField(max_length=200, choices=PROVINCES)
    postal_code = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    language = models.CharField(max_length=15, choices=LANGUAGES.choices)
    registry_office = models.CharField(
        max_length=200, choices=REGISTRY_OFFICES)

    def __str__(self):
        return self.first_name


class Submission(models.Model):

    APPEAL_TYPES = (
        ("RPD", "RPD"),
        ("RAD", "RAD"),
        ("H&C", "H&C"),
        ("PRRA", "PRRA"),
        ("Deferral",  "Deferral"),
        ("SP", "SP"),
        ("TRV", "TRV"),
    )

    filing_party = models.ForeignKey(FilingParty, on_delete=PROTECT)
    client_first_name = models.CharField(max_length=200)
    client_last_name = models.CharField(max_length=200)
    appeal_type = models.CharField(max_length=200, choices=APPEAL_TYPES)
    submission_date_db = models.DateTimeField(auto_now_add=True, null=True)
    submission_date = CharField(max_length=100, null=True)
    due_date = CharField(max_length=100, null=True)
    secondary_email = models.EmailField(null=True, blank=True)
    confirmation_number = models.CharField(
        max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['-submission_date_db']

    def __str__(self):
        return self.client_first_name + " " + self.client_last_name


class ScanResult(models.Model):

    APPEAL_TYPES = (
        ("RPD", "RPD"),
        ("RAD", "RAD"),
        ("H&C", "H&C"),
        ("PRRA", "PRRA"),
        ("Deferral",  "Deferral"),
        ("SP", "SP"),
        ("TRV", "TRV"),
    )

    filing_party = models.ForeignKey(FilingParty, on_delete=PROTECT)
    date_scanned = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    first_names = models.CharField(max_length=500)
    last_names = models.CharField(max_length=500)
    number_of_applicants = models.IntegerField(null=True)
    app_type = models.CharField(max_length=20, choices=APPEAL_TYPES)
    decision_maker = models.CharField(max_length=255)
    sec_email = models.EmailField(null=True, blank=True)
    scan_errors = models.TextField()
    file_size = models.CharField(max_length=200)
    file_content = models.CharField(max_length=200)
    file_path = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.id


class TimeTook(models.Model):
    submission = ForeignKey(Submission, on_delete=PROTECT)
    time_took = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.submission.id)
