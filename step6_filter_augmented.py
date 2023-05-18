import ijson 
import json
import os
import time
from PIL import Image

dataset_subset = "full"
split = "train"
resized_folder = f'./data/taxo_data_images_{dataset_subset}_resized/'
#Path(resized_folder).mkdir(parents=True, exist_ok=True)

processed = 0
final_text_aug = f'./data/full_captions_taxons_dataset.json'

textaug_full = []
with open(final_text_aug) as f:
    t0 = time.time()
    for line in f:
        item = json.loads(line)
        if processed == 0:
            print(item)
        # print("Item: ", processed, item["filename"][17:])

        # Get filename and check if image exists locally
        image_filename = item["filename"][17:]
        #print(item)
        local_path = os.path.join(resized_folder, image_filename)
        
        # Check if the image file exists, is non-empty and not corrupted
        if os.path.isfile(local_path):
            try:
                with Image.open(local_path) as img:
                    img.verify()
                    textaug_full.append(item)
            except Exception as e:
                print(f"Error processing {local_path}: {e}")
        
        processed += 1
        if processed%100 == 0:
            print("Processed: ", processed, "entries")

with open(f'./data/textaug_{split}_{dataset_subset}_capaug.json', 'w') as f:
    for item in textaug_full:
        f.write(json.dumps(item)+'\n')
