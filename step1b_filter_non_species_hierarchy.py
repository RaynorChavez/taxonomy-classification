from collections import defaultdict
import time
from typing import DefaultDict

from tqdm import tqdm

from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
from pathlib import Path
import json

from functools import reduce  # forward compatibility for Python 3
import operator


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

def getFromDict(dataDict, mapList):
    for item in mapList:
        if item in dataDict:
            dataDict = dataDict[item]
        else:
            return ""
    return dataDict
    return reduce(operator.getitem, mapList, dataDict)

def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

def map_claims_id(claim, id=False):
    if id:
        return [c['mainsnak'].get('datavalue', {'value':{'id':''}})['value']['id'] for c in claim]     
    return [c['mainsnak']['datavalue']['value'] for c in claim]

def return_values(entity_dict):
    out_dict = defaultdict(lambda x: {})
    types = ['id', 'labels.en.value', 'descriptions.en.value', 'claims.P171', 'claims.P18', 'claims.P105', 'lastrevid', 'aliases.en.value', ]#'type', 'pageid', 'ns', 'title','modified']
    for i in types:
        # print(i)
        li = i.split('.')
        if li[-1]=='value':
            out_dict[li[0]] = getFromDict(entity_dict, li)
        elif li[0]!='claims':
            out_dict[li[0]] = {}
            setInDict(out_dict, li, getFromDict(entity_dict, li))
        elif li[1]=='P171':
            setInDict(out_dict, ['parent_taxon'], map_claims_id(getFromDict(entity_dict, li),id=True))
        elif li[1]=='P105':
            setInDict(out_dict, ['taxon_rank'], map_claims_id(getFromDict(entity_dict, li),id=True))
        elif li[1]=='P18':
            setInDict(out_dict, ['image_fn'], map_claims_id(getFromDict(entity_dict, li)))
    return out_dict

def apply_entry(entity_dict):
     if entity_dict["type"] == "item":
        entity = WikidataItem(entity_dict)
        if is_instance_of_taxon(entity):
            return return_values(entity._entity_dict)

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
    wjd_dump_path = "./data/wikidata-20230213-all.json.bz2" # "./data/wikidata-20220103-all.json.gz" # "./data/wikidata-20230213-all.json.bz2"
    wjd = WikidataJsonDump(wjd_dump_path)

    li = []

    # create an iterable of WikidataItem representing politicians
    processed = 0
    t1 = time.time()

    print("done wjd")

    import pandas as pd

    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)


    with open('data/species_hierarchy.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        start = 000000
        i = 0
        for item in tqdm(wjd.__iter__()):
            '''
            if i<start:
                i+=1
                continue
            elif i>count+start:
                break
            else:
                i+=1'''
            fix_item = apply_entry(item)
            if fix_item is None:
                continue
            f.write(json.dumps(fix_item))
            f.write(', \n')
        f.write('\n]')


'''
    with open("data/non_species_hierarchy.json", "w", encoding='utf-8') as fp:
        json.dump(li, fp)
''' 


## write the iterable of WikidataItem to disk as JSON
#out_fname = "./data/filtered_taxons.json"
#dump_entities_to_json(taxons, out_fname)
#wjd_filtered = WikidataJsonDump(out_fname)

# load filtered entities and create instances of WikidataItem
#for ii, entity_dict in enumerate(wjd_filtered):
#    item = WikidataItem(entity_dict)