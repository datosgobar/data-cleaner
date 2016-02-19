#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import pandas as pd

from fingerprint_keyer import FingerprintKeyer, GroupFingerprintStrings
from fingerprint_keyer import GetBestReplacements, ReplaceByKey

testStrings = [
    u" - juan     peRes",
    u"Juan ; Perés",
    u"Juan -- Peres",
    u"Juan Per\tes",
    u"juán Peres",
    u"Juan Peres",
    u"Juan Peres",
    u"   Juan\t \tPeres",
]


def demo1():
    print "=" * 80
    print "Demo 1"
    print "=" * 80

    testStrings = [
        ("schön", "schon"),
        #("Ære Øre Åre", "are aere ore"),
        #("Straße","strasse"),
        ("\tABC \t DEF ", "abc def"),  # test leading and trailing whitespace
        ("bbb\taaa", "aaa bbb"),
        ("müller", "muller"),
        #("müller","mueller"), # another possible interpretation
        #("ﬁﬂĳ","fiflij"),
        #("ﭏ","אל"),
        #("œ ӕ","ae oe"),
        ("", ""),
    ]

    for (inp, out_exp) in testStrings:
        r = FingerprintKeyer(inp)
        print "inp=%s" % inp
        print "out_exp=%s" % out_exp
        print "r=%s" % r
        print "FingerprintKeyer(%s)" % inp
        print "result=%s" % (r == out_exp)
        print ""


def demo2():
    print "=" * 80
    print "Demo 2"
    print "=" * 80

    print "Strings originales"
    for s in testStrings:
        print s
    print ""

    # df = pd.read_csv("audiencias-raw.csv")
    # testStrings = df.lugar

    clusters, counts = GroupFingerprintStrings(testStrings)
    print "Clusters encontrados"
    pprint(clusters)
    print ""

    print "Conteos de strings"
    pprint(counts)
    print ""

    # Para cada cluster tomo la string raw que resulte mas apta
    d = GetBestReplacements(clusters, counts)
    print "Strings de replazo para cada key"
    pprint(d)
    print ""

    # Reemplazo las keys que matchean el fingerprint una version
    print "Output:"
    for s in ReplaceByKey(d, testStrings):
        print s
    print ""

if __name__ == "__main__":
    demo1()
    demo2()
