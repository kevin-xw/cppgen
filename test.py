#
import sys
import json
from pprint import pprint
import cppgen


defstr = '''
{
    "header" : 
    {
        "precom" : "APSARA_CLASS_GEN_H",
        "include" : ["<string>", "stdio.h"],
        "namespace" : "space1:space2", 
        "file" : "myclass.h"
    },
    "impl" : 
    {
        "file" : "myclass.cpp",
        "include" : ["myclass.h"],
        "using" : ["space1::space2"]
    },
    "class" :
    [
        {
            "child":
            {
                "inherit" : 
                {
                    "base": "father"
                },
                "pub_func":
                [
                    "void func1()",
                    "bool func2(char)",
                    "int func3(string&)"
                ],
                "members":
                {
                    "m_name" : {"type": "string", "init":"andy"},
                    "m_age" : {"type": "int", "init": 9},
                    "m_boy" : {"type": "bool"}
                }
            }
        },
        {
            "child2":
            {
            }
        }
    ]
}
'''        
    
if __name__ == '__main__' :
       
    jdata = json.loads(defstr)
    
    cpp = cppgen.CppGen(jdata)
    cpp.Output()
    '''
    clist = []
    header = cppgen.Header(sys.stdout, jdata)
    header.OutputPrecom(True)
    header.OutputIncludes()
    header.OutputNamespace(True)
    
    classdef = jdata[cppgen.cppclass]
    #pprint(classdef)
    #pprint(jdata)

    for c in classdef : 
        for n, d in c.items() : 
            myclass = cppgen.ClassGen(sys.stdout, n, d)
            myclass.OutputDelaration()
            clist.append(myclass)
            
    header.OutputNamespace(False)
    header.OutputPrecom(False)
             
    print "\n"
    for c in clist :
        c.OutputImpl()
    '''        

