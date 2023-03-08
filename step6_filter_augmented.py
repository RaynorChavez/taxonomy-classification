import ijson 
from pathlib import Path
import json
import time

dataset_subset = "subset1k"
split = "train"
Path(f'./data/taxo_data_images_{dataset_subset}_resized/').mkdir(parents=True, exist_ok=True)

processed = 0
final_text_aug = f'./data/textaug_{dataset_subset}.json'

textaug_full = []
with open(final_text_aug) as f:
    t0 = time.time()
    for line in f:
        item = json.loads(line)

        # Get filename and check if image exists locally
        image_filename = item["filename"][17:]
        local_path = f"./data/taxo_data_images_{dataset_subset}_resized/"+image_filename
        print(local_path)
        if Path(local_path).is_file():
            textaug_full.append(item)
            #print(f"{image_filename}: exists")
        
        processed += 1
        if processed%1000 == 0:
            print("Processed: ", processed, "entries")

with open(f'./data/textaug_{split}_{dataset_subset}.json', 'w') as f:
    for item in textaug_full:
        f.write(json.dumps(item)+'\n')
