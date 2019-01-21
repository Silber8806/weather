import os
import datetime
import pytz
import us # US state metadata
from datetime import datetime

from django.db import models
from django.db.utils import DatabaseError
from django.conf import settings

from .util import if_null

# means location was deleted from database
DEFAULT_LOCATION=999999


class BaseModel(models.Model):
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

class Location(models.Model):
	city = models.CharField(max_length=255, null=True, blank=False)
	state = models.CharField(max_length=255, null=True, blank=False)

	@property
	def city_state(self):
		city_state_lst = [if_null(val,'NULL') for val in [self.id, self.city,self.state]]
		location_id, city, state = city_state_lst
		location_ret = tuple([location_id, city + ',' + state])
		return tuple(location_ret)

	@property
	def timezone(self):
		if (self.state is not None):
			timezone = us.states.lookup(self.state).time_zones[0]
		else:
			timezone = None
		return timezone

	@property
	def now(self):
		if (self.state is not None):
			timezone = us.states.lookup(self.state).time_zones[0]
			tz = pytz.timezone(timezone)
			now_time = datetime.now(tz)
		else:
			# later on override this with Central or Pacific time.
			now_time = datetime.now()
		return now_time

	def __str__(self):
		return "{}".format(self.city_state)

class Customer(models.Model):
	email = models.EmailField(null=False,blank=False,unique=True)
	location = models.ForeignKey(Location, on_delete=models.SET_DEFAULT, default=DEFAULT_LOCATION)

	def __str__(self):
		return "{} : {}".format(self.email,self.location.city + ',' + self.location.state)

