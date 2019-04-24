import os
import numpy as np
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def get_list_of_names_from_child(child):
	try:
		child_names   = child.find_all("a",{"class":"ent-name"})
		output_list_of_names = []
		for each_child in child_names:
			output_list_of_names.append(each_child.text)
		return output_list_of_names
	except:
		raise

def get_list_of_numbers_from_child(child):
	try:
		child_numbers = child.find_all("small") 
		output_list_of_numbers = []
		for each_child in child_numbers:
			if "#" in each_child.text:
				output_list_of_numbers.append(each_child.text[1:])
		return output_list_of_numbers
	except:
		raise

def get_list_of_urls_from_child(child):
	try:
		child_urls    = child.find_all("span",{"class":"img-fixed img-sprite"})
		output_list_of_urls = []
		for each_url in child_urls:
			output_list_of_urls.append(each_url['data-src'])
		return output_list_of_urls
	except:
		raise

def generate_list_element_pairs(child_properties):
	try:
		output_list_pair_list = []
		for first,second in zip(child_properties,child_properties[1:]):
			output_list_pair_list.append(tuple((first,second)))
		return output_list_pair_list
	except:
		raise

def create_names_numbers_urls_from_child(child):
	try:
		names   = get_list_of_names_from_child(child)
		numbers = get_list_of_numbers_from_child(child)
		urls    = get_list_of_urls_from_child(child)
		return names,numbers,urls
	except:
		raise

def create_pair_forms_dataframe(names,numbers,urls):
	try:
		ev_name_pairs = pd.DataFrame(generate_list_element_pairs(names))
		ev_num_pairs  = pd.DataFrame(generate_list_element_pairs(numbers))
		ev_url_pairs  = pd.DataFrame(generate_list_element_pairs(urls))
		pair_forms_dataframe = pd.concat([ev_name_pairs,ev_num_pairs,ev_url_pairs],ignore_index=True,axis=1)
		return pair_forms_dataframe
	except:
		raise

def create_pokemon_info_dataframes(child):
	try:
		names,numbers,urls  = create_names_numbers_urls_from_child(child)
		list_form_dataframe = pd.DataFrame({'name':names,'number':numbers,'img_url':urls})
		pair_form_dataframe = create_pair_forms_dataframe(names,numbers,urls)
		return list_form_dataframe, pair_form_dataframe
	except:
		raise

def create_download_destination_paths(num):
	try:
		output_url = os.path.expanduser('~/Sync/projects/personal_projects/pokemon_evolution/downloaded_data/'+num+'.png')
		return output_url
	except:
		raise

def main():
	try:
		site_to_scrape = 'https://pokemondb.net/evolution'
		page = requests.get(site_to_scrape)
		soup = BeautifulSoup(page.content, 'html.parser')
		result = soup.find_all("div", {"class":"infocard-list-evo"})
		pair_forms_output_list = []
		for res in result:
			list_form_dataframe, pair_form_dataframe = create_pokemon_info_dataframes(res)
			pair_forms_output_list.append(pair_form_dataframe)
		pair_forms_output = pd.concat(pair_forms_output_list)
		pair_forms_output.columns = ['ev_from_name', 'ev_to_name', 'ev_from_num','ev_to_num','ev_from_url','ev_to_url']
		pair_forms_output.to_csv('~/Sync/projects/personal_projects/pokemon_evolution/pair_forms_sheet.csv',index=False)
	except:
		raise

if __name__ == '__main__':
	main()