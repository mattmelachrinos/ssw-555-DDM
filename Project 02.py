# Project Week 2 Assignment
# This program will read my GEDCOM file, print each line, prints the level number of each line, and the tag if valid 
# If no valid tag is found it will print Invalid tag
# Danielle Romanoff

import sys

Tags = ['NAME','SEX','BIRT','DEAT','FAMC','FAMS','FAM','MARR','HUSB','WIFE','CHIL','DIV','DATE','HEAD','TRLR','NOTE']

# open and read GEDCOM file
fname=raw_input('Please enter the file name: ')

try:
    Family_Tree = open(fname,'r') 

except:
    print 'That is an incorrect file name.'
    sys.exit()

print 'The following format on each printed line is as follows:'
print 'The line itself, the level number of that line, and the tag if there is one or invalid tag if not'
print '*****************************************************************************************************'

for line in Family_Tree:
    
    parts = line.lstrip().rstrip().split(' ')
    
    print 'The line is: ', line, 'The level is: ' , parts[0]
    if len(parts) >= 2 and parts[1] in Tags:
        print 'The Tag is: ', parts[1], '\n'
    elif len(parts) >= 3 and parts[2] == 'INDI':
        print 'The Tag is: ', parts[2], '\n'
    else:
        print 'Invalid tag \n'
        

