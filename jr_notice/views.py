from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.forms import inlineformset_factory
from .pdf_recognizer import PdfRecognizer
from .e_file import efile_jr_notice

# Create your views here.
from .models import *
from .forms import *
from .decorators import unauthenticated_user
from django.urls import reverse
import boto3
import time
import os
import io

from rq import Queue, Retry
from .worker import conn

q = Queue(connection=conn)


def upload_aws_s3(file_to_upload, user_id, file_name):
    # Connect to AWS S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ["aws_id"],
        aws_secret_access_key=os.environ["aws_key"])

    try:
        # upload a file-like object
        s3_client.upload_fileobj(
            file_to_upload, "leaveapp", f"{user_id}/{file_name}")

    except Exception as e:
        print("Error ", e)
        return


@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # create a filingparty and link with user
            FilingParty.objects.create(user=user, email=email)
            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'jr_notice/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'jr_notice/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):

    try:
        # get all the submissions by the user by descending order
        submissions = request.user.filingparty.submission_set.all().order_by(
            "-submission_date_db")
    except:
        pass

    # redirect to the account page if filing party info is incomplete
    if not request.user.filingparty.city:
        return redirect('account')

    total_submissions = submissions.count()
    # confirmed_submissions = total_submissions.filter(
    #     status='Confirmed').count()
    # pending_submissions = total_submissions.filter(status='Pending').count()

    pending_submissions = 0
    confirmed_submissions = submissions.count()

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():

            # get the file in memory
            file = request.FILES['file']
            secondary_email = request.POST["secondary_email"]

            # save the file on disk - until we find a better solution
            fs = FileSystemStorage()
            file_name = "{}_{}".format(request.user.filingparty.id, file.name)
            fs.save(file_name, file)

            file_path = os.path.join(
                os.getcwd(), "jr_notice", "static", "jr_notice", "pdf", file_name)

            # convert the bytes into file-like object
            file.seek(0)
            file_object = io.BytesIO(file.read())

            # perform pdf recognition
            try:
                pdf_rec = PdfRecognizer(file_object)
                pdf_rec.scan()
                if pdf_rec.applicant_names and pdf_rec.applicant_lastnames:
                    # These two come as iterables, we need to convert these to string
                    app_first_names = ",".join(pdf_rec.applicant_names)
                    app_last_names = ",".join(pdf_rec.applicant_lastnames)
            except Exception as e:
                print(e)
                print("Could not scan the document")

            # enter the scan result into db
            scan_result = request.user.filingparty.scanresult_set.create(first_names=app_first_names,
                                                                         last_names=app_last_names,
                                                                         number_of_applicants=pdf_rec.number_of_applicants,
                                                                         app_type=pdf_rec.application_type,
                                                                         decision_maker=pdf_rec.decision_maker,
                                                                         sec_email=secondary_email,
                                                                         scan_errors=pdf_rec.errors,
                                                                         file_size=file.size,
                                                                         file_content=file.content_type,
                                                                         file_path=file_path)

            # if there's more than 6 applicants there's probably an error
            # redirect to manuel entry
            if len(pdf_rec.applicant_names) >= 6:
                return redirect('manuel-entry', scan_id=scan_result.id)

            file_object.close()
            # create a delay effect to show JS
            time.sleep(1.5)
            return HttpResponseRedirect(reverse('scan-result', args=(scan_result.id,)))

    # we ask sec_email and pdf_file
    upload_form = FileUploadForm()

    context = {'submissions': submissions, 'upload_form': upload_form,
               'total_submissions': total_submissions,
               'confirmed_submissions': confirmed_submissions,
               'pending_submissions': pending_submissions}

    return render(request, 'jr_notice/dashboard.html', context)


@ login_required(login_url='login')
def scanResult(request, scan_id):

    scan_result_info = get_object_or_404(ScanResult, id=scan_id)

    if "," in scan_result_info.first_names:
        first_names = scan_result_info.first_names.split(",")
    else:
        first_names = [scan_result_info.first_names]

    if "," in scan_result_info.last_names:
        last_names = scan_result_info.last_names.split(",")
    else:
        last_names = [scan_result_info.last_names]

    full_names = tuple(zip(first_names, last_names))

    if request.method == "POST":
        # scan_result_info = ScanResult.objects.get(id=scan_id)
        # filing_party_info = request.user.filingparty

        filing_party_info = get_object_or_404(
            FilingParty, user_id=request.user.id)

        # app_first_names = scan_result_info.first_names.split(",")
        # app_last_names = scan_result_info.last_names.split(",")

        # efile_jr_notice(scan_result_info.number_of_applicants,
        #                 first_names,
        #                 last_names,
        #                 scan_result_info.app_type,
        #                 filing_party_info,
        #                 scan_result_info.file_path,
        #                 scan_result_info.sec_email,
        #                 filing_party_info.id)

        job_result = q.enqueue(efile_jr_notice, scan_result_info.number_of_applicants,
                               first_names,
                               last_names,
                               scan_result_info.app_type,
                               filing_party_info,
                               scan_result_info.file_path,
                               scan_result_info.sec_email,
                               filing_party_info.id, retry=Retry(max=1))

        # os.remove(scan_result_info.file_path)
        return redirect('home')

    context = {'ledger': scan_result_info,
               "full_names": full_names, "scan_id": scan_id}
    return render(request, 'jr_notice/scan_result.html', context)


@ login_required(login_url='login')
def manuelEntry(request, scan_id):

    ManuelEntryFormSet = inlineformset_factory(
        FilingParty,
        ScanResult,
        fields=("first_names", "last_names"),
        extra=3)

    filing_party = request.user.filingparty
    formset = ManuelEntryFormSet(queryset=ScanResult.objects.none(),
                                 instance=filing_party)

    if request.method == "POST":
        # I need the validation but I dont want to the user to choose the appeal type for each applicant
        # when the form gives error, display it
        if formset.is_valid():

            appeal_type = request.POST["appeal_type"]
            first_names = []
            last_names = []

            length = int(request.POST['scanresult_set-TOTAL_FORMS'])

            for x in range(length):
                first_names.append(
                    request.POST[f"scanresult_set-{x}-first_names"])
                last_names.append(
                    request.POST[f"scanresult_set-{x}-last_names"])

            first_names_cleaned = [item.strip()
                                   for item in first_names if item]
            last_names_cleaned = [item.strip() for item in last_names if item]

            number_of_applicants = len(last_names_cleaned)

            scan_result_info = get_object_or_404(ScanResult, id=scan_id)
            filing_party_info = get_object_or_404(
                FilingParty, user_id=request.user.id)

            efile_jr_notice(number_of_applicants,
                            first_names_cleaned,
                            last_names_cleaned,
                            appeal_type,
                            filing_party_info,
                            scan_result_info.file_path,
                            scan_result_info.sec_email,
                            filing_party_info.id)

            # formset = ManuelEntryFormSet(request.POST, instance=filing_party)
            # if formset.is_valid():
            #     print(request.POST)
            #     print(type(request.POST))
            #     formset.save()

            return redirect("home")

    context = {"form": formset, "scan_id": scan_id}
    return render(request, "jr_notice/manuel_entry.html", context)


@ login_required(login_url='login')
def accountSettings(request):
    filing_party_info = get_object_or_404(
        FilingParty, user_id=request.user.id)
    form = FilingPartyForm(instance=filing_party_info)

    if request.method == 'POST':
        form = FilingPartyForm(request.POST, instance=filing_party_info)
        if form.is_valid():
            form.save()

        return redirect('account')

    context = {'form': form}
    return render(request, 'jr_notice/account_settings.html', context)
