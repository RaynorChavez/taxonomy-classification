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
