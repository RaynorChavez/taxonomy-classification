"""
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

"""

import os
import tensorflow as tf

# Set the path to the directory containing the images
dataset_subset = "full"
image_dir = f'./data/{dataset_subset}_taxo_data_images'

# Set the desired image size
img_size = (224, 224)

# Define a function to preprocess each image
def preprocess_image(file_path):
    # Load the image file
    img = tf.io.read_file(file_path)
    img = tf.image.decode_jpeg(img, channels=3)

    # Resize the image
    img = tf.image.resize(img, img_size)

    # Normalize the pixel values
    img = tf.cast(img, tf.float32) / 255.0

    return img

# Get a list of all image files in the directory
files = [os.path.join(image_dir, f) for f in os.listdir(image_dir)
         if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]

# Set the path to the directory to save the resized images
save_dir = f'./data/taxo_data_images_{dataset_subset}_resized'

# Check if save_dir exists, create it if it doesn't
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Loop through the list of image files
for i, file_path in enumerate(files):
    # Get the image name and path for the resized image
    img_name = os.path.splitext(os.path.basename(file_path))[0] + '.jpg'
    img_path = os.path.join(save_dir, img_name)

    # If the resized image already exists, skip this file
    if os.path.exists(img_path):
        print(f"Resized {file_path} already exists in {save_dir}")
        continue

    # Load and preprocess the image
    try:
        img = preprocess_image(file_path)
    except Exception as e:
        print(f"Error while processing {file_path}: {str(e)}")
        continue

    # Save the resized image
    try:
        img = tf.image.encode_jpeg(tf.cast(img * 255.0, tf.uint8))
        tf.io.write_file(img_path, img)
        print(f"Resized {file_path} to {img_size} and saved to {img_path}")
    except Exception as e:
        print(f"Error while saving {img_path}: {str(e)}")
        continue
