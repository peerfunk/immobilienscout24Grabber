import json, requests, pprint,re
import csv
import gmplot
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.64 Safari/537.36")


class ImmoGetter:
    __currentPage=0
    __currentItem=0
    __maxPages=0
    __hits=0
    __localizationGeoHierarchy = "003004,003007,003017,003018,003019,003021,003023,003024"
    __typeUseType = "RESIDENTIAL"
    __priceInformationPrimaryPriceTo = "500000"
    __typeEstateType = "PROPERTY"
    __typeTransferType = "BUY"
    __spot = 'Nieder"%"C3"%"B6sterreich'
    __region = "003"
    __mapFile = ""
    lats=[]
    lons=[]
    #latLons = golden_gate_park_lats, golden_gate_park_lons = zip(*[])
    def getNextPage(self):
        if(self.__currentItem > self.__hits):
            return None
        url = "https://www.immobilienscout24.at/api/psa/is24/properties/search?areaPrimaryAreaFrom=1000&from=" + str(self.__currentItem) + "&localizationGeoHierarchy=" + str(self.__localizationGeoHierarchy) + "&matchSubProperties=true&priceInformationPrimaryPriceTo=" + self.__priceInformationPrimaryPriceTo + "&size=25&sort=PRICE_ASC&typeEstateType=" + self.__typeEstateType+"&typeTransferType=" +self.__typeTransferType +"&typeUseType=" + self.__typeUseType
        headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.64 Safari/537.36',
                   'Accept' : 'application/json, text/plain, */*',
                   'Accept-Language' : 'en-US,en;q=0.5',
                   'Referer' : 'https://www.immobilienscout24.at/resultlist?spot=' + self.__spot + '&region=' + self.__region + '&regions='+self.__localizationGeoHierarchy+'&useType='+self.__typeUseType+'&transferType='+self.__typeTransferType+'&estateType=PROPERTY&price=500000&priceSqmFlg=0&totalArea=1000&sort=PRICE_ASC&page=' + str(self.__currentPage) +'&matchSubProperties=true',
                   'Client-Key' : 'is24-platform',
                   'DNT' : '1',
                   'Connection': 'keep-alive',
                   'Cookie' : 'immobilienscout24_persist=35342602.20480.0000; viewedOuibounceModal=true'
                  }
        r =requests.get(url, headers=headers)
        binary = r.content
        ret = json.loads(binary)
        self.__maxPages = ret['numberOfPages']
        self.__hits = ret['totalHits']
        ret['url']= url
        ret['Referer']= headers['Referer']
        output = {}
        output["currentPage"] = self.__currentPage
        output["hits"] = self.__hits
        output["maxPages"] = self.__maxPages
        output["currentItem"] = self.__currentItem
        output = json.dumps(output)
        print(output)
        self.__currentItem +=25
        self.__currentPage +=1
        return ret
    def __init__(self,filename,localizationGeoHierarchy,spot, priceInformationPrimaryPriceTo, typeEstateType, typeTransferType,typeUseType):
        self.__localizationGeoHierarchy=localizationGeoHierarchy
        self.__typeUseType = typeUseType
        self.__priceInformationPrimaryPriceTo = priceInformationPrimaryPriceTo
        self.__spot = spot
        self.__typeEstateType = typeEstateType
        self.__typeTransferType = typeTransferType
        self.getToFile(filename)
    def __init__(self, filename):
        self.getToFile(filename)
    def __init__(self, filename,mapFile):
        self.__mapFile = mapFile
        self.getToFile(filename)
        self.plot()
    def getToFile(self,filename):
        counter = 0
        with open(filename, 'w' , newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')
            spamwriter.writerow(["id", "title", "totalArea", "primaryPrice", "zip", "ciy", "url", "referer", "hit"])
            page = self.getNextPage()
            hits = page['hits']
            url = page['url']
            referer = page['Referer']
            while(page != None):
                hits = page['hits']
                url = page['url']
                referer = page['Referer']
                for hit in hits:
                    address = hit['localization']['address']
                    if(self.__mapFile != ""):
                        location = geolocator.geocode(address['zip'] + " " + address['city'] + " Austria" )
                        if (location != None):
                            self.lats.append(location.latitude)
                            self.lons.append(location.longitude)
                        else:
                            print(address['zip'] + " " + address['city'] + " Austria" )    
                    spamwriter.writerow([counter]+[hit['description']['title'],hit['area']['totalArea'],hit['priceInformation']['primaryPrice'],address['zip'],address['city'],url,referer,hit])
                    counter +=1
                page = self.getNextPage()
    def plot(self):
        print(self.lats)
        print(self.lons)
        gmap = gmplot.GoogleMapPlotter(48.014589, 15.889625, 9)
        gmap.scatter(self.lats, self.lons, '#FF0000', size=500, marker=False)
        gmap.draw(self.__mapFile)



        
x = ImmoGetter("out.csv", "map.html")                
         
       
    
    
