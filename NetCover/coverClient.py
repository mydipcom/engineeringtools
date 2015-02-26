import re, urllib2
import time
import urllib
import urllib2


class Getmyip:
    def getip(self):
        try:
            myip = self.visit("http://ip.cn/")
        except:
            try:
                myip = self.visit("http://www.bliao.com/ip.phtml")
            except:
                try:
                    myip = self.visit("http://www.whereismyip.com/")
                except:
                    myip = "So sorry!!!"
        return myip
    def visit(self, url):
        opener = urllib2.urlopen(url)
        if url == opener.geturl():
            str = opener.read()
        return re.search('\d+\.\d+\.\d+\.\d+', str).group(0)
    
def postFrom(ip):
    try:
		url = 'http://180.235.135.189:8000/cgi-bin/netcover.py'    
		values = {'address':ip+":8090"}
		data = urllib.urlencode(values)
		print data
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req,timeout=20)
		the_page = response.read()
		print the_page
    except:
		print "Request error!"
	
if __name__ == '__main__':
    while True:
        print "="*30
        print time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(time.time()))
        try:
            localip = Getmyip().getip()
            postFrom(localip)
        except Exception,e:
            print e
        print "sleep 60*10 s!"
        print "-"*30   
        time.sleep(60*10) 
