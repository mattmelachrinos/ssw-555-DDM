# Team code for GEDCOM Project SSW 555
# Daniel Heyman, Danielle Romanoff, and Matthew Melachrinos

import sys  # graceful exit

# open and read GEDCOM file
fname = raw_input('Please enter the file name: ')

try:
    file = open(fname, 'r').read().replace("\xef\xbb\xbf", "").splitlines()

except:
    print 'That is an incorrect file name.'
    sys.exit()

zero_tags = ["HEAD", "TRLR", "NOTE"]
one_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"]
two_tags = ["DATE"]
tags = [zero_tags, one_tags, two_tags]

families = {}
individuals = {}
id_type = 'none'
id_num = ''
date_type = ''
family_tags = {"HUSB": "Husband", "WIFE": "Wife", "CHIL": "Child"}

print 'The following format on each printed line is as follows:'
print 'The line itself, the level number of that line, and the tag if there is one or invalid tag if not'
print '*****************************************************************************************************'

for line in file:
    line = line.lstrip().rstrip()
    print 'The line is:', line
    parts = line.split(' ')
    print 'The level is:', parts[0]

    if len(parts) == 3 and parts[0] == '0' and parts[2] in ["FAM","INDI"]:
        print 'The tag is:', parts[2]
        id_type = parts[2]
        id_num = parts[1]
        if(id_type == 'INDI'):
            individuals[id_num] = {}
        else:
            families[id_num] = []
    elif int(parts[0]) < 3 and parts[1] in tags[int(parts[0])]:
        print 'The tag is:', parts[1]
        if parts[0] == '1' and len(parts) > 2:
            if id_type == 'INDI':
                individuals[id_num][parts[1]] = ' '.join(parts[2:])
            if id_type == 'FAM':
                families[id_num] += [[parts[1], parts[2]]]
        if parts[0] == '1' and parts[1] in ["BIRT", "DEAT", "MARR", "DIV"]:
            date_type = parts[0]
        if date_type != '' and parts[0] == '2' and parts[1] == 'DATE':
            individuals[id_num][date_type] = ' '.join(parts[2:])
    else:
        print "Invalid tag"
    print ""

print "\nIndividuals:"
for individual in sorted(individuals.keys()):
    print "Individual ID:", individual
    print "Name:", individuals[individual]["NAME"], "\n"

print "\nFamilies:"
for family in sorted(families.keys()):
    print "Family ID:", family
    for member in families[family]:
        if member[0] in family_tags:
            print family_tags[member[0]] + ": " + individuals[member[1]]['NAME']
    print ""
