# Weather-based E-mail 

Simple application that runs a weather-based e-mail subscription service (Django) for the top 100 most populous US cities.  Django manager has a command send_mass_email that will send e-mails to customers based on their current weather compared to 7-days ago (generic e-mail if current temperature can't be found).

Base commands:

Run webserver:
```bash
python manage.py runserver 
```

Send mass e-mails (via sendgrid):
```bash
python manage.py send_mass_email 
```

## Installing 

How to set-up development environment (will dockerize later)

1. Install python 2.7
2. Install requirements in file: pip install -r ./weather/settings/requirements/base.txt
3. Install postgres
4. Create a database and user for this system.
5. Sign-up for Weatherbit api (https://www.weatherbit.io/account/create)
6. Sign-up for Sendgrid (https://signup.sendgrid.com/)
7. create a env with the following settings:

```
# This is a template for environment file...

# django secret key
export SECRET_KEY=''

# weatherbit api key
export WEATHERBIT_KEY=''

# sendgrid api key
export SENDGRID_API_KEY=''

# email you are sending from
export EMAIL_FROM=''

# postgres database settings
export DB_NAME=''
export DB_USER=''
export DB_PASSWORD=''
export DB_HOST=''
```

Note: I place in ./apps/webapps/weather/weather/settings/sys_vars/base.env

8. source the environment file above.
9. run:

```bash
source run.sh dev 1
```

To start postgres and load the top 100 us cities by population.

10. navigate to ./apps/webapps/weather/ and type:

```bash
python manage.py makemigrations
python manage.py migrate
```

11. start webserver

```bash
python manage.py runserver
```

This should start the subscription service at:

http:127.0.0.1:8000/signup

12. sign-up for any number of e-mail subscriptions.  Note e-mails must be unique.
13. To send mass e-mails:

```bash
python manage.py send_mass_email
```

This will go through all locations with customers, get the current weather and historic weather.  It will calculate if 
the weather is good (clear skies or 5 degrees warmer than 7 days ago) or bad (rain/snow or 5 degrees lower than 7 days ago).
It will then send a custom e-mail regarding the weather (just text-based, nothing fancy).

If a location can't retrieve temperature or the location was deleted, it sends a generic discount email.

### Prerequisites

1. python 2.7
2. python libraries (below):
```
backports.functools-lru-cache==1.5
beautifulsoup4==4.7.1
bs4==0.0.1
certifi==2018.11.29
chardet==3.0.4
Django==1.11.17
idna==2.8
jellyfish==0.5.6
psycopg2==2.7.6.1
psycopg2-binary==2.7.6.1
python-dateutil==2.7.5
python-http-client==3.1.0
pytz==2018.7
requests==2.21.0
sendgrid==5.6.0
six==1.12.0
soupsieve==1.7.2
urllib3==1.24.1
us==1.0.0
```
3. postgres
4. weatherbit subscription
5. sendgrid subscription



