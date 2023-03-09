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
import os

dataset_subset = "subset1k"
Path(f'./data/logs/').mkdir(parents=True, exist_ok=True)
Path(f'./data/{dataset_subset}_taxo_data_images/').mkdir(parents=True, exist_ok=True)

processed = 0
per_image_cleaned = f'./data/{dataset_subset}_per_image_cleaned.json'

final_textaug = []
log = []
with open(per_image_cleaned) as f:
    
    t0 = time.time()
    for item in ijson.items(f, "item"):
        processed += 1
        
        # Get filename and check if image exists locally
        image_filename = item["filename"][17:]
        # Validate if filename is suitable
        try:
            validate_filename(image_filename, platform="Windows")
        except ValidationError as e:
            print("{}\n".format(e), file=sys.stderr)
            print("{} -> {}".format(image_filename, sanitize_filename(image_filename)))
            image_filename = sanitize_filename(image_filename)
        local_path = f"./data/{dataset_subset}_"+item["filename"][0:17]+image_filename
        
        if Path(local_path).is_file():
            log_entry = {
                "id": processed,
                "status": "exists_locally",
                "file": image_filename,
            }
            final_textaug.append(item)
            log.append(log_entry)

            #print(f"{image_filename}: exists")
            if processed%1000 == 0:
                print("Processed: ", processed, "entries")

            continue

        # Construct image url
        image_filename = item["filename"][17:]
        md5 = hashlib.md5(image_filename.encode('utf-8')).hexdigest()
        a = md5[0]
        b = md5[1]
        url = f"https://upload.wikimedia.org/wikipedia/commons/{a}/{a}{b}/{image_filename}"
        headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}

        # Request the image from the url
        img_data = requests.get(url, headers=headers)

        if img_data.ok:
            
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
            final_textaug.append(final_textaug_entry)

            # Log entry
            log_entry = {
                "id": processed,
                "status": "Success",
                "file": image_filename,
                "source": url
            }
            log.append(log_entry)
            
        else:
            log_entry = {
                "id": processed,
                "status": "Error",
                "file": image_filename,
                "source": url
            }

            # Log entry
            log.append(log_entry)
            print(f'Image Couldn\'t be retrieved\n\t{image_filename}\n\t{url}')
        
        # Progress Indicator
        if processed%20 == 0:
            print(f"Downloaded {processed} images. Start time: {t0} Elapsed: {time.time() - t0}")
        if processed%1000 == 0:
            print("Processed: ", processed, "entries")

    # Close JSON outputs
    # remove the last character of the file final_textaug
 
    with open(f'./data/textaug_{dataset_subset}.json', 'w') as f:
        for entry in final_textaug:
            json.dump(entry, f)
            f.write('\n')

    with open(f'./data/logs/{dataset_subset}_img_download_log.json', 'w') as f:
        for entry in log:
            json.dump(entry, f)
            f.write('\n')

