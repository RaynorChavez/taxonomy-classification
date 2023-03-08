from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from PIL import Image
import os

# Define the path to the folder of images
dataset_subset = "subset1k"
data_path = f'./data/{dataset_subset}_taxo_data_images/'

# Define the target image size
target_size = 256

# Define the transformation pipeline
transform = transforms.Compose([
    transforms.Resize(target_size),
    transforms.ToTensor(),
])

# Create an ImageFolder dataset and apply the transformation pipeline to it
dataset = ImageFolder(data_path, transform=transform)

# Create a dataloader to load the transformed images in batches
batch_size = 32
num_workers = 4  # Set this to the number of CPU cores you want to use for loading and transforming the data
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

# Loop through the dataloader and save the transformed images to disk
for i, (images, labels) in enumerate(dataloader):
    for j in range(images.size(0)):
        original_filename = dataset.imgs[i*batch_size+j][0]
        image = transforms.ToPILImage()(images[j])
        label = labels[j]
        filename = os.path.basename(original_filename)
        save_path = f'./data/{dataset_subset}_taxo_data_images_resized/{filename}'
        image.save(save_path)
