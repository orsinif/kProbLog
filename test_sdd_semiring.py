from kproblog.semirings.sdd_semiring import ProbabilisticSDDSemiring

def main():
    sdd_mgr = ProbabilisticSDDSemiring()
    evaluate = sdd_mgr.get_evaluate_metafunction()
    _, a = sdd_mgr.parse("a", 0.5)
    _, b = sdd_mgr.parse("b", 0.6)

    c = sdd_mgr.plus(a, b)
    d = sdd_mgr.times(a, b)

    print "w(a or b) = ", sdd_mgr.value(c)
    print "w(a and b) = ", sdd_mgr.value(d)

if __name__ == '__main__':
    main()