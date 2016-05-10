import re
import time
import httplib2
epoch = int(time.time())

pricePattern = re.compile('<meta itemprop="price" content="(?P<price>\$\d{1},\d{3},\d{3}|\$\d{3},\d{3}?)">')
statusPattern = re.compile('<span id="listing-icon" data-icon-class="zsg-icon-(?P<status>for-sale|recently-sold|pre-market?)"')
metaPattern=re.compile('<span class="addr_bbs">(.*?)</span>')
addrPattern=re.compile('zillow_fb:address" content="(?P<addr>.*?)"/>')



http = httplib2.Http()


with open('zpids.in') as f, open("test.txt", "a") as myfile:
    for zpid in f:
        #Get the html for this zpid
        zpid = zpid.rstrip('\n')
        print "Getting data for zpid %s" % zpid
        myUrl = "http://www.zillow.com/homedetails/"+zpid+"_zpid/"
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
