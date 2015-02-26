# coding=GB2312
'''
Created on 2014-5-4

@author: Alvin
'''
import cgi, cgitb 
import commands
from subprocess import PIPE
import subprocess
import sys, os, shutil
import time

from Lib import XmlLib


htmlContent = """
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-cn">
<head></head>
<body>
    <center><h1>Build Information</h1></center><hr><br>
    <h2>Build Number:</h2><h3 style="color:blue">&nbsp;&nbsp;&nbsp;&nbsp;%(num)s</h3><br><br>
    <h2>Build Time:</h2><h3 style="color:blue">&nbsp;&nbsp;&nbsp;&nbsp;%(time)s</h3>
</body>
"""

class autoBuild():
    def __init__(self, configfile):
        config = XmlLib.xml2dict("f", configfile)
        self.username = config['root']['v']['setting']['v']['username']['v']
        self.password = config['root']['v']['setting']['v']['password']['v']
        self.rootpath = config['root']['v']['setting']['v']['rootpath']['v']
        self.prolist = config['root']['v']['prolist']['v']['project']
         
    def mainDo(self, proname):
        print "<br><br><h3>%s</h3>" % (('< %s >' % proname).center(50, "="))
        result = True
                     
        def copyDir(source,target):
            target = os.path.join(target,"")
            cmd = 'xcopy "%s" "%s" /O /X /E /H /K'%(source,target)
            return executeCmd(cmd)
        
        def removeDir(source):
            cmd = 'rd /q /s "%s"'%source
            return executeCmd(cmd)
            
        def executeCmd(cmd,printOut=False):
            try:
                print "<br>执行命令：%s" % cmd
                print ""
                sp = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                output, unused_err = sp.communicate()
                if printOut:
                    print output
                sp.wait()
                print ""
                if sp.returncode > 0:
                    print '<br><strong style="color:red">结果：< 执行失败 ></strong><br>'
                    print "<br>错误信息：", unused_err, ""
                    return False
                else:
                    print '<br><strong style="color:green">结果：< 执行成功 ></strong><br>'
                    return True
            except Exception, e:
                print "<br>**%s<br>%s" % ('异常信息：'.center(40, "*"), e)
                return False
            
        # git操作函数
        def doGit(type, url, path):
            if type == "clone":
                print "<br>仓库不存在，进行克隆！"
                cmd = "git clone %s %s" % (url, path)
            elif type == "pull":
                print "<br>仓库存在，进行更新！"
                os.chdir(url)
                cmd = "git pull"
            elif type == "push":
                print "<br>推送本地修改（版本信息）"
                os.chdir(url)
                cmd = 'git add "%s"&git commit -m "AutoBuild:buildinfo change"&git push origin master' % path
            return executeCmd(cmd,True)
            
        # 构建函数    
        def doMsBuild(slnpath, csprojpath, websitepath, logpath):
            os.chdir(os.path.dirname(sys.argv[0]))
            nuget = "./Tool/NuGet.exe"
            if os.path.isfile(logpath):
                os.remove(logpath)
            cmd = os.path.abspath(nuget) + " restore " + slnpath + ' >>"%s" &' % logpath + '''msbuild "%s" /t:ResolveReferences;Compile /t:_WPPCopyWebApplication /p:Configuration=Release /p:_ResolveReferenceDependencies=true /p:WebProjectOutputDir="%s" >>"%s"''' % (csprojpath, websitepath, logpath)
            result = executeCmd(cmd)
            if os.path.isfile(logpath):
                print "<br><strong><a href='%s'>查看构建日志</a></strong>" % ("./Log/" + os.path.split(logpath)[1])
            return result
            
        def doMavenBuild(websitepath, logpath):
            os.chdir(propath)
            print os.getcwd()
            if os.path.isfile(logpath):
                os.remove(logpath)
            cmd = "mvn clean package" + ' >> "%s"'% logpath
            result = executeCmd(cmd)
            if os.path.isfile(logpath):
                print "<br><strong><a href='%s'>查看构建日志</a></strong>" % ("./Log/" + os.path.split(logpath)[1])
            if result:
                sourcefile = os.path.join(os.getcwd(),"target")+"\\mpos.war"
                targetfile = websitepath+"\\mpos.war"
                cmd = 'copy /y "%s" "%s"' % (sourcefile, targetfile)
                result = executeCmd(cmd)
            return result
            
        try:
            for pro in self.prolist:
                if proname.lower() in pro['a']['name'] and pro['a']['enable'] == 'true':
                    pullResult = False
                    os.chdir(os.path.dirname(sys.argv[0]))
                    proname = pro['a']['name']
                    mode = pro['a']['mode']
                    schema = pro['a']['schema']
                    homepath = os.path.join(self.rootpath, pro['v']['homepath']['v'])
                    propath = os.path.join(self.rootpath, pro['v']['propath']['v'])
                    logpath = os.path.abspath("./Log/" + proname + '.txt')
                    if not os.path.isdir(homepath):
                        pullResult = doGit('clone', pro['v']['giturl']['v'], homepath)
                    else:
                        if not os.path.isdir(propath):
                            print "<br>[异常]仓库存在，但项目不存在！请检查配置文件或本地文件目录！"
                            pullResult = False
                            break
                        pullResult = doGit('pull', homepath, None)
                        #pullResult = True  # 同步结果
                    if pullResult == True:
                        print"<br>----------"
                        buildResult = False
                        backupdirs = pro['v']['backupdir']['v']
                        backupdirList = backupdirs.split(";") if backupdirs != None else None
                        websitepath = pro.get('v').get('websitepath').get('v')
                        #备份目录
                        if not backupdirs == None:
                            os.chdir(os.path.dirname(sys.argv[0]))
                            for backupdir in backupdirList:
                                backupabsdir = os.path.join(websitepath, backupdir)
                                tempabsdir = os.path.abspath(os.path.join("./Temp", proname, backupdir))
                                print "<br><strong>备份目录</strong>%s" % backupabsdir
                                if os.path.isdir(backupabsdir):
                                    if os.path.isdir(tempabsdir):
                                        removeDir(tempabsdir)
                                    copyresult = copyDir(backupabsdir, tempabsdir)
                                    if not copyresult:
                                        return
                                else:
                                    print '<br><strong style="color:red">结果：< 备份失败 > 请检查目录是否正确！</strong><br>'
                                    return
                        #构建C#项目
                        if schema == "c#":
                            slnpath = pro.get('v').get('slnpath').get('v')
                            csprojpath = pro.get('v').get('csprojpath').get('v')
                            
                            if csprojpath == None or websitepath == None:
                                print "<br>未配置,不进行构建"
                                break
                            
                            print"<br>----------" 
                            print "<br><strong>开始构建</strong>"
                            print ""
                            buildResult = doMsBuild(os.path.join(propath, slnpath), os.path.join(propath, csprojpath), websitepath, logpath)
                        elif schema =="java":
                            if websitepath == None:
                                print "<br>未配置,不进行构建"
                                break
                            buildResult = doMavenBuild(websitepath,logpath)
                        #buildResult = True  # 构建结果
                        print ""
                        if buildResult == True:
                            #还原目录
                            if not backupdirs == None:
                                print"<br>----------"
                                for backupdir in backupdirList:
                                    backupabsdir = os.path.join(websitepath, backupdir)
                                    tempabsdir = os.path.abspath(os.path.join("./Temp", proname, backupdir))
                                    if  os.path.isdir(tempabsdir):
                                        if os.path.isdir(backupabsdir):
                                            removeDir(backupabsdir)
                                            time.sleep(1)
                                        print "<br><strong>还原目录</strong>%s" % backupabsdir
                                        copyDir(tempabsdir, backupabsdir)
                                    else:
                                        print '<br><strong style="color:red">结果：< 还原失败 >备份不存在！</strong><br>' 
                                    
                            dbfile = pro['v'].get('dbfile')
                            if not dbfile is None:
                                sourcefile = os.path.abspath(os.path.join(r".\DBfile", dbfile['v']['source']['v']))
                                targetfile = os.path.join(websitepath, dbfile['v']['target']['v'])
                                print"<br>----------"
                                print "<br><strong>替换数据库文件</strong>"
                                cmd = 'copy /y "%s" "%s"' % (sourcefile, targetfile)
                                executeCmd(cmd)
                            print"<br>----------"
                            print "<br><strong>版本信息</strong>"
                            pushResult = False;
                            if mode == 'dev':
                                buildInfoFilePath = os.path.join(propath, 'BuildInfo.txt')
                                if os.path.isfile(buildInfoFilePath):
                                    with open(buildInfoFilePath, "r") as buildInfoFile:
                                        lines = buildInfoFile.readlines()
                                    #numTemp = lines[0].strip().split(".")
                                    #numTemp[-1] = str(eval(numTemp[-1]) + 1)
                                    #buildNum = '.'.join(numTemp)
                                    buildNum = "N/A"
                                    localTime = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(time.time()))
                                    print '<br><strong style="color:green">构建后版本：%s</strong><br>' % buildNum
                                    print '<br><strong style="color:green">构建完时间：%s</strong><br>' % localTime
                                    #infoText = buildNum + "\n" + localTime
                                    infoText = localTime;
                                    with open(buildInfoFilePath, "w") as buildInfoFile:
                                        buildInfoFile.write(infoText)
                                    #pushResult = doGit('push', homepath, buildInfoFilePath)
                                    pushResult = True
                            else:
                                buildInfoFilePath = os.path.join(propath, 'BuildInfo.txt')
                                if os.path.isfile(buildInfoFilePath):
                                    with open(buildInfoFilePath, "r") as buildInfoFile:
                                        lines = buildInfoFile.readlines()
                                    buildNum = lines[0]
                                    localTime = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(time.time()))
                                    print '<br><strong style="color:green">当前版本：%s</strong><br>' % buildNum
                                    print '<br><strong style="color:green">发布时间：%s</strong><br>' % localTime
                                    pushResult = True
                            if pushResult == True:
                                htmlFilePath = os.path.join(websitepath, 'BuildInfo.html')
                                with open(htmlFilePath, "w") as htmlFile:
                                    htmlFile.write(htmlContent % {'num':buildNum, 'time':localTime})
                                print "<br>生成文件:BuildInfo.html"
                    print "<br><strong>任务结束</strong>"
        except Exception, e:
            print "<br>%s<br>" % ('异常信息'.center(40, "*"))
            print e
        print "<br><h3>", "".center(50, "="), "</h3>"

if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    ab = autoBuild(os.path.abspath(r"./ProList.xml"))
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
    print '<h1 align="center">One Click Build & Deploy</h1><hr>'
    print r'<center><form name="form1" action="/cgi-bin/%s" method="Post" target="_self">' % os.path.split(__file__)[1]
    for pro in ab.prolist:
        if pro['a']['enable'] == 'true':
            print r'<h2><input type="checkbox" name="%s" value="on" /> %s </input></h2>' % (pro['a']['name'], pro['a']['name'].center(15).replace(" ", "&nbsp"))
    print '''<h2><input id="submit" type="submit" value="      Start      " onclick="show()"/></h2>'''
    print '<dev id="msg" style="display:none;color:red"><h3>处理中，请等待...</h3></dev>'
    print '</form></center><hr>'
    form = cgi.FieldStorage()
    for name in form.keys():
        ab.mainDo(name)
    print "</body>"
#    ab.mainDo("e-library")
