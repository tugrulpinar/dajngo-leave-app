from django.contrib import admin

# Register your models here.
from .models import *

# admin.site.register(FilingParty)
# admin.site.register(Submission)


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 3


class FilingPartyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identity', {'fields': ['first_name', 'last_name']}),
        ('Address', {'fields': [
         'address', 'city', 'province', 'postal_code'], 'classes': ['collapse']}),
        ('Contact', {'fields': ['phone', 'email'], 'classes': ['collapse']}),
        ('Filing Info', {'fields': [
         'language', 'registry_office'], 'classes': ['collapse']})
    ]
    exclude = ['submission_date_db']
    inlines = [SubmissionInline]
    list_display = ('last_name', 'email', 'city')
    list_filter = ['last_name', 'email']
    search_fields = ['last_name', 'email']


admin.site.register(FilingParty, FilingPartyAdmin)
admin.site.register(TimeTook)
