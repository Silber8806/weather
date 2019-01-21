import os

from django import forms

from .models import Customer, Location

DEFAULT_LOCATION=999999

def get_all_location_choices():
	query = Location.objects.exclude(id=DEFAULT_LOCATION).order_by('city','state')

	locations_lst = []

	for result in query:
		if result.id != '999999':
			locations_lst.append(result.city_state)

	locations_lst = tuple([loc for loc in locations_lst])

	return locations_lst


class CustomerForm(forms.Form):
	email = forms.EmailField(label='email',required=True,help_text="email address..")
	location = forms.ChoiceField(label='location',required=True, choices=get_all_location_choices(), help_text="location...")