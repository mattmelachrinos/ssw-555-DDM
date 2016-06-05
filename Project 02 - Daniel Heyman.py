# Daniel Heyman
# CS 555
# Project 02

import sys  # graceful exit

# open and read GEDCOM file
fname=raw_input('Please enter the file name: ')

try:
    file = open(fname,'r').read().splitlines() 

except:
    print 'That is an incorrect file name.'
    sys.exit()

zero_tags = ["HEAD", "TRLR", "NOTE"]
one_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"]
two_tags = ["DATE"]
tags = [zero_tags, one_tags, two_tags]


print 'The following format on each printed line is as follows:'
print 'The line itself, the level number of that line, and the tag if there is one or invalid tag if not'
print '*****************************************************************************************************'

for line in file:
    print 'The line is: ' , line , '\n'
    line = line.lstrip().rstrip().split(' ')
    print 'The level is: ' , line[0] , '\n'
    if len(line) == 3 and line[0] == '0' and line[2] in ["FAM","INDI"]:
        print 'The Tag is: ' , line[2] , '\n'
    elif line[1] in tags[int(line[0])]:
        print 'The Tag is: ' , line[1] , '\n'
    else:
        print "Invalid tag"
    print ""
