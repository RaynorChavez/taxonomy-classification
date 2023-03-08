import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
Image.MAX_IMAGE_PIXELS = 10000000000


dataset_subset = "subset1k"

def resize_image(image_path, new_size):
    with Image.open(image_path) as image:
        image = image.resize(new_size)
        return image


def write_image(image, output_folder, filename, image_num):
    output_path = os.path.join(output_folder, filename)
    image.save(output_path)
    if image_num % 500 == 0:
        print(f"Processed {image_num} images...")

def process_images_in_folder(folder_path, output_folder, new_size):
    resize_pool = ThreadPoolExecutor()
    write_pool = ThreadPoolExecutor()
    futures = []

    for i, filename in enumerate(os.listdir(folder_path)):
        if not filename.endswith('.jpg'):
            continue
        image_path = os.path.join(folder_path, filename)
        future = resize_pool.submit(resize_image, image_path, new_size)
        futures.append((future, filename, i + 1))


    for future, filename, image_num in futures:
        resized_image = future.result()
        write_pool.submit(write_image, resized_image, output_folder, filename, image_num)

    resize_pool.shutdown()
    write_pool.shutdown()

if __name__ == '__main__':
    folder_path = f'./data/{dataset_subset}_taxo_data_images'
    output_folder = f'./data/taxo_data_images_{dataset_subset}_resized'
    new_size = (225, 225)
    os.makedirs(output_folder, exist_ok=True)
    process_images_in_folder(folder_path, output_folder, new_size)