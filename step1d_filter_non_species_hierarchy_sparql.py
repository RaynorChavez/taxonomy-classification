from tqdm import tqdm
from time import sleep
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)
import json

def get_val(entry):
  if entry['type']=='uri':
      return entry['value'].split('/')[-1]
  elif entry['type']=='literal':
      return entry['value']
def send_query(sparql_query):
  while True:
        res = return_sparql_query_results(sparql_query)
        code = res.status_code
        res = res.content
        if code == 200:
          break
        sleep(3)
  return res
lenn = -1
running_val = 0
run = 0
limit = 100
for k in range(65,91): # 65 start
  for j in [_ for _ in range(65,91)] + [32]:
    for i in [__ for __ in range(65,91)] + [32]: # 65 start
      
      if k<66:
        continue
      elif k==66 and j<69:
        continue
      elif j==69 and i<70:
        continue
      
      sparql_query = """
SELECT ?item ?itemLabel ?taxonName ?taxonRank ?parentTaxon ?image WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
  {
    SELECT ?item ?taxonName ?taxonRank ?parentTaxon ?image WHERE {
      ?item wdt:P18 ?image.
      ?item wdt:P225 ?taxonName.
      ?item wdt:P105 ?taxonRank.
      ?item wdt:P171 ?parentTaxon.
      ?item p:P31 ?statement0.
      ?statement0 (ps:P31/(wdt:P279*)) wd:Q16521.
      FILTER(SUBSTR(?taxonName, 1, 3) = '"""
      sparql_query+= chr(k) + chr(j).lower() + chr(i).lower() + "').\n  }\n  LIMIT " + str(limit) + "}\n}"


      print(chr(k) + chr(j).lower() + chr(i).lower())
      
      code = 0
      res = send_query(sparql_query)
      res = json.loads(res, strict=False)
      
      lenn = len(res['results']['bindings'])
      print(f'Query executed! {lenn} were found.')

      if lenn >= 100:
        with open('again.log', 'a') as f:
          print('Skipping...')
          f.write(''.join([chr(k),chr(j),chr(i)])+'\n')
          continue

      with open('data/new_non_species_hierarchy2.csv', 'a', encoding='utf-8') as f:
          if k==65:
            f.write(','.join(res['head']['vars']))
            f.write('\n')
          print(run)
          for z in tqdm(res['results']['bindings']):
              f.write(','.join(['"'+get_val(z[col])+'"' for col in res['head']['vars']]))
              f.write('\n')
      running_val+=lenn
      run+=1
