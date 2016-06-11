#!/usr/bin/env python

import requests, json, random, string, time, sys

url = "http://tvpapi.as.tvinci.com/v3_4/gateways/jsonpostgw.aspx"

querystring = {"m":"SearchAssets"}

search_query = ' '.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(2))
print "search_query:'%s'" %(search_query)

payload = "{\n    \"initObj\": {\n        \"Locale\": {\n            \"LocaleLanguage\": \"\",\n            \"LocaleCountry\": \"\",\n            \"LocaleDevice\": \"\",\n            \"LocaleUserState\": \"Unknown\"\n        },\n        \"Platform\": \"Web\",\n        \"SiteGuid\": \"\",\n        \"DomainID\": 0,\n        \"UDID\": \"\",\n        \"ApiUser\": \"tvpapi_225\",\n        \"ApiPass\": \"11111\"\n    },\n    \"filter_types\": [389,390,391],\n    \"filter\": \"seriesMainTitle^'%s'\",\n    \"order_by\": \"a_to_z\",\n    \"with\": ['files'],\n    \"page_index\": 0,\n    \"page_size\": 50\n\n}" %(search_query)

headers = {
    'cache-control': "no-cache",
    'postman-token': "42c89c49-2fbd-5c35-29e8-8b0e9f8bb5fb"
    }

#start = int(time.time() * 1000000) / 1000
response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
#finish = int(time.time() * 1000000) / 1000
response_time = int(response.elapsed.microseconds / 1000)
print "response time:%d ms" %(response_time)
response_time_threshold = 500

try: 
	assert response.status_code == 200
	print "HTTP status:%d" %(response.status_code)


	assert response_time < response_time_threshold, 'response time was:%d ms, should be < threshold:%d ms' %(response_time, response_time_threshold)

	json_response = json.loads(response.text)

	assert json_response['status']['code'] == 0, 'responsebody.status.code was: %d instead of %s' %(json_response['status']['code'], 0)
	assert json_response['total_items'] >= 0, 'responsebody.total_items was: %d, expected >=0' %(json_response['total_items'])

	print "total_items:%d" %(json_response['total_items'])

	assert json_response['assets'] is not None, 'response-body did not contain "assets" key'
except Exception, e:
	error = str(e)
	print "[FAIL] %s" %(error)
	with open('/tmp/searchAssets.error', 'w') as f:
		f.write(error)
	sys.exit(1)