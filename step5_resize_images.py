import os
from PIL import Image
from multiprocessing import Pool, cpu_count

dataset_subset = "subset1k"

def resize_image(image_path, new_size):
    with Image.open(image_path) as image:
        image = image.resize(new_size)
        return image

def write_image(args):
    image, output_folder, filename, image_num = args
    output_path = os.path.join(output_folder, filename)
    image.save(output_path)
    if image_num % 500 == 0:
        print(f"Processed {image_num} images...")

def process_images_in_folder(folder_path, output_folder, new_size):
    os.makedirs(output_folder, exist_ok=True)

    images = [(os.path.join(folder_path, filename), filename, i+1) for i, filename in enumerate(os.listdir(folder_path)) if filename.endswith('.jpg')]
    num_processes = min(len(images), cpu_count())

    with Pool(num_processes) as pool:
        resized_images = pool.starmap(resize_image, [(image_path, new_size) for image_path, _, _ in images])
        pool.map(write_image, [(resized_images[i], output_folder, filename, image_num) for i, (_, filename, image_num) in enumerate(images)])

if __name__ == '__main__':
    folder_path = f'./data/{dataset_subset}_taxo_data_images'
    output_folder = f'./data/taxo_data_images_resized'
    new_size = (225, 225)
    process_images_in_folder(folder_path, output_folder, new_size)
