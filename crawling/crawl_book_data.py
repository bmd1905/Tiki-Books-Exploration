import pandas as pd
import requests
import time
import random
from tqdm import tqdm

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-guest-token': '8jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

params = (
    ('platform', 'web'),
    ('spid', 74021318)
    #('include', 'tag,images,gallery,promotions,badges,stock_item,variants,product_links,discount_tag,ranks,breadcrumbs,top_features,cta_desktop'),
)

def parser_product(json):
    d = dict()
    d['title'] = json.get('name')

    # Get author(s)
    try:
        d['authors'] = json.get('authors')[0].get('name')
    except:
        d['authors'] = ""
    d['original_price'] = json.get('original_price')
    d['current_price'] = json.get('current_seller').get('price')
    d['quantity'] = json.get('all_time_quantity_sold')
    d['catagory'] = json.get('breadcrumbs')[3].get('name')
    d['n_review'] = json.get('review_count')
    d['avg_rating'] = json.get('rating_average')

    # Get number of pages
    d['pages'] = ""
    for i in range(15):
        try:
            if json.get('specifications')[0].get('attributes')[i].get('code')  == 'number_of_page':
                d['pages'] = json.get('specifications')[0].get('attributes')[i].get('value')
                break
        except:
            continue

    # Get publisher
    d['manufacturer'] = ""
    for i in range(15):
        try:
            if json.get('specifications')[0].get('attributes')[i].get('code') == 'manufacturer':
                d['manufacturer'] = json.get('specifications')[0].get('attributes')[i].get('value')
                break
        except:
            continue

    # Get cover_link
    try:
        d['cover_link'] = json.get('images')[1].get('base_url')
    except:
        d['cover_link'] = json.get('images')[0].get('base_url')

    return d


df_id = pd.read_csv('book_id.csv')
p_ids = df_id.id.to_list()
print(p_ids)
result = []
for pid in tqdm(p_ids, total=len(p_ids)):
    try:
        response = requests.get('https://tiki.vn/api/v2/products/{}'.format(pid), headers=headers, params=params)
        if response.status_code == 200:
            print('Crawling product id {} successful!'.format(pid))
            result.append(parser_product(response.json()))
    except:
        continue
df_product = pd.DataFrame(result)
df_product.to_csv('crawled_book_data.csv', index=False)
