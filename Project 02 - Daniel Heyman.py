# Daniel Heyman
# CS 555
# Project 02

file = open('family.ged').read().splitlines()
zero_tags = ["HEAD", "TRLR", "NOTE"]
one_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"]
two_tags = ["DATE"]
tags = [zero_tags, one_tags, two_tags]

for line in file:
    print line
    line = line.split(' ')
    print line[0]
    if len(line) == 3 and line[0] == '0' and line[2] in ["FAM","INDI"]:
        print line[2]
    elif line[1] in tags[int(line[0])]:
        print line[1]
    else:
        print "Invalid tag"
    print ""
