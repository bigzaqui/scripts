import urlparse

fname = "/tmp/solr_log"
with open(fname) as f:
    content_solr = f.readlines()

list_solr = []
list_api = []
list_ratio = []

for i in content_solr:
        parsed = urlparse.urlparse(i)
        value = urlparse.parse_qs(parsed.query)
        time =  float(value['fl'][0][-10:][:-5])
        id_value_orig = value['id_value_orig'][0]
        searchfile = open("/tmp/api_log", "r")
        for line in searchfile:
            if id_value_orig in line:
                api_time = float(line[-10:][:-5])
                ratio = (time*100)/api_time
                list_solr.append(time)
                list_api.append(api_time)
                list_ratio.append(ratio)
                print "API time:" + str(api_time)
                print "SOLR time:" + str(time)
                print "ratio: " +str(ratio) +" %"
                print "#######################"
        searchfile.close()

total_ratio = sum(list_ratio)
average_ratio = total_ratio / len(list_ratio)

print "ratio average: "+ str(average_ratio) + " %"
print "Sample size: "+ str(len(content_solr))


