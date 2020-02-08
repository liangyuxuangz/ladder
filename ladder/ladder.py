import re
import types


class LDIpt():
    def __init__(self, vars):
        # 建立梯形图起点节点列表
        self.start_nodelist = []
        # 建立后续的节点字典
        self.nodelist = {}
        # 建立变量字典关联
        self.vars = vars
        # 如果getvarblock=true，就不用分析梯形图，可以一直运行建立好的逻辑程序
        self.getvarblock = 0
        # 自动给节点命名。因为不同节点可以关联同一个变量。这里是初始化。
        self.nodeid = 0
        # 分析梯形图时辅助，标记o点的位置
        self.o_pos = 0
        # 正则表达式。|x|, u|x|, d|x|, n|x|, nu|x|, nd|x|, dp, ndp, o, [y], s[y], r[y]
        self.pattern1 = re.compile(
            r'\|\w+\||[nN]\|\w+\||[dD]\|\w+\||[nN][dD]\|\w+\||[uU]\|\w+\||[nN][uU]\|\w+\||\[\w+\]|[sS]\[\w+\]|[rR]\[\w+\]|-[oO]|[oO]-|[dD][pP]|[nN][dD][pP]')
        # 获取节点功能
        self.pattern2 = re.compile(
            r'\||[nN]\||[dD]\||[nN][dD]\||[uU]\||[nN][uU]\||\[|[sS]\[|[rR]\[|[oO]|[dD][pP]|[nN][dD][pP]')

    def line(self, prglist):
        if self.getvarblock == 0:
            n = Node("start", None)
            n.nodelink = None
            n.type = 0
            n.val = 1
            self.pre_node = n
            self.start_nodelist.append(n)
            self.result = self.pattern1.findall(prglist)
            self.o_pos = 0
            self.nodedefine(prglist)

    def run(self):
        self.cangetvar = 1
        for x in self.start_nodelist:
            if x.nodelink is not None:
                x.nodelink.go(x.val)

    def nodelink(self, source):
        if self.pre_node.type != 10:
            self.pre_node.nodelink = source
            self.pre_node = source
        else:
            self.pre_node.nodelink.append(source)
            self.pre_node = source

    def O_nodelink(self, source):
        if self.pre_node.type == 0:
            self.pre_node = source
        elif self.pre_node.type == 10:
            self.pre_node = source
        else:
            source.nodelinkcnt += 1
            self.pre_node.nodelink = source
            self.pre_node = source

    def makenode(self, varname, type, foo):
        nodename = "n_"+str(self.nodeid)
        n = Node(nodename, self.vars)
        self.nodeid += 1
        n.varlinkname = varname
        n.type = type
        n.go = types.MethodType(foo, n)
        self.nodelink(n)
        self.nodelist[nodename] = n

    def O_makenode(self, nodename, foo):
        n = Node(nodename, None)
        n.type = 10
        n.nodelinkcnt = 0
        n.val = []
        n.nodelink = []
        n.go = types.MethodType(foo, n)
        self.O_nodelink(n)
        self.nodelist[nodename] = n

    def nodedefine(self, prglist):
        # type 0:起始，10：ORS，255：End
        for x in self.result:
            k = len(x)
            re = self.pattern2.findall(x)
            if re[0] == '|':
                varname = x[1:k-1]
                self.makenode(varname, 1, f_AND)
            elif (re[0] == 'n|') or (re[0] == 'N|'):
                varname = x[2:k-1]
                self.makenode(varname, 2, f_NAND)
            elif (re[0] == 'd|') or (re[0] == 'D|'):
                varname = x[2:k-1]
                self.makenode(varname, 3, f_D_DP)
            # elif (re[0] == 'nd|') or (re[0] == 'Nd|') or (re[0] == 'nD|') or (re[0] == 'ND|'):
            #     varname = x[3:k-1]
            #     self.makenode(varname, 4, f_N_D_DP)
            elif (re[0] == 'u|') or (re[0] == 'U|'):
                varname = x[2:k-1]
                self.makenode(varname, 5, f_U_DP)
            # elif (re[0] == 'nu|') or (re[0] == 'Nu|') or (re[0] == 'nU|') or (re[0] == 'NU|'):
            #     varname = x[3:k-1]
            #     self.makenode(varname, 6, f_N_U_DP)
            elif re[0] == '[':
                varname = x[1:k-1]
                self.makenode(varname, 7, f_OUT)
            elif (re[0] == 's[') or (re[0] == 'S['):
                varname = x[2:k-1]
                self.makenode(varname, 3, f_SET)
            elif (re[0] == 'r[') or (re[0] == 'R['):
                varname = x[2:k-1]
                self.makenode(varname, 3, f_RST)
            elif (re[0] == 'o') or (re[0] == 'O'):
                # 寻找“O”的位置。要分别处理“-o”或“o-”两种情况
                poslist = self.searchX(prglist)[0]
                pos_start = poslist[0]
                if prglist[pos_start] == "-":
                    pos_start += 1
                name = "o_"+str(self.o_pos + pos_start)
                self.o_pos = self.o_pos + pos_start + 1

                lst = self.nodelist
                if name in lst:
                    n = lst[name]
                    self.O_nodelink(n)
                else:
                    self.O_makenode(name, f_ORS)
            elif (re[0] == 'dp') or (re[0] == 'dP') or (re[0] == 'Dp') or (re[0] == 'DP'):
                varname = re[0]
                self.makenode(varname, 12, f_DPU)
            elif (re[0] == 'ndp') or (re[0] == 'ndP') or (re[0] == 'nDp') or (re[0] == 'nDP'):
                varname = re[0]
                self.makenode(varname, 13, f_N_DPU)
            elif (re[0] == 'Ndp') or (re[0] == 'NdP') or (re[0] == 'NDp') or (re[0] == 'NDP'):
                varname = re[0]
                self.makenode(varname, 13, f_N_DPU)
            else:
                pass

        self.makenode("End", 255, f_End)

    def searchX(self, prglist):
        tmp = prglist[self.o_pos:]
        searchobj = re.search(r'-[oO]|[oO]-', tmp)
        return searchobj.regs


def f_AND(self, sourceval):
    self.val = sourceval and self.varlink[self.varlinkname]
    self.nodelink.go(self.val)


def f_NAND(self, sourceval):
    self.val = sourceval and self.varlink[self.varlinkname]
    self.nodelink.go(self.val)


def f_ORS(self, sourceval):
    self.nodelinkcnt = self.nodelinkcnt-1
    self.val.append(sourceval)
    if self.nodelinkcnt == 0:
        calval = 0
        for x in self.val:
            calval = calval | x
        for y in self.nodelink:
            y.go(calval)


def f_OUT(self, sourceval):
    self.varlink[self.varlinkname] = sourceval
    self.nodelink.go(sourceval)


def f_SET(self, sourceval):
    if sourceval == 1:
        self.varlink[self.varlinkname] = 1
    self.nodelink.go(sourceval)


def f_RST(self, sourceval):
    if sourceval == 1:
        self.varlink[self.varlinkname] = 0
    self.nodelink.go(sourceval)


def f_End(self, sourceval):
    pass


def f_U_DP(self, sourceval):
    self.val = self.varlink[self.varlinkname] and sourceval
    if (self.preval == 0) and (self.val == 1):
        self.val = 1
        self.preval = 1
        self.nodelink(self.val)
    else:
        self.val = 0
        self.preval = 0
        self.nodelink(self.val)


def f_D_DP(self, sourceval):
    self.val = self.varlink[self.varlinkname] and sourceval
    if (self.preval == 1) and (self.val == 0):
        self.val = 1
        self.preval = 1
        self.nodelink(self.val)
    else:
        self.val = 0
        self.preval = 0
        self.nodelink(self.val)


def f_DPU(self, sourceval):
    self.val = sourceval
    if (self.preval == 0) and (self.val == 1):
        self.val = 1
        self.preval = 1
        self.nodelink(self.val)
    else:
        self.val = 0
        self.preval = 0
        self.nodelink(self.val)


def f_N_DPU(self, sourceval):
    self.val = sourceval
    if (self.preval == 1) and (self.val == 0):
        self.val = 1
        self.preval = 1
        self.nodelink(self.val)
    else:
        self.val = 0
        self.preval = 0
        self.nodelink(self.val)


class Node():
    def __init__(self, name, vars):
        self.name = name
        self.val = 0
        self.type = 0
        self.varlink = vars
        self.varlinkname = None
        self.nodelink = None


def Vargroup(varnamelist):
    var = {}
    for x in varnamelist:
        var[x] = 0
    return var


# if __name__ == '__main__':
#     vars = Vargroup(["a", "b", "c", "d", "e", "f", "k", "j", "h"])
#     vars["a"] = 1
#     vars["b"] = 1
#     vars["d"] = 1
#     vars["e"] = 1
#     ld = LDIpt(vars)
#     ld.line("--|a|--o--|b|----o------[c]")
#     ld.line("       o--|e|----o         ")
#     ld.run()

#     print("Program end")


