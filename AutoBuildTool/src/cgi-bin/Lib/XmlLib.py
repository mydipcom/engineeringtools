#coding:utf8
import pprint

def xml2dict(type, strdict):
    from lxml import etree
    
    def xmltodictunit(node):
        res = {}
        if False:#isinstance(node,lxml.etree._Comment):
            print node
        else:  
            if len(node):
                for n in list(node):
                    if len(n):
                        rep = xmltodictunit(n)
                    else :
                        rep = n.text
                    if isinstance(res.get(n.tag), list):
                        res[n.tag].append({'v':rep, 'a':n.attrib})
                    elif res.get(n.tag) is not None:
                        l = []
                        l.append(res[n.tag])
                        l.append({'v':rep, 'a':n.attrib})
                        res[n.tag] = l
                    else:  
                        res[n.tag] = {'v':rep, 'a':n.attrib}
            else:
                res = {'v':node.text, 'a':node.attrib}
        return res
    
    if type.lower() == 'f':
        node = etree.parse(strdict).getroot()
    elif type.lower() == 's':
        node = etree.fromstring(strdict)
    res = xmltodictunit(node)
    reply = {}
    reply[node.tag] = {'v':res, 'a':node.attrib}
    return reply

def dict2xml(d):
    from xml.sax.saxutils import escape
    
    def unicodify(o):
        if o is None:
            return u'';
        return unicode(o)
    lines = [r'<?xml version="1.0" encoding="UTF-8"?>']
    
    def addDict(node, offset):
        for name, value in node.iteritems():
            if name == "a":
                strqq = lines[len(lines) - 1]
                index = strqq.find(u"<")
                strqq = strqq[index + 1:len(strqq) - 1]
                for x, y in value.iteritems():
                    strqq = strqq + u" " * 1 + u"%s='%s'" % (x, y)
                lines[len(lines) - 1] = u" " * index + u"<%s>" % (strqq)
            else:
                if isinstance(value, dict):
                    lines.append(offset + u"<%s>" % name)
                    addDict(value, offset + u"    " * 1)
                    lines.append(offset + u"</%s>" % name)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            addDict(item, offset + u" " * 1)
                        else:
                            lines.append(offset + u"<%s>%s</%s>" % (name, escape(unicodify(item)), name))
                else:
                    if value != "":
                        pass
    addDict(d, u"")
    lines.append(u"")
    return u"/n".join(lines)      
         
                
if __name__ == '__main__':
    a = """<?xml version="1.0" encoding="gb2312"?>
<Config>
  <NpcModel mname="NPC_Default">
 <ActionList>
  <Action name="openUrl">
   <Param name="url" type="string">
      <test name='1'>1</test>
      <test name='2'/>
   </Param>
   <Param name="size" type="enum" enum="large,small,full"/>
  </Action>
  <Action name="playGame">
   <Param name="id" type="string"/>
  </Action>
 </ActionList>
  </NpcModel>
</Config>
    """
    x = xml2dict("s", a)
    pprint.pprint(x)
    pprint.pprint(str(dict2xml(x)))
    # f.close()
