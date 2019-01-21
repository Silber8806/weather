import os
import smtplib
import requests

def normalize_email(email):
	""" normalize email to lowercase username + domain unrestricted"""
	username, domain = email.split('@')
	email = username.lower() + "@" + domain
	return email

def if_null(value,default=''):
	if (value is None):
		return default 
	else:
		return value