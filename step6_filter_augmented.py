import ijson 
from pathlib import Path
import json
import time

dataset_subset = "subset1k"
split = "train"
Path(f'./data/{dataset_subset}_taxo_data_images/').mkdir(parents=True, exist_ok=True)

processed = 0
final_text_aug = f'./data/textaug_{dataset_subset}.json'

textaug_full = []
with open(final_text_aug) as f:
    t0 = time.time()
    for line in f:
        item = json.loads(line)

        # Get filename and check if image exists locally
        image_filename = item["filename"][17:]
        local_path = f"./data/{dataset_subset}_"+item["filename"][0:17]+image_filename
        
        if Path(local_path).is_file() and item["filename"][-4:] == ".jpg":
            textaug_full.append(item)
            #print(f"{image_filename}: exists")
        
        processed += 1
        if processed%1000 == 0:
            print("Processed: ", processed, "entries")

with open(f'./data/textaug_{split}_{dataset_subset}', 'w') as f:
    for item in textaug_full:
        f.write(json.dumps(item)+'\n')
