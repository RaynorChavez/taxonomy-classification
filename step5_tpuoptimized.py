import os
import tensorflow as tf

# Set the path to the directory containing the images
dataset_subset = "full"
image_dir = f'gs://taxo-class-dataset/{dataset_subset}_taxo_data_images'

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
files = tf.io.gfile.glob(os.path.join(image_dir, '*.jpg')) + tf.io.gfile.glob(os.path.join(image_dir, '*.jpeg')) + tf.io.gfile.glob(os.path.join(image_dir, '*.png')) + tf.io.gfile.glob(os.path.join(image_dir, '*.JPG'))+ tf.io.gfile.glob(os.path.join(image_dir, '*.PNG'))

# Set the path to the directory to save the resized images
save_dir = f'gs://taxo-class-dataset/taxo_data_images_{dataset_subset}_resized_tpu'

# Check if save_dir exists, create it if it doesn't
if not tf.io.gfile.exists(save_dir):
    tf.io.gfile.makedirs(save_dir)

# Create a dataset from the list of image files
dataset = tf.data.Dataset.from_tensor_slices(files)

# Shard the dataset across all available TPU cores
strategy = tf.distribute.TPUStrategy()

# Define the preprocessing function to use in the map operation
@tf.function
def preprocess(file_path):
    img = preprocess_image(file_path)
    img_name = tf.strings.split(tf.strings.split(file_path, '/')[-1], '.')[0] + '.jpg'
    img_path = os.path.join(save_dir, img_name)

    # If the resized image already exists, skip this file
    if tf.io.gfile.exists(img_path):
        print(f"Resized {file_path} already exists in {save_dir}")
        return file_path

    img = tf.image.encode_jpeg(tf.cast(img * 255.0, tf.uint8))
    tf.io.gfile.GFile(img_path, 'w').write(img.numpy())

    # Print progress update every 500 images
    if int(file_path.split('/')[-1].split('.')[0]) % 500 == 0:
        print(f"Processed {file_path.split('/')[-1]}")

    return file_path

# Apply the preprocessing function to the dataset
dataset = dataset.map(preprocess, num_parallel_calls=tf.data.experimental.AUTOTUNE)

# Print the number of images processed
num_images = tf.data.experimental.cardinality(dataset).numpy()
print(f"Processed {num_images} images")
