import time

from tqdm.contrib.concurrent import process_map
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
import multiprocessing as mp
from pathlib import Path
import json

dataset_subset = "subset"
# -1 for all
desired_entries_count = -1

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

def apply_entry(entity_dict):
     if entity_dict["type"] == "item":
        entity = WikidataItem(entity_dict)
        if is_instance_of_taxon(entity) and not is_rank_species(entity):
            return entity._entity_dict

def get_x(iter, x):
    li = []
    for i, key in enumerate(iter):
        if x==i:
            break
        li.append(key)
    return li

if __name__=='__main__':
    # create path if doesn't exist
    Path('./data/').mkdir(parents=True, exist_ok=True)
    
    # create an instance of WikidataJsonDump
    wjd_dump_path = "./data/wikidata-20220103-all.json.gz"
    wjd = WikidataJsonDump(wjd_dump_path)


    # create an iterable of WikidataItem representing politicians
    processed = 0
    t1 = time.time()

    li = process_map(apply_entry, get_x(wjd.__iter__(), 10000), chunksize=1000, max_workers=8)
    
    print(len(li))

    li = list(filter(lambda x: x is not None, li))

    print(len(li))

    with open("non_species_hierarchy.json", "w", encoding='utf-8') as fp:
        json.dump(li, fp)
    


## write the iterable of WikidataItem to disk as JSON
#out_fname = "./data/filtered_taxons.json"
#dump_entities_to_json(taxons, out_fname)
#wjd_filtered = WikidataJsonDump(out_fname)

# load filtered entities and create instances of WikidataItem
#for ii, entity_dict in enumerate(wjd_filtered):
#    item = WikidataItem(entity_dict)