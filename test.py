from ladder.ladder import Vargroup
from ladder.ladder import MKblock

if __name__ == '__main__':
    vars = Vargroup(["a", "b", "c", "d", "e", "f", "k", "j", "h"])
    vars["a"] = 0
    vars["b"] = 1
    vars["d"] = 1
    vars["e"] = 1
    vars["c"] = 0
    bl=MKblock(vars)

    for i in range(100):
        bl.line("--|a|----dp-------s[c]")
        bl.run()


    bl.printvars()
