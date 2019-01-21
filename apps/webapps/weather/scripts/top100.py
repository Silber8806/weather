import csv

def write_top_100_file():
	""" quick script for populating top 100 cities """
	print("reading pop file...")
	population = [city_state[1:3] for city_state in csv.reader(open('population.txt','r'))]
	print("reading abbreviatio nfile...")
	abbreviations = {abbre[0]:abbre[1] for abbre in csv.reader(open('abbreviations.txt','r'))}
	print("combining files...")
	convert_to_abbre = [[city_state[0],abbreviations[city_state[1]]] for city_state in population]
	convert_to_abbre = [ ','.join([city, state]) for city,state in convert_to_abbre ]
	convert_to_abbre = '\n'.join(convert_to_abbre)
	print('write file as top100.txt')
	outfile = open('top100.txt','w').write(convert_to_abbre)
	return 0

write_top_100_file()