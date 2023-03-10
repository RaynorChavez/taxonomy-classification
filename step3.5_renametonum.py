import os
import json

dataset_subset = "subset1k"

# Specify the path to the folder containing the images
folder_path = f'./data/{dataset_subset}_taxo_data_images'

# Specify the path to the JSON file containing the image data
json_path = f'./data/textaug_{dataset_subset}.json'

# Load the JSON data
with open(json_path) as f:
    json_data = f.readlines()

# Create a new list to store the modified JSON objects
new_json_data = []
counter = 0
# Iterate over each image file in the folder
for i, filename in enumerate(os.listdir(folder_path)):
    # Check if the file is an image
    if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg") or filename.endswith(".JPG"):
        # Get the corresponding JSON object
        for j in range(len(json_data)):
            image_data = json.loads(json_data[j])
            if image_data["filename"] == f"taxo_data_images/{filename}":
                # Rename the image file
                os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, f"{i}.jpg"))
                # Modify the JSON object to reflect the new filename
                image_data["filename"] = f"{image_data['filename'][0:17]}{i}.jpg"
                # Append the modified JSON object to the new list
                new_json_data.append(image_data)
                break
        counter +=1
        if counter%300 == 0:
            print("Processed: ", counter, "entries")

# Write the updated JSON objects back to the file
with open(json_path, "w") as f:
    for line in new_json_data:
        f.write(json.dumps(line) + "\n")
