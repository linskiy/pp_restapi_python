# PRICEPLAN REST API
```
api_key = 'xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
pp = PricePlan(user='priceplan', key=api_key)
#get clients
#сроздаем пользователя
new_client = {
    "name": "pp_test1",
    "type": 1,
    "values": {
        "29": "test@mail.ru",
        "34": "Ivan Ivonov"
    }
}
client = pp.get('clients/', BODY=new_client)
print client


#создаем подписку
new_subscribe = {
    "product": 1,
    "values": {
        "36": 50,
        "37": c_user.username
    },
    "period": 1,
    "client": client['data']['id],
    "doc_number": "",
    "doc_date": None,
    "coupons": [""]
}
subscribe = pp.get('subscribes/', BODY=new_subscribe)
print subscribe


#запрашиваем информацию о подписках
subscribe_filter={
    'filters': [
        {'field': 'client__id', 'operator': 'eq', 'value': client['data']['id]}
    ]
}
s = pp.get('subscribes', http_method='GET', filter=subscribe_filter,
            fields='subscribe__id,subscribe__product,subscribe__blocking,subscribe__start,client__id,subscribe__delete,product__name',
            pageSize = '100')['data']
​
for i in s:
    print pp.get('subscribes/%s' % i['subscribe__id'], http_method='GET')['data']
```