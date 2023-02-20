import ijson
import json

per_taxon_cleaned = []

processed = 0
filename = './data/filtered_taxons.json'
with open(filename) as f:
    for item in ijson.items(f, "item"):

        images = []
        for image in item["claims"]["P18"]:
            img_filename = image["mainsnak"]["datavalue"]["value"]
            img_type = image["mainsnak"]["datatype"]
            if img_type == "commonsMedia":
                img_filename = "_".join(img_filename.split(" "))
                images.append(img_filename)

        id = item["id"]
        taxon =  item["claims"]["P225"][0]["mainsnak"]["datavalue"]["value"]
        caption = item["descriptions"]["en"]["value"]

        per_taxon_cleaned.append({ 
            "id": id,
            "taxon": taxon,
            "captions": [f"This is an example of species {taxon}.",
                        f"Image of an animal with taxon name: {taxon}.",
                        f"Species: {taxon}. {caption}",
                        f"{caption}",
                        f"{caption}. Taxon Name: {taxon}"
                        f"{caption}. Species: {taxon}"
                        ],
            "images": images # Change this to "wiki images and add a new field google images"
        })

        processed += 1
        if processed >= 1000:
            print(f"Processed {processed} taxons")


with open("./data/per_taxon_cleaned.json", 'w') as f:
    json.dump(per_taxon_cleaned, f)

# To get image, https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Sample.png&width=300
# Source: https://stackoverflow.com/a/65412349/21110285