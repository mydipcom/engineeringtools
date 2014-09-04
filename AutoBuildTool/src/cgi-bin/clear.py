#coding:gbk
'''
Created on 2014-6-16

@author: Alvin
'''
import os, sys
import cgi, cgitb 
#import pymssql
import pyodbc

def printPage():
    os.chdir(os.path.dirname(sys.argv[0]))
    print 'Content-Type: text/html\n\n'
    print "<body>"
    print """
    <script language="javascript">
    function show(){
        var msg=document.getElementById("msg");
        var submit=document.getElementById("submit");
        msg.style.display='block';
        submit.style.display='none';
    }
    </script>
    """
    print '<h1 align="center">Clear Session - Elibrary</h1><hr>'
    print r'<center><form name="form1" action="/cgi-bin/%s" method="Post" target="_self">' % os.path.split(__file__)[1]
    print '<br><b>Email:</b><input type="text" name="email" / >'
    print '''<h2><input id="submit" type="submit" value="      Start      " onclick="show()"/></h2>'''
    print '<dev id="msg" style="display:none;color:red"><h3>处理中，请等待...</h3></dev>'
    print '</form></center><hr>'
    
def dbOperation(email):
    Servername = "CR-Server1\SQLEXPRESS"
    Username = "elibrary"
    Password = "elibrary"
    DBname = "elibrary"
    try:
#        conn = pymssql.connect(host=Host,user=Username,password=Password,database=DBname)
#        cursor = conn.cursor()
        cs = r"Driver={SQL Server};Server=tcp:%s;Database=%s;Uid=%s;Pwd=%s;Encrypt=No;" % (Servername, DBname, Username, Password)
        conn = pyodbc.connect(cs)
        cursor = conn.cursor()
        sql = "DELETE LoginRecord where Customer_Id In (SELECT id FROM Customer WHERE Email like '%" + email.strip() + "%')"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        print '<center><h2 style="color:green">清理结束</h2></center><br>'
    except Exception, e:
        print '<center><h2 style="color:red">清理失败</h2></center><br>'
        print "[except]:", e

if __name__ == '__main__':
    printPage()
    form = cgi.FieldStorage()
    if form.has_key("email") and form["email"].value != "":   
        email = form["email"].value
        dbOperation(email)
