import random

import pandas as pd
from store.models import Product

# do uruchomienia  exec(open('store/dataloader.py').read()) w shellu

start_idx = 50
how_many = 50
data = pd.read_excel(open('store/sources/books_data.xlsx', 'rb'), sheet_name='Arkusz3')
products_data = []
for i in range(start_idx, start_idx + how_many):
    one_product_data = {data.iloc[i].index[0]: data.iloc[i].values[0],
                        data.iloc[i].index[1]: data.iloc[i].values[1],
                        data.iloc[i].index[2]: data.iloc[i].values[2],
                        data.iloc[i].index[3]: data.iloc[i].values[3],
                        data.iloc[i].index[4]: data.iloc[i].values[4],
                        data.iloc[i].index[5]: data.iloc[i].values[5],
                        data.iloc[i].index[6]: data.iloc[i].values[6],
                        data.iloc[i].index[7]: data.iloc[i].values[7],
                        data.iloc[i].index[8]: data.iloc[i].values[8],
                        data.iloc[i].index[9]: data.iloc[i].values[9]}
    products_data.append(one_product_data)

for i in range(0, how_many):
    Product.objects.create(title=products_data[i]['Book-Title'],
                           author=products_data[i]['Book-Author'],
                           description=products_data[i]['Description'],
                           genre=products_data[i]['Genre'],
                           isbn=products_data[i]['ISBN'],
                           price=random.randint(30, 45) - 0.01,
                           publisher=products_data[i]['Publisher'],
                           year=products_data[i]['Year-Of-Publication'],
                           image_url=products_data[i]['Image-URL-M'],
                           image_big_url=products_data[i]['Image-URL-L'],
                           inventory=random.randint(1, 30))
