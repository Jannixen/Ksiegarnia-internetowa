from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render

from store.models import Complaint


@login_required
def complaint_details(request, complaint_id):
    try:
        chosen_complaint = Complaint.objects.get(pk=complaint_id)
    except ObjectDoesNotExist:
        messages.info(request, "Reklamacja nie istnieje bądź nie masz do niej dostępu")
        return HttpResponseRedirect('/')
    if request.user == chosen_complaint.user:
        context = {'complaint': chosen_complaint}
        return render(request, "complaint_detail.html", context)
    else:
        messages.info(request, "Reklamacja nie istnieje bądź nie masz do niej dostępu")
        return HttpResponseRedirect('/')
