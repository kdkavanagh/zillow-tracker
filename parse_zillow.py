import re
import time
import httplib2
import urllib2
import json
epoch = int(time.time())

pricePattern = re.compile('<meta itemprop="price" content="(?P<price>\$\d{1},\d{3},\d{3}|\$\d{3},\d{3}?)">')
statusPattern = re.compile('<span id="listing-icon" data-icon-class="zsg-icon-(?P<status>for-sale|recently-sold|pre-market?)"')
metaPattern=re.compile('<span class="addr_bbs">(.*?)</span>')
addrPattern=re.compile('zillow_fb:address" content="(?P<addr>.*?)"/>')

http = httplib2.Http()


zpidUrl='http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111001&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=14&rect=-87656608,41914301,-87617341,41923179&p=1&sort=globalrelevanceex&search=maplist&disp=1&listright=true&isMapSearch=1&zoom=14'


req = urllib2.Request(zpidUrl)
opener = urllib2.build_opener()
f = opener.open(req)
json = json.loads(f.read())
props= json['map']['properties']

with  open("test.txt", "a") as myfile:
    for zpid in props:
        #Get the html for this zpid
        zpid = zpid[0]#.rstrip('\n')
        print "Getting data for zpid %s" % zpid
        myUrl = "http://www.zillow.com/homedetails/"+str(zpid)+"_zpid/"
        print myUrl
        headers, htmlContent = http.request(myUrl)
        price =0;
        status ="";
        beds=""
        baths=""
        sqft=""
        addr=""
        for match in re.finditer(pricePattern, htmlContent):
            price = match.group('price').replace(',','')
        for match in re.finditer(statusPattern, htmlContent):
            status = match.group('status')
        meta = re.findall(metaPattern, htmlContent)
        beds = meta[0]
        baths = meta[1]
        sqft = meta[2].replace(',','')
        for match in re.finditer(addrPattern, htmlContent):
            addr = match.group('addr').replace(',',' ')

        csv = '%s,%s,%s,%s,%s,%s,%s,%s\n' % (epoch,zpid, addr, price, status, beds, baths, sqft)
        myfile.write(csv)
