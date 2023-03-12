import pandas as pd
import requests as r

if __name__=="__main__":
    df = pd.read_csv("data/test_data_1.csv")
    for link, fn in zip(df['source_image'], df['fn']):
        with open("images/"+fn, 'wb') as f:
            f.write(r.get(link).content)
