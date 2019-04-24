import os
import wget
import pandas as pd
import numpy as np
from PIL import Image
from tqdm import tqdm
from sklearn.model_selection import train_test_split

def create_ev_to_from_paths(data_frame):
	try:
		data_frame['ev_from_path'] = os.path.expanduser('~/Sync/projects/personal_projects/pokemon_evolution/data/')+data_frame['ev_from_num'].map(str)+'.jpg'
		data_frame['ev_to_path'] = os.path.expanduser('~/Sync/projects/personal_projects/pokemon_evolution/data/')+data_frame['ev_to_num'].map(str)+'.jpg'
		return data_frame
	except:
		raise

def check_image_is_available(data_frame):
	try:
		data_frame['ev_from_available']  = data_frame['ev_from_path'].map(os.path.isfile)
		data_frame['ev_to_available']    = data_frame['ev_to_path'].map(os.path.isfile)
		return data_frame
	except:
		raise

def download_image_from_url(url,dest_path):
	try:
		wget.download(url,dest_path)
	except:
		raise

def set_combined_data_path(train_val_test):
	try:
		if train_val_test == 'train':
			dest_folder = os.path.expanduser(
				'~/Sync/projects/personal_projects/pokemon_evolution/processed_data/train/')
		elif train_val_test == 'val':
			dest_folder = os.path.expanduser(
				'~/Sync/projects/personal_projects/pokemon_evolution/processed_data/val/')
		else:
			dest_folder = os.path.expanduser(
				'~/Sync/projects/personal_projects/pokemon_evolution/processed_data/test/')
		return dest_folder
	except:
		raise

def create_dest_combined_path(data_frame,train_val_test='train'):
	try:
		dest_folder = set_combined_data_path(train_val_test)
		data_frame['combined_img_dest_path'] = dest_folder+'from_'+data_frame[
		'ev_from_num'].map(str)+'_to_'+data_frame['ev_to_num'].map(str)+'.png'
		return data_frame
	except:
		raise

def load_and_resize_image(path_to_image):
	try:
		path = os.path.expanduser(path_to_image)
		img  = Image.open(path)
		img.thumbnail((128, 128), Image.ANTIALIAS)
		return img
	except:
		raise

def create_save_combined_images(data_frame_row):
	try:
		files  = [data_frame_row['ev_from_path'],data_frame_row['ev_to_path']]
		comb_images = Image.fromarray(
			np.hstack(
				[load_and_resize_image(each_image) for each_image in files]))
		comb_images.save(data_frame_row['combined_img_dest_path'])
	except:
		raise

def apply_create_save_combined_images_to_rows(data_frame):
	try:
		for each_row_idx,each_row in tqdm(data_frame.iterrows()):
			print('From {0},to {1}'.format(each_row['ev_from_name'],each_row['ev_to_name']))
			create_save_combined_images(each_row)
	except:
		raise

def main():
	try:
		to_from_data = pd.read_csv(
			os.path.expanduser(
				'~/Sync/projects/personal_projects/pokemon_evolution/pair_forms_sheet.csv'))
		to_from_paths = create_ev_to_from_paths(to_from_data)
		to_from_paths_available = check_image_is_available(to_from_paths)

		for each_row_idx, each_row in tqdm(to_from_paths_available.iterrows()):
			if not each_row['ev_from_available']:
				download_image_from_url(each_row['ev_from_url'],each_row['ev_from_path'])
			elif not each_row['ev_to_available']:
				download_image_from_url(each_row['ev_to_url'],each_row['ev_to_path'])

		#Create train/test/split assignments
		train_valtest_mask = np.random.rand(len(to_from_paths_available)) < 0.6
		train_data   = to_from_paths_available[train_valtest_mask]
		valtest_data = to_from_paths_available[~train_valtest_mask]
		val_test_mask  = np.random.rand(len(valtest_data)) < 0.5
		val_data     = valtest_data[val_test_mask]
		test_data    = valtest_data[~val_test_mask]

		train_data = create_dest_combined_path(train_data,train_val_test='train')
		val_data   = create_dest_combined_path(val_data,train_val_test='val')
		test_data  = create_dest_combined_path(test_data,train_val_test='test')

		apply_create_save_combined_images_to_rows(train_data)
		apply_create_save_combined_images_to_rows(val_data)
		apply_create_save_combined_images_to_rows(test_data)

	except:
		raise

if __name__ == '__main__':
	main()