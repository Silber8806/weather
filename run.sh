#!/bin/sh

function usage 
{
	echo "### source run.sh <python environment> <re-load development data>"
	echo "quickly source environment..."
}

function main 
{
	if [[ -f "${envr_activate}" ]]
	then 
		echo "starting ${envr}"
		source "${envr_activate}"
	else 
		echo "no environment: ${envr} found..."
	fi

	if [[ "${envr}" == "dev" ]]
	then 
		set_up_dev_envir
	else 
		set_up_prod_envir
	fi
	return 0
}

function set_up_dev_envir
{
	export DJANGO_SETTINGS_MODULE=weather.settings.local

	echo "starting postgres server"
	pg_server_binary=/usr/local/var/postgres

	pg_err=0
	pg_ctl -D "${pg_server_binary}" start || pg_err=1

	if [[ "${pg_err}" -ne "0" ]]
	then 
		# normally i'd exit out of this, but I haven't written that part yet..
		echo "error starting postgres..."
	fi

	if [[ "${load_data}" -eq "1" ]]
	then 
		echo "reload data..."
		start_script=./apps/webapps/weather/scripts/load_data.sh
		bash "${start_script}"
	fi

	echo "environmnet started..."
	return 0
}

function set_up_prod_envir
{
	# this is not implemented yet...
	echo "production has not been implemented yet..."
	export DJANGO_SETTINGS_MODULE=weather.settings.production
	return 0
}

if [[ "$#" -lt "1" ]]
then 
	usage
fi 

# environment to load... options [dev and prod]
envr="$1"

# load data for dev [0,1]
load_data="$2"

# virtualenv activation
envr_activate="./env/${envr}/bin/activate"

main
