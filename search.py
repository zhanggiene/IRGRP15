from pywebio.input import  NUMBER
from pywebio.output import put_table, put_text,put_html
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
import plotly.express as px
import requests
from datetime import datetime
import time
import pandas as pd
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import httpx
import asyncio
import aiohttp
import langid
from pywebio.platform.tornado_http import start_server as async_start_server
import httpx
from html import unescape

url = "https://httpbin.org/post"
data = {"message": "Hello, world2!"}

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

SearchField=[ {
            "label": "Text",
            "value": "Text",
            "selected": True,
        },
        {
            "label": "Summary",
            "value": "Summary",
        },{
            "label": "ProfileName",
            "value": "ProfileName",
        },{
            "label": "ProductId",
            "value": "ProductId",
        },]

def search_solr(sortField,sortOrder,queryfield=None,query=None, fq=None, start=0, rows=10):
    solr_url = "http://localhost:8983/solr/test2/select"
    params = {
        "q": f"*:*",
        "start": start,
        "rows": rows,
        'sort': sortField +' '+ sortOrder,
        "wt": "json"
    }
    if fq:
        params["fq"] = fq
    if query:
        params["q"]=f"{queryfield}:{query}"
        
    response = requests.get(solr_url, params=params)
    return response.json()

async def score_bar_graph():
    input_date_time_end=await pin.input_date_time_end
    input_date_time_start= await pin.input_date_time_start
    sort_field =await pin.sort_field
    radio =await pin.radio
    query_field=await pin.query_field
    query= await pin.query
    scores=[]
    count=[]
    fq=[]
    data={}
    start_timestamp=0
    end_timestamp=int(time.time())
    if (input_date_time_start):
        try:
            start_date_time_obj = datetime.strptime(input_date_time_start, '%d/%m/%Y %H:%M')
            start_timestamp = (int)(start_date_time_obj.timestamp())
        except:
            print("start time string has some problem")
    if (input_date_time_end):
        try:
            end_date_time_obj = datetime.strptime(input_date_time_end, '%d/%m/%Y %H:%M')
            end_timestamp =  end_date_time_obj.timestamp()
        except:
            print("end time string has some problem ")
    fq.append(f"Time:[{start_timestamp} TO {end_timestamp}]")
    for i in range(1,6):
        fqcopy=fq.copy()
        fqcopy.append(f"Score:[{i} TO { i}]")
        results = search_solr(sortField=sort_field,sortOrder=radio,queryfield=query_field,query=query,fq=" AND ".join(fqcopy), start=0, rows=1)
        #print(results)
        count.append(results['response']['numFound'])
        scores.append(i)
    data['score']=scores
    data['count']=count
    df = pd.DataFrame(data)
    fig = px.bar(df, x='score', y='count')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    with use_scope("query_content",clear=True):
        put_html(html)

    
    
async def addData(n):
    csv_file_path = 'crawlreview.csv'
    solr_url = "http://localhost:8983/solr/test2"
    asinlst = await getnewasin()
    min_score=await pin.min_score
    maximum_score= await pin.maximum_score
    input_date_time_end=await pin.input_date_time_end
    input_date_time_start= await pin.input_date_time_start
    start_timestamp=0
    end_timestamp=int(time.time())
    if (input_date_time_start):
        try:
            start_date_time_obj = datetime.strptime(input_date_time_start, '%d/%m/%Y %H:%M')
            start_timestamp = (int)(start_date_time_obj.timestamp())
        except:
            print("start time string has some problem")
    if (input_date_time_end):
        try:
            end_date_time_obj = datetime.strptime(input_date_time_end, '%d/%m/%Y %H:%M')
            end_timestamp =  end_date_time_obj.timestamp()
        except:
            print("end time string has some problem ")
    newdata = await getnewdata(asinlst,mintime=start_timestamp,maxtime=end_timestamp,minscore=min_score,maxscore=maximum_score,reviewctr=n)
    print("crawling done")
    df = pd.DataFrame.from_dict(newdata)
    df.to_csv(csv_file_path, index=False, header=True)
    update_url = f"{solr_url}/update/csv?commit=true"

    headers = {"Content-Type": "application/csv"}
    with open(csv_file_path, "rb") as csv_file:
        csv_data = csv_file.read()
    response = requests.post(update_url, data=csv_data, headers=headers)

    if response.status_code == 200:
        print("Documents added successfully!")
    else:
        print(f"An error occurred while adding documents: {response.text}")
    with open(csv_file_path, 'r') as csv_file:
        csv_data = csv_file.read()



async def add_data_func():
    with use_scope("query_content",clear=True):
            put_loading()
    n=await pin.review_num
    await addData(n)
    with use_scope("query_content",clear=True):
            put_text("data uploaded to server")
            toast("data added successfully")
    
async def search_fun():
    fq = []
    min_score=await pin.min_score
    maximum_score= await pin.maximum_score
    input_date_time_end=await pin.input_date_time_end
    input_date_time_start= await pin.input_date_time_start
    page=await pin.page
    rows=await pin.rows
    sort_field =await pin.sort_field
    radio =await pin.radio
    query_field=await pin.query_field
    query= await pin.query
    rows = await pin.rows
    fq.append(f"Score:[{min_score} TO { maximum_score}]")

    start_timestamp=0
    end_timestamp=int(time.time())
    if (input_date_time_start):
        try:
            start_date_time_obj = datetime.strptime(input_date_time_start, '%d/%m/%Y %H:%M')
            start_timestamp = (int)(start_date_time_obj.timestamp())
        except:
            print("start time string has some problem")
    if (input_date_time_end):
        try:
            end_date_time_obj = datetime.strptime(input_date_time_end, '%d/%m/%Y %H:%M')
            end_timestamp =  end_date_time_obj.timestamp()
        except:
            print("end time string has some problem ")
    fq.append(f"Time:[{start_timestamp} TO {end_timestamp}]")

    start = (page - 1) * rows

    results = search_solr(sortField=sort_field,sortOrder=radio,queryfield=query_field,query=query,fq=" AND ".join(fq), start=start, rows=rows)
    docs = results['response']['docs']
    headers = ["ProductId", "ProfileName", "HelpfulnessNumerator", "Score", "Time", "Summary", "Text"]
    data = [[doc.get(header, "") for header in headers] for doc in docs]
    with use_scope("query_content",clear=True):
        put_text("Totol results:" + str(results['response']['numFound']))
        put_table(data, header=headers)
        
async def search_engine():
    put_text("Search Engine")
    put_row([put_input('query',label='Text input',placeholder="search for anything)"),None,put_select('query_field', options=SearchField, label='Sort by')])
    put_row([

    # Input fields
    put_input('input_date_time_start',label='start time', placeholder="date time in this format(dd/mm/yyyy HH:MM)"),None,
    put_input('input_date_time_end',label='end time', placeholder="date time in this format(dd/mm/yyyy HH:MM)")])
    put_row([
    put_input('min_score',label='minimum score',type=NUMBER,value=0),None,
    put_input('maximum_score',label="maximum score",type=NUMBER,value=5)])
    put_row([
    put_radio('radio', options=ascendOptions, label='Sort', inline=False, value=None),None,
    put_select('sort_field', options=ascendOptionsField, label='Sort by')])
    put_input('page',label="page number",type=NUMBER,value=1)
    put_input('rows',label="rows per page",type=NUMBER,value=10)
    put_buttons(['Search'], lambda _: run_async(search_fun()))
    put_buttons(['score_barchart'], lambda _: score_bar_graph())
    put_input('review_num',label='Number of Additional reviews to crawl',type=NUMBER,value=5)
    put_buttons(['add_data'], lambda _:run_async(add_data_func()))





async def getnewasin():
    maxpage = 6
    urlbase = 'https://www.amazon.sg/s?k=grocery&i=amazonfresh&crid=47HZTXS3UKAC&sprefix=grocery%2Camazonfresh%2C298&ref=nb_sb_noss_1'
    urllist = [urlbase]
    for pgctr in range(2, maxpage):
        url = f'https://www.amazon.sg/s?k=grocery&i=amazonfresh&bbn=8112913051&page=2&crid=47HZTXS3UKAC&qid=1679385651&sprefix=grocery%2Camazonfresh%2C298&ref=sr_pg_{pgctr}'
        urllist.append(url)
    asins = []
    s = AsyncHTMLSession()

    for url in urllist:
        print(url)
        r = await s.get(url)
        await r.html.arender(sleep=1)
        items = r.html.find('div[data-asin]')

        for item in items:
            if item.attrs['data-asin'] != '':
                asins.append(item.attrs['data-asin'])

    return asins


async def getnewdata(asinlist, mintime=0, maxtime=int(time.time()), minhelp=0, minscore=0, maxscore=5, reviewctr=10):
    asinpool = set(asinlist)
    result = []
    for asin in asinpool:
        amz = Reviews(asin)
        for x in range(1, 500):
            reviews = await amz.pagination(x)
            if reviews is not False:
                reviewlst = await amz.parse(reviews, mintime, maxtime, minhelp, minscore, maxscore, reviewctr)
                for review in reviewlst:
                    result.append(review)
            else:
                break
        if len(result) >= reviewctr:
            break
    return result


class Reviews:
    def __init__(self, asin) -> None:
        self.asin = asin
        self.session = HTMLSession()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                      ' Chrome/111.0.0.0 Safari/537.36'}
        self.url = f'https://www.amazon.sg/product-reviews/{self.asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&' \
                   f'reviewerType=all_reviews&sortBy=recent&pageNumber='

    @staticmethod
    def timeconverter(dt):
        dt = dt.split('on')
        dt = dt[1].strip()
        dt = dt.split()
        mnum = datetime.strptime(dt[1], '%B').month
        date_time = datetime(int(dt[2]), mnum, int(dt[0]), 0, 0)
        utctime = int(time.mktime(date_time.timetuple()))
        return utctime

    def validate(self, username, mintime, maxtime, minhelp, minscore, maxscore, utc, helpcount, rating,body):
        olddf = pd.read_csv('reviewshort.csv', index_col=False)
        if self.asin in olddf['ProductId'] and username in olddf['ProfileName']:
            return False
        if mintime > utc:
            return False
        if maxtime < utc:
            return False
        if minhelp > helpcount:
            return False
        if minscore > rating or rating > maxscore:
            return False
        try:
            lang = langid.classify(body)
        except:
            lang = 'nil'
        if 'en' not in lang:
            return False
        if 'videoUrl' in body:
            return False

        return True


    async def pagination(self, page):
        async_session = AsyncHTMLSession()
        r = await async_session.get(self.url + str(page))
        await r.html.arender(sleep=1)
        
        if not r.html.find('div[data-hook=review]'):
            return False
        else:
            return r.html.find('div[data-hook=review]')


    async def parse(self, reviews, mintime, maxtime, minhelp, minscore, maxscore, reviewctr):
        total = []
        ctr = 0
        for review in reviews:
            print(review)
            await asyncio.sleep(0.05)
            username = review.find('span[class="a-profile-name"]', first=True).text
            try:
                helpcount = int(review.find('span[data-hook="helpful-vote-statement"]', first=True).text[0])
            except:
                helpcount = 0
            dt = review.find('span[data-hook="review-date"]', first=True).text
            utc = self.timeconverter(dt)
            try:
                rating = int(review.find('i[data-hook="review-star-rating"]', first=True).text[0])
            except:
                rating = int(review.find('i[data-hook="cmps-review-star-rating"]', first=True).text[0])
            try:
                title = review.find('a[data-hook="review-title"]', first=True).text
            except:
                title = review.find('span[data-hook="review-title"]', first=True).text
            body = review.find('div[class="a-row a-spacing-small review-data"]', first=True).text
            for item in body:
                x = item.find('span')
                if x == -1 or x is None:
                    continue
                else:
                    body = x.replace('\n', '').strip()
            is_valid=self.validate(username, mintime, maxtime, minhelp, minscore,
                             maxscore, utc, helpcount, rating,body)
            if not is_valid:
                continue

            data = {
                'ProductId': self.asin,
                'ProfileName': username,
                'HelpfulnessNumerator': helpcount,
                'Score': rating,
                'Time': utc,
                'Summary': title,
                'Text': body
            }
            total.append(data)
            ctr += 1
            if ctr >= reviewctr:
                break
        return total



if __name__ == "__main__":
    start_server(search_engine, port=8080,debug=True)
