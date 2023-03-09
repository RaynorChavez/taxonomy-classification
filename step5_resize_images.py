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
dataset_subset = "subset1k"
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

# Create a dataset from the list of file paths
dataset = tf.data.Dataset.from_tensor_slices(files)

# Use multiple threads to preprocess the images in parallel
dataset = dataset.map(preprocess_image, num_parallel_calls=tf.data.experimental.AUTOTUNE)

# Set the path to the directory to save the resized images
save_dir = f'./data/taxo_data_images_{dataset_subset}_resized'

# Save the resized images
for i, img in enumerate(dataset):
    file_path = files[i]
    img_name = os.path.splitext(os.path.basename(file_path))[0] + '.jpg'
    img_path = os.path.join(save_dir, img_name)
    img = tf.image.encode_jpeg(tf.cast(img * 255.0, tf.uint8))
    tf.io.write_file(img_path, img)

    print(f"Resized {file_path} to {img_size} and saved to {img_path}")
