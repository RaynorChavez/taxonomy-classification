"""
import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
Image.MAX_IMAGE_PIXELS = 10000000000


dataset_subset = "subset1k"

def resize_image(image_path, new_size):
    with Image.open(image_path) as image:
        image = image.resize(new_size)
        return image


def write_image(image, output_folder, filename, image_num):
    output_path = os.path.join(output_folder, filename)
    image.save(output_path)
    if image_num % 500 == 0:
        print(f"Processed {image_num} images...")

def process_images_in_folder(folder_path, output_folder, new_size):
    resize_pool = ThreadPoolExecutor()
    write_pool = ThreadPoolExecutor()
    futures = []

    for i, filename in enumerate(os.listdir(folder_path)):
        if not filename.endswith('.jpg'):
            continue
        image_path = os.path.join(folder_path, filename)
        future = resize_pool.submit(resize_image, image_path, new_size)
        futures.append((future, filename, i + 1))


    for future, filename, image_num in futures:
        resized_image = future.result()
        write_pool.submit(write_image, resized_image, output_folder, filename, image_num)

    resize_pool.shutdown()
    write_pool.shutdown()

if __name__ == '__main__':
    folder_path = f'./data/{dataset_subset}_taxo_data_images'
    output_folder = f'./data/taxo_data_images_{dataset_subset}_resized'
    new_size = (225, 225)
    os.makedirs(output_folder, exist_ok=True)
    process_images_in_folder(folder_path, output_folder, new_size)

"""

import os
import tensorflow as tf
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump


# Set the path to the directory containing the images
dataset_subset = "full"
image_dir = f'./data/{dataset_subset}_taxo_data_images'

# Set the desired image size
img_size = (224, 224)

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
            setInDict(out_dict, ['taxon_rank'], map_claims_id(getFromDict(entity_dict, li),id=True)[0])
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

wjd_dump_path = "./data/wikidata-20230213-all.json.bz2" # "./data/wikidata-20220103-all.json.gz" # "./data/wikidata-20230213-all.json.bz2"
wjd = WikidataJsonDump(wjd_dump_path)

# Loop through the list of image files


# https://www.kaggle.com/code/ashrafkhan94/fruits-classification-image-processing-using-tpu/notebook
tpu = tf.distribute.cluster_resolver.TPUClusterResolver()
tf.config.experimental_connect_to_cluster(tpu)
tf.tpu.experimental.initialize_tpu_system(tpu)


# instantiate a distribution strategy
strategy = tf.distribute.experimental.TPUStrategy(tpu)


BATCH_SIZE = 16 * strategy.num_replicas_in_sync


AUTO = tf.data.experimental.AUTOTUNE


dataset = (
        tf.data.Dataset\
        .from_tensor_slices((wjd.__iter__()))\
        .map(apply_entry, num_parallel_calls=AUTO)\
        .batch(BATCH_SIZE).prefetch(AUTO)
)