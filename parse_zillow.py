import re
import time
import httplib2
import urllib2
import json
import sys
import os.path
epoch = int(time.time())

if len(sys.argv) < 2:
    print "An output file is required"
    exit(1)

dataFile = sys.argv[1]
if not os.path.isfile(dataFile):
     with open(dataFile, "a+") as outFile:
         outFile.write('epoch,zpid,addr,zipCode,price,status,beds,baths,sqft\n')

http = httplib2.Http()
props=None

if len(sys.argv) ==3 :
    print "Reading zpids from %s"%sys.argv[2]
    props = [int(line.rstrip('\n')) for line in open(sys.argv[2])]
else:
    minPrice='300000'
    maxPrice='550000'
    baths='1.5'

    #zpidUrl='http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111001&pr=300000,550000&mp=1065,1953&bd=2%2C&ba=1.5%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=12&rect=-87728577,41898507,-87571507,41960830&p=1&sort=globalrelevanceex&search=maplist&disp=1&listright=true&isMapSearch=1&zoom=12'
    zpidUrl='http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111001&pr='+minPrice+','+maxPrice+'&mp=1064,1951&bd=2%2C&ba='+baths+'%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=13&rect=-87689267,41923642,-87610732,41936030&p=1&sort=globalrelevanceex&search=maplist&disp=1&listright=true&isMapSearch=1&zoom=13'
    req = urllib2.Request(zpidUrl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    jsonR = json.loads(f.read())
    props= [e[0] for e in jsonR['map']['properties']]


pricePattern = re.compile('<meta itemprop="price" content="(?P<price>\$\d{1},\d{3},\d{3}|\$\d{3},\d{3}?)">')
soldPricePattern = re.compile('Sold: <span class="">(?P<price>\$\d{1},\d{3},\d{3}|\$\d{3},\d{3}?)')
statusPattern = re.compile('<span id="listing-icon" data-icon-class="zsg-icon-(?P<status>for-sale|recently-sold|pre-market?)"')
metaPattern=re.compile('<span class="addr_bbs">(.*?)</span>')
addrPattern=re.compile('zillow_fb:address" content="(?P<addr>.*?)"/>')
zipPattern = re.compile('"zip":"(?P<zip>\d+)",')


with  open(dataFile, "a+") as myfile, open("zpids.txt", "a+") as zpidsFile:
    for zpid in props:
        #Get the html for this zpid
        print "Getting data for zpid %s" % zpid
        myUrl = "http://www.zillow.com/homedetails/"+str(zpid)+"_zpid/"
        print myUrl
        headers, htmlContent = http.request(myUrl)
        if headers['content-location']=="http://www.zillow.com/homes/":
            #We got redirected
            print "Failure for zpid %s" % zpid
            continue

        price =0;
        status ="";
        beds=""
        baths=""
        sqft=""
        addr=""
        zipCode=0

        for match in re.finditer(statusPattern, htmlContent):
            status = match.group('status')
        if status=="recently-sold":
            for match in re.finditer(soldPricePattern, htmlContent):
                price = match.group('price').replace(',','')
        else:
            for match in re.finditer(pricePattern, htmlContent):
                price = match.group('price').replace(',','')

        meta = re.findall(metaPattern, htmlContent)
        beds = meta[0]
        baths = meta[1]
        sqft = meta[2].replace(',','')
        for match in re.finditer(addrPattern, htmlContent):
            addr = match.group('addr').replace(',',' ')
        for match in re.finditer(zipPattern, htmlContent):
            zipCode=match.group('zip')

        csv = '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (epoch,zpid, addr,zipCode, price, status, beds, baths, sqft)
        myfile.write(csv)
        zpidsFile.seek(0)
        if str(zpid)+"\n" not in zpidsFile:
            # Write it; assumes file ends in "\n" already
            print "Discovered new zpid %s" % zpid
            zpidsFile.write(str(zpid)+"\n")
