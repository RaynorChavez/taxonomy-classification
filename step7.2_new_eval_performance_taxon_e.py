#!/usr/bin/env python
import argparse
import jax
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from PIL import Image
from transformers import CLIPProcessor, FlaxCLIPModel


DATA_DIR = "data/"
# IMAGES_DIR = os.path.join(DATA_DIR, "RSICD_images")
IMAGES_DIR = os.path.join(DATA_DIR)

BASELINE_MODEL = "openai/clip-vit-base-patch32"
MODEL_DIR = "/home/shared/models/clip-rsicd"
K_VALUES = [1, 3, 5, 10]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_dir",
                        help="Path of model to evaluate, set to 'baseline' for baseline. Intermediate \
                        results will be written out to nbs/results/${model_name}")
    args = parser.parse_args()
    return args


def predict_one_image(image_file, model, processor, class_names, k):
    eval_image = Image.fromarray(plt.imread(os.path.join(IMAGES_DIR, image_file)))
    eval_sentences = ["This is an example of species {:s}".format(ct) for ct in class_names]
    inputs = processor(text=eval_sentences,
                       images=eval_image,
                       return_tensors="jax",
                       padding=True)
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = jax.nn.softmax(logits_per_image, axis=-1)
    probs_np = np.asarray(probs)[0]
    probs_npi = np.argsort(-probs_np)
    predictions = [(class_names[i], probs_np[i]) for i in probs_npi[0:k]]
    return predictions


def get_model_basename(model_dir):
    if model_dir == "basename":
        return "basename"
    else:
        # return model_dir.split("/")[-1]
        return model_dir.replace(MODEL_DIR + "/", "").replace("/", "-")



print("Starting evaluation...")

args = parse_arguments()

print("Loading checkpoint {:s}...".format(args.model_dir))
if args.model_dir == "baseline":
    model = FlaxCLIPModel.from_pretrained(BASELINE_MODEL)
    processor = CLIPProcessor.from_pretrained(BASELINE_MODEL)
else:
    # TODO: unfix later
    model = FlaxCLIPModel.from_pretrained(args.model_dir)
    # from flax.jax_utils import unreplicate
    # model.params = unreplicate(model.params)
    processor = CLIPProcessor.from_pretrained(BASELINE_MODEL)

print("Retrieving evaluation images...", end="")
eval_images = []
df = pd.read_csv("data/final_test_set_with_taxon_tree.csv", encoding='utf-8')
df = df.dropna(subset=['taxon_e'])
eval_images = df['image_link'].map(lambda x: "new_test_images_5k/" + x.split('/')[-1]).tolist()

print("{:d} images found".format(len(eval_images)))

print("Retrieving class names...", end="")
class_names = df['taxon_e'].unique().tolist()
print("{:d} classes found".format(len(class_names)))

labels = df['taxon_e'].tolist()


print("Generating predictions...")
fres = open(os.path.join(
    "data", "results", get_model_basename(args.model_dir) + "_taxon_e_new_test_preds.tsv"), "w")
num_predicted = 0
for eval_image, label in zip(eval_images, labels):
    if num_predicted % 10 == 0:
        print("{:d} images evaluated".format(num_predicted))        
    if not os.path.exists("data/" + eval_image):
        continue
    preds = predict_one_image(
        eval_image, model, processor, class_names, max(K_VALUES))
    fres.write("{:s}\t{:s}\t{:s}\n".format(
        eval_image, label, 
        "\t".join(["{:s}\t{:.5f}".format(c, p) for c, p in preds])))
    num_predicted += 1
    # if num_predicted > 10:
    #     break

print("{:d} images evaluated, COMPLETE".format(num_predicted))
fres.close()


print("Computing final scores...")
num_examples = 0
correct_k = [0] * len(K_VALUES)
model_basename = get_model_basename(args.model_dir)
fres = open(os.path.join("data", "results", model_basename + "_taxon_e_new_test_preds.tsv"), "r")
for line in fres:
    cols = line.strip().split('\t')
    label = cols[1]
    preds = []
    for i in range(2, 22, 2):
        preds.append(cols[i])
    for kid, k in enumerate(K_VALUES):
        preds_k = set(preds[0:k])
        if label in preds_k:
            correct_k[kid] += 1
    num_examples += 1

fres.close()
scores_k = [ck / num_examples for ck in correct_k]
print("\t".join(["score@{:d}".format(k) for k in K_VALUES]))
print("\t".join(["{:.3f}".format(s) for s in scores_k]))
fscores = open(os.path.join("data", "results", model_basename + "_taxon_e_new_test_score.tsv"), "w")
fscores.write("{:s}\t{:s}\n".format(
    model_basename, 
    "\t".join(["{:.3f}".format(s) for s in scores_k])))
fscores.close()
