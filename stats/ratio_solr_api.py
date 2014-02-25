import urlparse

api_review_log = "/tmp/api_review_log"
api_product_log = "/tmp/api_product_log"
solr_product_log = "/tmp/solr_product_log"
solr_review_log = "/tmp/solr_review_log"

with open(solr_review_log) as f:
    content_solr = f.readlines()


list_solr = []
list_api = []
list_api_product = []
list_solr_product = []
list_ratio = []

for i in content_solr:
	parsed = urlparse.urlparse(i)
	value = urlparse.parse_qs(parsed.query)
	solr_review_time =  float(value['fl'][0][-10:][:-5])
	id_value_orig = value['id_value_orig'][0]
	searchfile = open(api_review_log, "r")
	found = False
	for line in searchfile:
	    if id_value_orig in line: 
		found = True
		api_review_time = float(line[-10:][:-5])
		ratio = (solr_review_time*100)/api_review_time
		list_solr.append(solr_review_time)
		list_api.append(api_review_time)
		list_ratio.append(ratio)

		api_product_time = 0.0
		solr_product_time = 0.0

		#proceed with the api product calls
		searchfile_product = open(api_product_log, "r")
	        for line_product in searchfile_product:
	            if id_value_orig in line_product:
			api_product_time =  float(line_product[-10:][:-5])


		#proceed with the solr product calls
		searchfile_product = open(solr_product_log, "r")
	        for line_product in searchfile_product:
	            if id_value_orig in line_product:
			solr_product_time =  float(line_product[-10:][:-5])
		list_api_product.append(api_product_time)
		list_solr_product.append(solr_product_time)

		print "ID_value_orig: " + id_value_orig
		print "API product call time:" + str(api_product_time)
		print "SOLR product call time:" + str(solr_product_time)
		print "API review call time:" + str(api_review_time)
		print "SOLR review call time:" + str(solr_review_time)
		print "ratio: " +str(ratio) +" %"
		print "#######################"
	if not found:
		print "Warning: " + id_value_orig + " was not found!"
	searchfile.close()


total_ratio = sum(list_ratio)
average_ratio = total_ratio / len(list_ratio)

api_product_call_avg = sum(list_api_product)/len(list_api_product)
print "ratio REVIEW average: "+ str(average_ratio) + " %"
print "REVIEW product call average: "+ str(api_product_call_avg) + " sec"
print "Sample size: "+ str(len(content_solr))

