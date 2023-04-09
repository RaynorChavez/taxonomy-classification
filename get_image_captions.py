import pandas as pd
import os
import requests as r
from bs4 import BeautifulSoup
import httpx
import itertools
from time import sleep

async def extract(sample, client, run=1):
    QUERY_POINT = "https://commons.wikimedia.org/wiki/File:"
    if run==10:
        return "Error! Too many retries."
    res = await client.get(QUERY_POINT + sample, timeout=None)
    if res.status_code==200:
        soup = BeautifulSoup(res.text, 'html.parser')
        print(sample)
        e = soup.select('td#fileinfotpl_desc')
        if len(e)>0:
            e = e[0].find_next_siblings()[0]
            table = e.find('table')
            if table is not None:
                table.clear()
            f = e.select('.en')
                
            if len(f)<1:
                le = e
            else:
                le = f[0]
        else:
            e = soup.select('div.wbmi-entityview-caption')
            f = [el for el in e if el.select('.wbmi-language-label')[0].text=='English']
            le = f[0]
            if f[0].text.find('Add a one-line')!=-1:
                le = None
                f = soup.select('div.description.mw-content-ltr')
                if len(f)<0:
                    le = f[0]
        if le is not None:
            le = le.text.strip()
            if len(le)>0:
                return le
        else:
            f = soup.select('td > div.description.mw-content-ltr.en')
            if len(f) > 0:
                return f[0].text
            if len([el for el in soup.select('title') if el.text=="Wikimedia Error"])!=0:
                sleep(3)
                out = await extract(sample, client, run=run+1)
                return out
            return res.text
    else:
        out = await extract(sample, client, run=run+1)
        return out
'''
from time import time
start = time()
df['cap'] = df.apply(lambda x: extract(x), axis=1)
print(time()-start)
'''

from time import time
import asyncio  
import aiohttp

def fetch_page(url, idx):   
    response = yield from aiohttp.request('GET', url)

    if response.status == 200:
        print("data fetched successfully for: %d" % idx)
    else:
        print("data fetch failed for: %d" % idx)
        print(response.content, response.status)

async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro
    return await asyncio.gather(*(sem_coro(c) for c in coros), return_exceptions=True)

async def main(df):
    semaphore = asyncio.Semaphore(8)

    async def sem_coro(coro):
        async with semaphore:
            return await coro
    async with httpx.AsyncClient(limits = httpx.Limits(max_connections=8)) as client:
        return await asyncio.gather(
            *(sem_coro(c) for c in map(extract, df['filename'], itertools.repeat(client),)), return_exceptions=True
        )

if __name__ == '__main__':
    os.chdir('./data')
    df = pd.read_csv('full_per_image_cleaned.csv')
    df['filename'] = df['filename'].str[17:]

    start = time()
    loop = asyncio.get_event_loop()
    
    z = 4 # interval
    
    for i in range(4,5):
        smol = df.iloc[i*(len(df)//z):(i+1)*(len(df)//z)].copy()
        out = loop.run_until_complete(main(smol))
        smol['image_captions'] = out
        smol.to_csv(f'image_captions_{i}.csv',index=False,encoding='utf-8')
        break
    '''
    filenames = ['Campanula_adiyamanensis.jpg', 'Cercopis_septemmaculata_(DSCN0578,_crop_0480x0480px).jpg', 'Nitela_philippinica_02.jpg']

    df = df[df['filename'].isin(filenames)].copy()
    print(df)
    out = loop.run_until_complete(main(df))
    df['image_captions'] = out
    df.to_csv('image_captions_4.csv',index=False,encoding='utf-8')
    '''
    
    print(time()-start)
