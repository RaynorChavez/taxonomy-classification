from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os

# Define the path to the folder of images
dataset_path = "./data/subset1k_taxo_data_images/"

# Define the target image size
target_size = 256

# Define the transformation pipeline
transform = transforms.Compose([
    transforms.Resize(target_size),
    transforms.ToTensor(),
])

# Define a custom dataset that ignores class labels
class NoClassImageDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.imgs = sorted(os.listdir(root_dir))
        
    def __getitem__(self, idx):
        img_path = os.path.join(self.root_dir, self.imgs[idx])
        img = Image.open(img_path).convert('RGB')
        
        if self.transform:
            img = self.transform(img)
        
        return img, 0
    
    def __len__(self):
        return len(self.imgs)

# Create a custom dataset and apply the transformation pipeline to it
dataset = NoClassImageDataset(dataset_path, transform=transform)

# Create a dataloader to load the transformed images in batches
batch_size = 32
num_workers = 4  # Set this to the number of CPU cores you want to use for loading and transforming the data
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

# Loop through the dataloader and save the transformed images to disk
for i, (images, labels) in enumerate(dataloader):
    for j in range(images.size(0)):
        original_filename = dataset.imgs[i * batch_size + j]
        image = transforms.ToPILImage()(images[j])
        filename = os.path.basename(original_filename)
        save_path = f'./data/subset1k_taxo_data_images_resized/{filename}'
        image.save(save_path)

