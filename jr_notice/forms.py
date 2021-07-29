from django.db.models.fields import files
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
import os
from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FilingPartyForm(ModelForm):
    class Meta:
        model = FilingParty
        fields = "__all__"
        exclude = ["user"]


class FileUploadForm(forms.Form):

    def validate_file_extension(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.pdf']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')

    secondary_email = forms.EmailField(required=False)
    file = forms.FileField(max_length=100, validators=[
                           validate_file_extension], label="PDF File")


# class ManuelEntryForm(forms.Form):
#     # APPEAL_TYPES = (
#     #     ("RPD", "RPD"),
#     #     ("RAD", "RAD"),
#     #     ("H&C", "H&C"),
#     #     ("PRRA", "PRRA"),
#     #     ("Deferral",  "Deferral"),
#     #     ("SP", "SP"),
#     #     ("TRV", "TRV"),
#     # )

#     # appeal_type = forms.ChoiceField(choices=APPEAL_TYPES)
#     client_first_name = forms.CharField(max_length=100)
#     client_last_name = forms.CharField(max_length=100)
