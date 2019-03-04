from __future__ import print_function
from botocore.vendored import requests

def lambda_handler(event, context):
    categories = 'F:Food, H:Health, T:Transportation, G:Groceries, O:Other, L:Leisure'
    key = {'F': 'Food', 'H':'Health', 'T':'Transportation', 'G':'Groceries', 'O':'Other', 'L':'Leisure'}
    print("Received event: " + str(event))
    
    category, item, price = txt_parser(event['Body'])
    if category in key:
    	update_receipt_log(item, price, key[category])
    	total = get_category_total(key[category], price)
    	return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
               '<Response><Message>' + 'You have ' + str(total) + ' dollars in your ' + key[category] + ' budget.' + '</Message></Response>'
    else:
        return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
               '<Response><Message>'+ 'I don\'t understand. Please refer to key: ' + categories+ ' and send msg in this format: {Key}-{Item}-{Price}' + '</Message></Response>'
               

def get_category_total(category, amt):
	headers = {
	'Authorization': 'Bearer #######',
	}
	url = "https://api.airtable.com/v0/appnWJOP1Re0979C4/tbleE45Xxm1hzve5e?filterByFormula=(%7BName%7D+%3D+'{}')".format(category)
	response = requests.get(url, headers=headers).json()

	total = response['records'][0]['fields']['Total'] - amt

	#making a request to update the total
	headers = {
    'Authorization': 'Bearer keyJRfDna5qHRjXk3',
    'Content-Type': 'application/json',
	}

	data = '{{"fields": {{"Name": "{}", "Total": {}}}}}'.format(category, total)

	response = requests.patch('https://api.airtable.com/v0/appnWJOP1Re0979C4/Categories/recZe4QOzRdEnGSqQ', headers=headers, data=data)

	return total

def txt_parser(msg):
	sections = msg.split('-')
	try:
		category = sections[0]
		item = sections[1]
		price = float(sections[2])
	except:
		category = item = price = None
	return category, item, price

def update_receipt_log(item, price, category):
	headers = {
	    'Authorization': 'Bearer #######',
	    'Content-Type': 'application/json',
	}

	data = '{{"fields": {{"Short Description": "{}", "Total": {}, "Category": "{}"}}}}'.format(item, price, category)

	response = requests.post('https://api.airtable.com/v0/appnWJOP1Re0979C4/Receipt%20Log', headers=headers, data=data)
