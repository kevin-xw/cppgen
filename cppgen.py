
import sys
import json

class cppgen : 
# type of keyword used in config json
    header = 'header'
    header_prcom = 'precom'
    header_include = 'include'
    header_namespace = 'namespace'
    header_file = 'file'
    cppclass = 'class'
    cppclass_inherit = 'inherit'
    cppclass_inherit_base = 'base'
    cppclass_inherit_type = 'type'
    cppclass_member = 'members'
    cppclass_member_type = 'type'
    cppclass_member_init = 'init'
    cppclass_pubfunc = 'pub_func'
    impl = 'impl'
    impl_include = 'include'
    impl_file = 'file'
    impl_using = 'using'
    
# std containers 
    std_containers = ['string', 'vector', 'list', 'set', 'map', 'deque']
# number type 
    num_type = ['int', 'int32_t', 'int64_t', 'uint32_t', 'uint64_t', 'long', 'size_t']

class Header : 
    def __init__(self, out, header_json) :
        self._out = out
        self._init(header_json)
        
    def _init(self, config_json) :
        self._precom = config_json.get(cppgen.header_prcom) 
        self._includes = config_json.get(cppgen.header_include)
        self._namespace = config_json.get(cppgen.header_namespace)
            
    def OutputPrecom(self, begin) :
        if self._precom : 
            if begin == True :
                self._out.write("#ifndef %s\n#define %s\n\n" % (self._precom, self._precom))
            else : 
                self._out.write("#endif\n")
            
    def OutputNamespace(self, begin) : 
        if self._namespace :
            if begin == True :
                for n in self._namespace.split(":") :
                    self._out.write("namespace %s\n{\n" % n)
                self._out.write("\n")
            else :
                np = self._namespace.split(":")
                np.reverse()
                for n in np :
                    self._out.write("} //namespace %s\n" % n)
                self._out.write("\n")
                
    def OutputIncludes(self) :
        if self._includes :
            for i in self._includes :
                if i[1] != '<' and i[-1] != '>' :
                    self._out.write("#include \"%s\"\n" % i)
                else :
                    self._out.write("#include %s\n" % i)
            self._out.write("\n")

    def OutputPrecomEnd(self) :
        self._out.write("#endif\n")

class Impl : 
    def __init__(self, out, impl_json) :
        self._out = out
        self._init(impl_json)
        
    def _init(self, config_json) : 
        self._includes = config_json.get(cppgen.impl_include)
        self._using = config_json.get(cppgen.impl_using)
        
    def Output(self) : 
        if self._includes :
            for i in self._includes :
                if i[1] != '<' and i[-1] != '>' :
                    self._out.write("#include \"%s\"\n" % i)
                else :
                    self._out.write("#include %s\n" % i)
        self._out.write("\n")
        if self._using :
            for u in self._using : 
                self._out.write("using %s\n" % u)
        self._out.write("\n")
        
class ClassGen :
    def __init__(self, name, jsonstr) : 
        self._name = name
        self._jsonstr = jsonstr

    def Name(self) : 
        return self._name
    def Base(self) :
        if cppgen.cppclass_inherit in self._jsonstr and cppgen.cppclass_inherit_base in self._jsonstr[cppgen.cppclass_inherit]:
            return self._jsonstr[cppgen.cppclass_inherit][cppgen.cppclass_inherit_base]
        return ''
        
    def PubFuncs(self) :  
        if cppgen.cppclass_pubfunc in self._jsonstr :
            return self._jsonstr[cppgen.cppclass_pubfunc]
        return []
        
    def Members(self) :
        if cppgen.cppclass_member in self._jsonstr : 
            return self._jsonstr[cppgen.cppclass_member]
        return ''
    
    def _hasInherit(self) :
        if cppgen.cppclass_inherit in self._jsonstr :
            return True
        return False
                
    def _inheritType(self) :
        if cppgen.cppclass_inherit in self._jsonstr and cppgen.cppclass_inherit_type in self._jsonstr[cppgen.cppclass_inherit] : 
            return self._jsonstr[cppgen.cppclass_inherit][cppgen.cppclass_inherit_type]
        else :
            return "public"
                        
    def _constructMembers(self) :
        str = ''
        if len(self.Members()) > 0 :
            for m, s in self.Members().items() : 
                if cppgen.cppclass_member_init in s :
                    if 'type' in s and s[cppgen.cppclass_member_type] == 'string' : 
                        str += "%s(\"%s\"), " % (m, s[cppgen.cppclass_member_type]) 
                    else : 
                        str += "%s(%s), " % (m, s[cppgen.cppclass_member_init]) 
        return str[:-2]
    
    def _addStdNamespace(self, s) :
        for c in cppgen.std_containers :
            s = s.replace(c, ("std::" + c))
        return s
        
    def _defineMembers(self) :
        mlist = []
        if self.Members() : 
            for k, v in self.Members().items() : 
                mlist.append("%s\t%s" % (self._addStdNamespace(v[cppgen.cppclass_member_type]), k))
        return mlist
    
    def _formatFunc(self, func) :
        f = func.replace(' ', (" %s::" % self._name), 1)
        f += "\n{\n";
        returntype = func[: func.find(' ')]
        if returntype in cppgen.num_type :
            f += "\treturn 0;\n"
        elif returntype == 'string' :
            f += "\treturn \"\";\n"
        elif returntype == 'bool' :
            f +="\treturn false;\n"
        f += "}\n"
        return f
        
    def OutputDelaration(self, out) : 
        if self._hasInherit() :
            out.write("class %s : %s %s\n{\n" % (self._name, self._inheritType(), self.Base()))
        else : 
            out.write("class %s\n{\n" % self._name)
        out.write("pubic:\n")
        # constructor
        out.write("\t%s();\n" % self._name)
        out.write("\t~%s();\n" % self._name)
        # pubilc functions
        out.write("\n")
        if self.PubFuncs() :
            for f in self.PubFuncs() : 
                out.write("\t%s;\n" % self._addStdNamespace(f))
        
        # define Members
        out.write("\n")
        mlist = self._defineMembers()
        if len(mlist) > 0 :
            out.write("private:\n")
            for m in mlist :
                out.write("\t%s;\n" % m)
        
        # all done    
        out.write("};\n")
        
    def OutputImpl(self, out) : 
        # constructor
        out.write("%s::%s()" % (self._name, self._name))
        str = self._constructMembers()
        if len(str) != 0 :
            out.write(" : %s \n{\n}\n" % str)
        else :
            out.write("\n{\n}\n")
        # destructor
        out.write("~%s::%s()\n{\n}\n" % (self._name, self._name))
        # fuctions 
        for f in self.PubFuncs() :
            out.write("%s\n" % self._formatFunc(f))


class CppGen :    
    def __init__(self, desc_json): 
        self._desc_json = desc_json
        
    def SetHeader(self, fd) :
        self._headerfd = fd
    def SetImpl(self, fd) : 
        self._implfd = fd;
        
    def Output(self) : 
        hfd = sys.stdout
        if cppgen.header in self._desc_json and cppgen.header_file in self._desc_json[cppgen.header]: 
            hfd = open(self._desc_json[cppgen.header][cppgen.header_file], 'w')
        clist = []
        header = Header(hfd, self._desc_json[cppgen.header])
        header.OutputPrecom(True)
        header.OutputIncludes()
        header.OutputNamespace(True)
        
        classdef = self._desc_json[cppgen.cppclass]
    
        for c in classdef : 
            for n, d in c.items() : 
                myclass = ClassGen(n, d)
                myclass.OutputDelaration(hfd)
                clist.append(myclass)
                
        header.OutputNamespace(False)
        header.OutputPrecom(False)
        
        ifd = sys.stdout
        impl = None
        if cppgen.impl in self._desc_json and cppgen.impl_file in self._desc_json[cppgen.impl] : 
            ifd = open(self._desc_json[cppgen.impl][cppgen.impl_file], 'w')
            impl = Impl(ifd, self._desc_json[cppgen.impl])
        #print "\n"
        if impl : 
            impl.Output() 
        for c in clist :
            c.OutputImpl(ifd)
        
        hfd.close()
        ifd.close()