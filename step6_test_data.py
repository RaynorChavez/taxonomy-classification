from collections import Counter
import json
from time import sleep
import requests as r
import pandas as pd

if __name__=="__main__":
    json_obj = {}
    headers = {"Authorization": "O551VU0fZxrAIeUFWYMOEHk0xGPkHSgHUjcXd5S3PuebWdZuy4hD1gxp"}
    with open("data/subset10k_per_image_cleaned.json", 'r', encoding='utf-8') as f:
        json_obj = json.load(f)
    c = Counter([js['species'] for js in json_obj])
    c = {x:y for x, y in c.items() if y>1}
    '''
    li = []
    done = 121
    df = pd.read_csv("data/test_data_1.csv")
    to_find = set(c.keys()) - set(df['species'])
    print(len(to_find))
    c = {x:y for x,y in c.items() if x in to_find}
    for key, item in c.items():
        if item < 2:
            continue
        link = f"https://api.pexels.com/v1/search?query={'%20'.join(key.split())}"
        print(str(round((784-done)/1133*100, 2)), link)
        done-=1
        if done>=0:
            continue
        response = r.get(link, headers=headers)
        while response.status_code!=200:
            sleep(3)
            response = r.get(link, headers=headers)
        photos = response.json().get('photos', [])
        if len(photos) == 0:
            print("lacking")
        for image in photos[:item]:
            li.append((key, image['url'], image['src']['original'].split('/')[-1], image['photographer'], image['src']['medium'], image['alt']))
    
    df = pd.DataFrame(li, columns=['species', 'url', 'fn', 'photographer', 'source_image', 'alt_text'])
    df.to_csv('data/test_data_3.csv', index=False, encoding='utf-8')
    '''