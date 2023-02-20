# Recommend to run this if your system is windows
# This is because Windows filenaming conventions are more limited than linux
# 1. download dataset images
# 2. Run this to check for filename inconsistencies
# 3. This will download any images not consistent with Windows filenaming conventions
# The above are outdated. 

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

dataset_subset = "full"
Path(f'./data/logs/').mkdir(parents=True, exist_ok=True)
Path(f'./data/{dataset_subset}_taxo_data_images/').mkdir(parents=True, exist_ok=True)

processed = 0
per_image_cleaned = f'./data/{dataset_subset}_per_image_cleaned.json'
final_textaug_path = f'./data/{dataset_subset}_final_text_aug.json'
logs = f'./data/logs/{dataset_subset}_img_download_log.json'
with open(per_image_cleaned) as f:

    #Initialize JSON outputs
    log = open(logs, 'a')
    log.truncate(0)
    log.write("[")

    final_textaug = open(final_textaug_path, 'a')
    final_textaug.truncate(0)
    final_textaug.write("[")
    
    first_object = True  # flag to keep track of first object
    t0 = time.time()
    for item in ijson.items(f, "item"):
        processed += 1
        
        # Get filename and check if image exists locally
        image_filename = item["filename"][17:]
        local_path = f"./data/{dataset_subset}_"+item["filename"][0:17]+image_filename
        
        if Path(local_path).is_file():
            log_entry = {
                "id": processed,
                "status": "exists_locally",
                "file": image_filename,
            }
            final_textaug.write(json.dumps(item))
            log.write(json.dumps(log_entry))
            print(f"{image_filename}: exists")
            continue

        # Construct image url
        md5 = hashlib.md5(image_filename.encode('utf-8')).hexdigest()
        a = md5[0]
        b = md5[1]
        url = f"https://upload.wikimedia.org/wikipedia/commons/{a}/{a}{b}/{image_filename}"
        headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}

        # Request the image from the url
        img_data = requests.get(url, headers=headers)
        
        if img_data.ok:
            if not first_object:
                # add a comma before each object after the first one
                final_textaug.write(",")
                log.write(",")
            else:
                first_object = False  # set flag to False after writing the first object
            
            # Validate if filename is suitable
            try:
                validate_filename(image_filename, platform="Windows")
            except ValidationError as e:
                print("{}\n".format(e), file=sys.stderr)
                print("{} -> {}".format(image_filename, sanitize_filename(image_filename)))
                image_filename = sanitize_filename(image_filename)
                local_path = f"./data/{dataset_subset}_"+item["filename"][0:17]+image_filename

            # Write the image to file
            with open(local_path, 'wb') as handle:
                for block in img_data.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

            # Write final augmented JSON database
            final_textaug_entry = item
            final_textaug_entry["filename"] = final_textaug_entry["filename"][0:17]+image_filename
            final_textaug.write(json.dumps(final_textaug_entry))

            # Log entry
            log_entry = {
                "id": processed,
                "status": "Success",
                "file": image_filename,
                "source": url
            }
            log.write(json.dumps(log_entry))
            
        else:
            log_entry = {
                "id": processed,
                "status": "Error",
                "file": image_filename,
                "source": url
            }
            if not first_object:
                # add a comma before each object after the first one
                log.write(",")
            else:
                first_object = False  # set flag to False after writing the first object
            
            # Log entry
            log.write(json.dumps(log_entry))
            print(f'Image Couldn\'t be retrieved\n\t{image_filename}\n\t{url}')

        # Progress Indicator
        if processed%20 == 0:
            print(f"Downloaded {processed} images. Start time: {t0} Time now: {time.time()}")

    # Close JSON outputs
    final_textaug.write("]")
    final_textaug.close
    log.write("]")
    log.close
