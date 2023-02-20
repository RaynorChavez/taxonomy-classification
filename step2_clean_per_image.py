import ijson
import json

processed = 0
per_image_cleaned = []

# Separate the species name from the description
# Add an entry for animal type, place in taxonomy. Further perusal of wikidata shows that their information is inaccurat
#   - will forego this step for now. Might augment data from other sources in the future.

dataset_subset = "subset1k"

filename = f'./data/{dataset_subset}_filtered_taxons.json'
with open(filename) as f:
    for item in ijson.items(f, "item"):
        
        images = []
        for image in item["claims"]["P18"]:
            try:
                img_filename = image["mainsnak"]["datavalue"]["value"]
                img_type = image["mainsnak"]["datatype"]
            except:
                print("Error saving: image")
                continue
            if img_type == "commonsMedia":
                img_filename = "_".join(img_filename.split(" "))
                images.append(img_filename)

        id = item["id"]
        if 'datavalue' not in item["claims"]["P225"][0]["mainsnak"].keys():
            print("id: ", id, "\n", item["claims"]["P225"][0]["mainsnak"].keys())
            continue
        taxon =  item["claims"]["P225"][0]["mainsnak"]["datavalue"]["value"]
        if 'en' not in item["descriptions"].keys():
            print("id: ", id, "\n", item["descriptions"].keys(), type(list(item["descriptions"].keys())))
            try:
                caption = item["descriptions"][list(item["descriptions"].keys())[0]]["value"]
            except:
                print("Error saving: ", taxon)
                continue
        else:
            caption = item["descriptions"]["en"]["value"]
    

        for image in images:
            per_image_cleaned.append({
                "filename": "taxo_data_images/"+image,
                "species": taxon,
                "captions": [f"This is an example of species {taxon}.",
                        f"Image of an animal with taxon name: {taxon}.",
                        f"Species: {taxon}. {caption}",
                        f"{caption}",
                        f"{caption}. Taxon Name: {taxon}"
                        f"{caption}. Species: {taxon}"
                        ],
                "source": "wikimedia"
            })

        processed += 1
        if processed%1000 == 0:
            print("Processed: ", processed, "entries")

print("Processed: ", processed, "entries")
with open(f"./data/{dataset_subset}_per_image_cleaned.json", 'w') as f:
    json.dump(per_image_cleaned, f)
