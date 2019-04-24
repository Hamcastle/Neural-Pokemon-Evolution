import os
from PIL import Image
from tqdm import tqdm

def load_and_resize_image(path_to_image):
	try:
		path = os.path.expanduser(path_to_image)
		img  = Image.open(path)
		img.thumbnail((128, 128), Image.ANTIALIAS)
		return img
	except:
		raise

def main():
	try:
		image_paths = ['~/Sync/projects/personal_projects/pokemon_evolution/sword_shield/raw/grookey_raw.png','~/Sync/projects/personal_projects/pokemon_evolution/sword_shield/raw/scorbunny_raw.png','~/Sync/projects/personal_projects/pokemon_evolution/sword_shield/raw/sobble_raw.png']
		names = ['grookey','scorbunny','sobble']
		output_path = os.path.expanduser('~/Sync/projects/personal_projects/pokemon_evolution/sword_shield/preprocessed_with_blank/')
		for each_image_idx, each_image in tqdm(enumerate(image_paths)):
			blank_image  = Image.new('RGBA',(128,128))
			actual_image = load_and_resize_image(each_image)
			combined_image = Image.fromarray(np.hstack((actual_image,blank_image)))
			combined_image.save(output_path+names[each_image_idx]+'.png')
	except:
		raise

if __name__ == '__main__':
	main()