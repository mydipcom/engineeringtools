import cgi, cgitb ,re


page = r'C:\Website Group\campray\bug.html'
content = """
<html>
<head>
<meta http-equiv="refresh" content="0; url=http://%s" />
</head>
<body>
</body>
</html>
"""

if __name__ == '__main__':
    print 'Content-Type: text/html\n\n'
    try:
        form = cgi.FieldStorage()
        if form.has_key("address") and form["address"].value != "":   
            address = form["address"].value
            express = r"(\d+\.\d+\.\d+\.\d+):(.+)"
            mo = re.search(express ,address)
            if mo:
                file = open(page,"w")
                file.write(content%address)
                file.close()
                print "succeed!"   
            else:
                print 'failed!'
    except:
        print "exception!"