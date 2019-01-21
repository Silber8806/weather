#!/bin/bash

database=weather
user=postgres 
prev_wd=$(pwd)
start_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
file_to_upload="${start_dir}/top100.txt"

echo "setting up developer environment..."

echo "going to ${start_dir}"
cd "${start_dir}"

echo "getting top 100 cities from table..."
python ./top100.py

err=0
echo "truncating tables: customer and location..."
psql -d "${database}" -U "${user}" -c "truncate table signup_location CASCADE" || err=1
psql -d "${database}" -U "${user}" -c "truncate table signup_customer" || err=1

echo "reseting sequences..."
reset_sequences=$(python ../manage.py sqlsequencereset signup)
echo "${reset_sequences}"
echo "${reset_sequences}" | python ../manage.py dbshell || err=1
psql -d "${database}" -U "${user}" -c "copy signup_location(city,state) from '${file_to_upload}' DELIMITER ','"  || err=1
psql -d "${database}" -U "${user}" -c "insert into signup_location(id, city, state) values (999999,null,null)"

if [[ "${err}" -ne "0" ]]
then 
	echo "database failed..."
else 
	echo "upload succeeded..."
fi

cd "${prev_wd}"
