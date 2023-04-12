
import ijson 
import requests
import shutil
from pathlib import Path
import hashlib
import json
import time
import sys
from pathvalidate import ValidationError, validate_filename
from pathvalidate import sanitize_filename
import os

dataset_subset = "full"
Path(f'./data/logs/').mkdir(parents=True, exist_ok=True)
Path(f'./data/{dataset_subset}_taxo_data_images/').mkdir(parents=True, exist_ok=True)

processed = 0
kyle_aug = f'./data/full_captions_taxons_dataset.json'
textaug_train_full = f'./data/textaug_train_{dataset_subset}.json'
textaug_train_full_capaug_path = f'./data/textaug_train_{dataset_subset}_capaug.json'

filenames_in_kyle = set()
filenames_in_textaug = set()
textaug_train_full_capaug = []
with open(kyle_aug) as f:
    
    #t0 = time.time()
    for item in ijson.items(f, "item"):
        #processed += 1
        
        # Get filename and check if it also exists in the textaug_train_full.json file
        image_filename = item["filename"]
        filenames_in_kyle.add(image_filename)
    print("Done with kyle_aug")

#open textaug_train_full.json and take all filenames into a list
with open(textaug_train_full) as f:
    t0 = time.time()
    for line in f:
        item = json.loads(line)
        image_filename = item["filename"][17:]
        #print(image_filename)
        filenames_in_textaug.add(image_filename)
    print("Done with textaug_train_full.json")


#now take take all the filenames in filenames_in_kyle and check if they are in filenames_in_textaug
#if they are not, add them to a list
filenames_not_in_textaug = filenames_in_kyle - filenames_in_textaug

print("Done with filenames_not_in_textaug")

#now open kyle_aug again and output in textaug_train_full_capaug only if the item filename is not in filenames_not_in_textaug 
with open(kyle_aug) as f:
    t0 = time.time()
    
    for item in ijson.items(f, "item"):
        processed += 1

        image_filename = item["filename"]
        #print(image_filename)
        if image_filename not in filenames_not_in_textaug:
            #print("found: ", image_filename)
            item["filename"] = "taxo_data_images/"+item["filename"]
            item["captions"] = item["new_captions"]
            item.pop("new_captions", None)
            textaug_train_full_capaug.append(item)

        if processed < 2:
            print(str(json.dumps(item, indent=4, sort_keys=True)))
        if processed%500 == 0:
            print("Processed: ", processed, "entries")

with open(textaug_train_full_capaug_path, 'w') as outfile:
    for entry in textaug_train_full_capaug:
        json.dump(entry, outfile)
        outfile.write('\n')

print("Done with outputting to textaug_train_full_capaug.json")
