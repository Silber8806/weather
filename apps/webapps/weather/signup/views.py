from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .models import Customer, Location
from .forms import CustomerForm
from .util import normalize_email

def index(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        render_dict = {'form': form}
    else:
        form = CustomerForm()
        render_dict = {'form': form}

    if request.method == "POST":
        if form.is_valid():
            email = normalize_email(form.cleaned_data['email'])
            location = form.cleaned_data['location']
            try:
                customer_location = Location.objects.get(id = location)
                new_customer = Customer(email = email, location = customer_location)
                new_customer.save()
                return HttpResponseRedirect(reverse('signup:confirm'))
            except IntegrityError as e:
                render_dict['error'] = 'Email must be unique...'
                return render(request, 'signup/index.html', render_dict )
            except ObjectDoesNotExist as e: 
                render_dict['error'] = 'Location currently not available'
                return render(request, 'signup/index.html', render_dict )

        if not form.is_valid():
            return HttpResponseBadRequest("Validation Error")

    if ( request.method != "POST"):
        return render(request, 'signup/index.html',{'form': form})

def confirm(request):
    return render(request, 'signup/confirm.html')