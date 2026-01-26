import pandas as pd
#import json
import requests
import utils
from classes import RequestBuilder


# get api template
template = utils.get_template("template2.json")

# pip install openpyxl
# load test data into a pd.DataFrame
df = pd.read_excel("massa.xlsx")

# initialize dicts holding column names and values of a single row
rows = [row._asdict() for row in df.itertuples(index=False)]

for row in rows:
    req = RequestBuilder(template, row)
    method = template['metodo']
    print(f"method:{method}")
    url =req.build_url()
    print(f"URL: {url}")
    params = req.build_param_dict("query")
    print(f"Query params: {params}")
    body = req.build_param_dict("body")
    print(f"Body params: {body}")
    #auth = req.get_intranet_token()
    
    print("------------------")

    #res = requests.request(
    #    method=method,
    #    url=url,
    #    params=params,
    #    body=body
    #    auth=auth
    #)