from pywebio.input import  NUMBER
from pywebio.output import put_table, put_text
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
import requests
from datetime import datetime
import time
ascendOptions=[
        {
            "label": "Increasing",
            "value": 'asc',
            "selected": True,
        },
        {
            "label": "Decreasing",
            "value": 'desc',
        },
    ]

ascendOptionsField=[ {
            "label": "Score",
            "value": "Score",
            "selected": True,
        },
        {
            "label": "Time",
            "value": "Time",
        },]

def search_solr(query,sortField,sortOrder, fq=None, start=0, rows=10):
    solr_url = "http://localhost:8983/solr/test2/select"
    params = {
        "q": "*:*",
        "start": start,
        "rows": rows,
        'sort': sortField +' '+ sortOrder,
        "wt": "json"
    }
    if fq:
        params["fq"] = fq

    response = requests.get(solr_url, params=params)
    return response.json()

def search_fun():
    fq = []
    fq.append(f"Score:[{pin.min_score} TO { pin.maximum_score}]")
    start_timestamp=0
    end_timestamp=int(time.time())
    if (pin.input_date_time_start):
        try:
            start_date_time_obj = datetime.strptime(pin.input_date_time_start, '%d/%m/%Y %H:%M')
            start_timestamp = (int)(start_date_time_obj.timestamp())
        except:
            print("start time string has some problem")
    if (pin.input_data_time_end):
        try:
            end_date_time_obj = datetime.strptime(pin.input_date_time_end, '%d/%m/%Y %H:%M')
            end_timestamp =  end_date_time_obj.timestamp()
        except:
            print("end time string has some problem ")
    fq.append(f"Time:[{start_timestamp} TO {end_timestamp}]")

    start = (pin.page - 1) * pin.rows
    rows = pin.rows
    results = search_solr(pin.query,pin.sort_field,pin.radio,fq=" AND ".join(fq), start=start, rows=rows)
    print(results)
    docs = results['response']['docs']
    print(results)
    headers = ["ProductId", "ProfileName", "HelpfulnessNumerator", "Score", "Time", "Summary", "Text"]
    data = [[doc.get(header, "") for header in headers] for doc in docs]
    with use_scope("query_content",clear=True):
        put_text("Totol results:" + str(results['response']['numFound']))
        put_table(data, header=headers)
        
    

def search_engine():
    put_text("Search Engine")
    put_input('query',label='Text input',placeholder="search for anything)")
    put_row([

    # Input fields
    put_input('input_date_time_start',label='start time', placeholder="date time in this format(dd/mm/yyyy HH::MM)"),None,
    put_input('input_date_time_end',label='end time', placeholder="date time in this format(dd/mm/yyyy HH::MM)")])
    put_row([
    put_input('min_score',label='minimum score',type=NUMBER,value=0),None,
    put_input('maximum_score',label="maximum score",type=NUMBER,value=5)])
    put_row([
    put_radio('radio', options=ascendOptions, label='Sort', inline=False, value=None),None,
    put_select('sort_field', options=ascendOptionsField, label='Sort by')])
    put_input('page',label="page number",type=NUMBER,value=1)
    put_input('rows',label="rows per page",type=NUMBER,value=10)
    put_buttons(['Search'], lambda _: search_fun())

if __name__ == "__main__":
    start_server(search_engine, port=8080)
