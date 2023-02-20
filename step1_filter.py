import time

from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
import multiprocessing as mp
from pathlib import Path
import json

dataset_subset = "subset1k"
# -1 for all
desired_entries_count = 1000

P_OCCUPATION = "P106"
P_INSTANCE_OF = "P31"
P_TAXON_RANK = "P105"
P_IMAGE = "P18"
Q_POLITICIAN = "Q82955"
Q_TAXON = "Q16521"
Q_SPECIES = "Q7432"

def is_instance_of_taxon(item: WikidataItem, truthy: bool = True) -> bool:
    """Return True if the Wikidata Item is an instance of taxon."""
    if truthy:
        claim_group = item.get_truthy_claim_group(P_INSTANCE_OF)
    else:
        claim_group = item.get_claim_group(P_INSTANCE_OF)
    
    taxon_qids = [
        claim.mainsnak.datavalue.value["id"]
        for claim in claim_group
        if claim.mainsnak.snaktype == "value"
    ]
    return Q_TAXON in taxon_qids

def is_rank_species(item: WikidataItem, truthy: bool = True) -> bool:
    """Return True if the Wikidata Item is of rank species."""
    if truthy:
        claim_group = item.get_truthy_claim_group(P_TAXON_RANK)
    else:
        claim_group = item.get_claim_group(P_TAXON_RANK)
    
    taxon_rank_qids = [
        claim.mainsnak.datavalue.value["id"]
        for claim in claim_group
        if claim.mainsnak.snaktype == "value"
    ]
    return Q_SPECIES in taxon_rank_qids

def has_image(item: WikidataItem, truthy: bool = True) -> bool:
    """Return True if the Wikidata Item has image."""
    if truthy:
        claim_group = item.get_truthy_claim_group(P_IMAGE)
    else:
        claim_group = item.get_claim_group(P_IMAGE)
    
    return len(claim_group) > 0


def has_occupation_politician(item: WikidataItem, truthy: bool = True) -> bool:
    """Return True if the Wikidata Item has occupation politician."""
    if truthy:
        claim_group = item.get_truthy_claim_group(P_OCCUPATION)
    else:
        claim_group = item.get_claim_group(P_OCCUPATION)

    occupation_qids = [
        claim.mainsnak.datavalue.value["id"]
        for claim in claim_group
        if claim.mainsnak.snaktype == "value"
    ]
    return Q_POLITICIAN in occupation_qids

# create path if doesn't exist
Path('./data/').mkdir(parents=True, exist_ok=True)

# create an instance of WikidataJsonDump
wjd_dump_path = "./data/wikidata-20230213-all.json.bz2"
wjd = WikidataJsonDump(wjd_dump_path)

# create an iterable of WikidataItem representing politicians
processed = 0
t1 = time.time()

with open(f"./data/{dataset_subset}_filtered_taxons.json", "a") as output:
    output.truncate(0)
    output.write("[")
    first_object = True  # flag to keep track of first object
    for ii, entity_dict in enumerate(wjd):

        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)
            if is_instance_of_taxon(entity):
                if is_rank_species(entity):
                    if has_image(entity):
                        if not first_object:
                            # add a comma before each object after the first one
                            output.write(",")
                        else:
                            first_object = False  # set flag to False after writing the first object
                        output.write(json.dumps(entity._entity_dict))
                        processed += 1

        if ii % 1000 == 0:
            t2 = time.time()
            dt = t2 - t1
            print(
                "found {} taxons among {} entities [entities/s: {:.2f}]".format(
                    processed, ii, ii / dt
                )
            )

        if ii > desired_entries_count and desired_entries_count >= 0:
            break

    output.write("]")
    output.close

## write the iterable of WikidataItem to disk as JSON
#out_fname = "./data/filtered_taxons.json"
#dump_entities_to_json(taxons, out_fname)
#wjd_filtered = WikidataJsonDump(out_fname)

# load filtered entities and create instances of WikidataItem
#for ii, entity_dict in enumerate(wjd_filtered):
#    item = WikidataItem(entity_dict)