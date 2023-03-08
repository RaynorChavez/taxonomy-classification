import ijson
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

import string
import re
import json
import os
import sys
import time
nltk.download('punkt')

dataset_subset = "subset1k"
final_text_aug = f'./data/{dataset_subset}_final_text_aug.json'
tokenized_path = f'./data/{dataset_subset}_tokenized.json'

tokenized = {"images": []}
with open(final_text_aug) as f:
    
    t0 = time.time()
    processed = 0
    sentid = 0
    for line in f:
        item = json.loads(line)
        tokenized["images"].append(
            {
                "filename": item["filename"][17:],
                "imgid": processed,
                "sentences": [{
                        "tokens": word_tokenize(caption), 
                        "raw":caption,
                        "imgid": processed,
                        "sentid": sentid + i} 
                        for i,caption in enumerate(item["captions"])],
                "split": "train", # note that you might have to implement train-test split later
                "sentids": [sentid + i for i in range(len(item["captions"]))],
            }
        )
        sentid += len(item["captions"])
        processed += 1
        if processed%1000 == 0:
            print("Processed: ", processed, "entries")

with open(tokenized_path, 'w') as f:
    json.dump(tokenized, f)

'''
{
    "images": [
        {
            "filename": "airport_1.jpg",
            "imgid": 0,
            "sentences": [
                {
                    "tokens": [
                        "many",
                        "planes",
                        "are",
                        "parked",
                        "next",
                        "to",
                        "a",
                        "long",
                        "building",
                        "in",
                        "an",
                        "airport"
                    ],
                    "raw": "Many aircraft are parked next to a long building in an airport.",
                    "imgid": 0,
                    "sentid": 0
                },
                {
                    "tokens": [
                        "many",
                        "planes",
                        "are",
                        "parked",
                        "next",
                        "to",
                        "a",
                        "long",
                        "building",
                        "in",
                        "an",
                        "airport"
                    ],
                    "raw": "Many planes are parked next to a long building at an airport.",
                    "imgid": 0,
                    "sentid": 1
                }
            ],
            "split": "train",
            "sentids": [
                0,
                1,
                2,
                3,
                4
            ]
        },
'''