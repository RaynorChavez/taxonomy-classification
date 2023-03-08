import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

dataset_subset = "subset1k"

def resize_image(image_path, new_size, output_folder):
    with Image.open(image_path) as image:
        image = image.resize(new_size)
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        image.save(output_path)


def process_images_in_folder(folder_path, output_folder, new_size):
    with ThreadPoolExecutor() as executor:
        for filename in os.listdir(folder_path):
            image_path = os.path.join(folder_path, filename)
            executor.submit(resize_image, image_path, new_size, output_folder)


if __name__ == '__main__':
    folder_path = f'./data/{dataset_subset}_taxo_data_images'
    output_folder = f'./data/{dataset_subset}_taxo_data_images_resized'
    new_size = (225, 225)
    os.makedirs(output_folder, exist_ok=True)
    process_images_in_folder(folder_path, output_folder, new_size)
