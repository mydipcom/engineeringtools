import cgi, cgitb ,re


htmlfile = r'C:\Website Group\campray\%s.html'

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
        for name in form.keys():
            if name in ['bug','uswop','sponsor1']:
                value = form[name].value
                express = r"(\d+\.\d+\.\d+\.\d+):(.+)"
                mo = re.search(express ,value)
                if mo:
                    file = open(htmlfile%name,"w")
                    file.write(content%value)
                    file.close()
                    print name+":succeed!"   
                else:
                    print name+':failed!'
    except:
        print "exception!"