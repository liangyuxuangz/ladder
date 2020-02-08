from ladder.ladder import Vargroup
from ladder.ladder import LDIpt

if __name__ == '__main__':
    vars = Vargroup(["a", "b", "c", "d", "e", "f", "k", "j", "h"])
    vars["a"] = 0
    vars["b"] = 1
    vars["d"] = 1
    vars["e"] = 1
    vars["c"] = 0
    ld = LDIpt(vars)
    ld.line("--|a|----dp-------s[c]")
    # ld.line("-n|f|-----o--|e|----o         ")
    ld.run()
    vars["a"] = 0
    ld.run()
    vars["a"] = 0
    ld.run()

    ld.printvars()
