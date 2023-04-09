import ijson
import json

processed = 0
per_image_cleaned = []

# Separate the species name from the description
# Add an entry for animal type, place in taxonomy. Further perusal of wikidata shows that their information is inaccurat
#   - will forego this step for now. Might augment data from other sources in the future.

dataset_subset = "nonspecies_mono"
dictz = []
filename = f'./data/{dataset_subset}_filtered_taxons.json'
with open(f"./data/{dataset_subset}_cleaned.csv", 'w') as g:
    g.write("taxon,parent_taxon\n")
    with open(filename) as f:
        for item in ijson.items(f, "item"):

            id = item["id"]
            if item["claims"].get('P225') is None:
                taxon = ""
            elif 'datavalue' not in item["claims"]["P225"][0]["mainsnak"].keys():
                print("id: ", id, "\n", item["claims"]["P225"][0]["mainsnak"].keys())
                taxon = ""
            else:
                taxon =  item["claims"]["P225"][0]["mainsnak"]["datavalue"]["value"]

            if item["claims"].get('P171') is None:
                parent_taxon = ""
            elif 'datavalue' not in item["claims"]["P171"][0]["mainsnak"].keys():
                print("id: ", id, "\n", item["claims"]["P171"][0]["mainsnak"].keys())
                parent_taxon = ""
            else:
                parent_taxon =  item["claims"]["P171"][0]["mainsnak"]["datavalue"]["value"]["id"]

            if 'en' not in item["descriptions"].keys():
                print("id: ", id, "\n", item["descriptions"].keys(), type(list(item["descriptions"].keys())))
                try:
                    caption = item["descriptions"][list(item["descriptions"].keys())[0]]["value"]
                except:
                    caption = ''
            else:
                caption = item["descriptions"]["en"]["value"]
        
            dictz.append({'id': id, 'taxon': taxon, 'parent_taxon': parent_taxon, 'caption': caption})

            processed += 1
            if processed%1000 == 0:
                print("Processed: ", processed, "entries")

print("Processed: ", processed, "entries")

from pandas import json_normalize

df = json_normalize(dictz)
df.to_csv(f"./data/{dataset_subset}_per_image_cleaned.csv", encoding='utf-8', index=False)