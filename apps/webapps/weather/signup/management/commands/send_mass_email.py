import sys
import os
import math
import pytz
import us
import requests
import urllib
import logging
import json

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import sendgrid
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from sendgrid.helpers.mail import *

from signup.models import Customer, Location

# means location was deleted from database
DEFAULT_LOCATION=999999

def now(timezone):
    """ get time at timezone """
    tz = pytz.timezone(timezone)
    now_time = datetime.now(tz).date()
    return now_time

def format_json(content):
    """ format json for easy printing debug util"""
    return json.dumps(content, indent=4, sort_keys=True)

class Command(BaseCommand):
    help = 'Sends a mass email to all customers in the Customer table'

    """ 
    go through all locations with at least one customer.
    query weatherbit api to find current temperature in each location.
    if a current weather temperature is found, try to find temp 7 days ago.

    send an e-mail based on the below situations:
    > good weather: current temperature is > 5 degrees from 7 days ago or skies are clear
    > bad weather: weather is rain, snow or some kind of precipitation or 5 degrees lower then 7 days ago.
    > normal weather: weather doesn't meet the above cases.

    if no weather could be found or we deleted a location for a customer, send a generic email.
    """

    def handle(self, *args, **options):

        url_attempts = 2

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        customers = Customer.objects.all()

        # get all unique locations
        locations = list(set([loc.location for loc in customers if loc.location.id != DEFAULT_LOCATION]))
        location_json = {}

        # define email subject
        email_template = dict()
        email_template['good'] = "It's nice out! Enjoy a discount on us."
        email_template['normal'] = "Enjoy a discount on us."
        email_template['bad'] = "Not so nice out? That's okay, enjoy a discount on us."

        for loc in locations:

            # location id, city_state name
            loc_id = loc.id
            _id, city_state = loc.city_state

            # weatherbit_key
            attempts=0
            request_status=0
            current_base_url = 'https://api.weatherbit.io/v2.0/current'
            current_url = current_base_url + "?city=" + urllib.quote(city_state) + "&units=I" + "&key=" + settings.WEATHERBIT_KEY

            #default email type: [bad, normal, good] weather.
            email_type="normal"

            if (loc_id == DEFAULT_LOCATION):
                # just in case we end up snagging default (shouldn't happen)
                print("send only default emails")
                continue

            # call http for current weather
            while (request_status != 200 and attempts <= url_attempts):
                attempts = attempts + 1
                print "current attempt({}) {}".format(attempts,current_url)
                current_response = requests.get(current_url)
                print "current status_code: {}".format(current_response.status_code)

                request_status = current_response.status_code

                if (request_status == 200):
                    weather_info = json.loads(current_response.content)
                    request_count = weather_info['count']
                    # if multiple results... return status 999 and handle later
                    if (request_count != 1):
                        request_status = 999
                    else:
                        # retrieve contents from returned JSON
                        request_temp = weather_info['data'][0]['temp']
                        request_weather_type = weather_info['data'][0]['weather']['description']
                        request_weather_code = int(weather_info['data'][0]['weather']['code'])
                        if (request_weather_code < 700 or request_weather_code >= 900):
                            email_type = 'bad'
                        elif (request_weather_code == 800):
                            email_type = 'good'
                        else:
                            email_type = 'normal'
                        request_observiation_time = weather_info['data'][0]['ts']

            # create a record for each successful current temp found
            if (request_status == 200):
                location_record = {'temp':request_temp, \
                    'email_type': email_type, \
                    'weather': request_weather_type, \
                    'weather_code': request_weather_code, \
                    'observation_time': request_observiation_time}
                location_json[city_state]=location_record

            # if successful probe for history...
            if (request_status == 200):
                current_time = now(loc.timezone)
                end_date=(current_time - timedelta(days=7))
                start_date=(end_date + timedelta(days=1))
                start_date=start_date.strftime('%Y-%m-%d')
                end_date=end_date.strftime('%Y-%m-%d')

                # weatherbit weather 7 days ago
                history_base_url = 'https://api.weatherbit.io/v2.0/history/daily'
                history_url = history_base_url + \
                    "?city=" + urllib.quote(city_state) + \
                    "&start_date=" + end_date + \
                    "&end_date=" + start_date + \
                    "&units=I" + \
                    "&key=" + settings.WEATHERBIT_KEY

                attempts=0
                request_status=0

                # try to retreive history weather
                while (request_status != 200 and attempts <= url_attempts):
                    attempts = attempts + 1
                    print "current attempt({}) {}".format(attempts,history_url)
                    history_response = requests.get(history_url)
                    print "current status_code: {}".format(history_response.status_code) 

                    request_status = history_response.status_code  

                    if (request_status == 200):
                        history_info = json.loads(history_response.content)
                        history_temp = history_info['data'][0]['temp']

                if (request_status == 200):
                    location_record = location_json.get(city_state,{})
                    location_record.update({"past_temp":history_temp})

                print("location json:")
                print(location_json)
                print("")
                print("location record")
                print(location_record)
                print("")
                print("email_type (before):")
                print(email_type)

                # check if temperature was colder or hotter 7 days ago.
                if (location_record.get("email_type","normal") == "normal" \
                    and location_record.has_key("past_temp")):
                    temp_diff = location_record["temp"] - location_record["past_temp"] 
                    if (temp_diff >= 5):
                        email_type="good"
                    elif (temp_diff <= -5):
                        email_type="bad"
                    else:
                        email_type="normal"
                    location_json[city_state].update({"email_type":email_type})

            # set up email client...
            customers = loc.customer_set.all()
            location_record = location_json.get(city_state,{})

            for customer in customers:
                # set up email settings...

                temp = location_record.get("temp",None)
                history_temp = location_record.get("past_temp",None)
                email_type = location_record.get("email_type","normal")
                weather = location_record.get("weather",None)
                observiation_time = location_record.get("observation_time",now(loc.timezone))

                from_email = Email(settings.FROM_EMAIL)
                to_email = Email(customer.email)
                subject = email_template[email_type]

                if (weather is not None):
                    weather = weather.lower()
                
                # all the different email combinations
                # can't get temperature or multiple cities case...
                if (temp is None):
                    message="We hope you enjoy your time in {} have this great coupon on us!".format(city_state)
                    content = Content("text/plain",message)
                # we got temperature, but not historical data...
                elif (history_temp is None):
                    if (email_type == "good"):
                        message = "Great Weather in {} deserves a great discount!  Enjoy your {} weather ({} F)!".format(city_state,weather,temp)
                        content = Content("text/plain",message)
                    elif (email_type == "bad"):
                        message = "Weather looks dreadful in {}! Let's cheer you up with a discount!  Hope the {} weather ({} F) improves!".format(city_state,weather,temp)
                        content = Content("text/plain",message)
                    else:
                        message = "Weather seems mild in {}, not our great discounts!  Hope the {} weather ({} F) improves!".format(city_state,weather,temp)
                        content = Content("text/plain",message)
                # we have historical data...
                elif (history_temp):
                    diff_temp = round(float(temp - history_temp),2)
                    if (email_type == "good"):
                        message = "Weather seems to be great in {}, so are our discounts!  Enjoy your {} weather ({} F: a change of  {} F)!".format(city_state,weather,temp,diff_temp)
                        content = Content("text/plain",message)
                    elif (email_type == "bad"):
                        message = "Brrr...weather doesn't seem so nice in {}, but our discounts are!  Hope the {} weather ({} F: a change of  {} F) improves!".format(city_state,weather,temp,diff_temp)
                        content = Content("text/plain",message)
                    else:
                        message = "Weather seems mild in {}, not our great discounts!  Hope the {} weather ({} F: a change of  {} F) improves!".format(city_state,weather,temp,diff_temp)    
                        content = Content("text/plain",message)
                # try to send the email...          
                print("subject:")
                print(subject)
                print("contents:")
                print(message)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())

        customers = Customer.objects.filter(location__id=DEFAULT_LOCATION)

        # customers without locations due to deletes...send default email
        for orphan_customer in customers:
            from_email = Email(settings.FROM_EMAIL)
            to_email = Email(customer.email)     
            subject = email_template["normal"]
            content = Content("text/plain","We hope you enjoy this great coupon on us!")

            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

  

