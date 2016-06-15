# Team code for GEDCOM Project SSW 555
# Daniel Heyman, Danielle Romanoff, and Matthew Melachrinos

import sys  # graceful exit
import time # current date

# open and read GEDCOM file
fname = raw_input('Please enter the file name: ')

try:
    file = open(fname, 'r').read().replace("\xef\xbb\xbf", "").splitlines()

except:
    print 'That is an incorrect file name.'
    sys.exit()
    
currentDate = time.strftime("%d %b %Y") # Ex: 19 JAN 2007

def isDateBeforeOrEqual(date1,date2):
    months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

    # Parse first date
    date1year = int(date1[-4:])
    date1month = date1[-8:-5].upper()
    date1date = date1[:-9]

    # Parse second date
    date2year = int(date2[-4:])
    date2month = date2[-8:-5].upper()
    date2date = int(date2[:-9])

    if date1year < date2year:
        return True
    elif date1year==date2year:
        for item in months:
            if date1month == item:
                date1month = int(months.index(item))
            if date2month == item:
                date2month = int(months.index(item))
        if date1month < date2month:
            return True
        elif date1month == date2month:
            if date1date <= date2date:
                return True
        return False
    return False

# All the valid tags
zero_tags = ["HEAD", "TRLR", "NOTE"]
one_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"]
two_tags = ["DATE"]
tags = [zero_tags, one_tags, two_tags]

# Object for all the family members. Key is based off of the family ID
families = {}

# Object for all the individuals. Key is based off of the individual ID
individuals = {}

# Current individual or family
id_type = 'none' # When active, will be marked with FAM or INDI
id_num = ''

# Keeps track of the dates
date_type = ''

# The dictionary of valid family tags
family_tags = {"HUSB": "Husband", "WIFE": "Wife", "CHIL": "Child"}

# Loop through all the lines in the GEDCOM file
for line in file:
    line = line.lstrip().rstrip()
    parts = line.split(' ')

    # Case that marks the beginning of a new family or individual
    if len(parts) == 3 and parts[0] == '0' and parts[2] in ["FAM","INDI"]:
        id_type = parts[2]
        id_num = parts[1]
        
        # Initiate the object for the new family or individual
        if(id_type == 'INDI'):
            individuals[id_num] = {}
        else:
            families[id_num] = []
    # Ensure that the tag is valid
    elif int(parts[0]) < 3 and parts[1] in tags[int(parts[0])]:
        # Add a tag to the family or individual
        if parts[0] == '1' and len(parts) > 2:
            if id_type == 'INDI':
                individuals[id_num][parts[1]] = ' '.join(parts[2:])
            if id_type == 'FAM':
                families[id_num] += [[parts[1], parts[2]]]
        # Prepare to add a date tag
        if parts[0] == '1' and parts[1] in ["BIRT", "DEAT", "MARR", "DIV"]:
            date_type = parts[1]
        # Add the date based on the previously found tag
        if date_type != '' and parts[0] == '2' and parts[1] == 'DATE':
            # BIRT and DEAT tags belong to an individual
            if id_type == 'INDI' and date_type in ["BIRT", "DEAT"]:
                individuals[id_num][date_type] = ' '.join(parts[2:])
            # MARR and DIV belong to a family
            elif id_type == 'FAM' and date_type in ["MARR", "DIV"]:
                families[id_num] += [[date_type, ' '.join(parts[2:])]]


print "\nIndividuals:"
print "***************\n"
for individual in sorted(individuals.keys()):
    print "Individual ID:", individual
    print "Name:", individuals[individual]["NAME"]
    if individuals[individual].has_key('BIRT'):
        print "Birth:", individuals[individual]["BIRT"],"\n"

print "\nFamilies:"
print "************\n"
for family in sorted(families.keys()):
    print "Family ID:", family
    for member in families[family]:
        if member[0] in family_tags:
            print family_tags[member[0]] + ": " + individuals[member[1]]['NAME']
    print ""


#---------Error Checking---------

for individual_id in individuals:
    individual = individuals[individual_id]
    
    #---------US01---------
    # Dates before current date
    # Dates (birth, marriage, divorce, death) should not be after the current date
    if individual.has_key('BIRT') and isDateBeforeOrEqual(currentDate, individual['BIRT']):
        print "ERROR: The birth date is after current date for " , individual["NAME"]
    if individual.has_key('DEAT') and isDateBeforeOrEqual(currentDate, individual['DEAT']):
        print "ERROR: The death date is after current date for " , individual["NAME"]
    #---------US01---------
    
    #---------US03---------
    # Birth before death
    # Birth should occur before death of an individual
    if individual.has_key('BIRT') and individual.has_key('DEAT') and isDateBeforeOrEqual(individual['DEAT'], individual['BIRT']):
        print "ERROR: The death date is before birth date for " , individual["NAME"]
    #---------US03---------

for family in families:
    husbandID = ""
    wifeID = ""
    weddingDate = ""
    divorceDate = ""

    # Since the family data is stored as fam = [['HUSB', ID], ['WIFE', ID], etc] to account for multiple children, 
    # this loop can extract some information for quicker use
    for item in families[family]:
        if item[0] == "HUSB":
            husbandID = item[1]
        if item[0] == "WIFE":
            wifeID = item[1]
        if item[0] == "MARR":
            weddingDate = item[1]
        if item[0] == "DIV":
            divorceDate = item[1]
            
    #---------US02---------
    # Birth before marriage
    # Birth should occur before marriage of an individual
    if husbandID and wifeID and weddingDate:
        husbandBirthDay = individuals[husbandID]["BIRT"]
        wifeBirthDay = individuals[wifeID]["BIRT"]
        if isDateBeforeOrEqual(weddingDate,husbandBirthDay):
            print "ERROR: The wedding date is before the birth of ", individuals[husbandID]["NAME"]
        if isDateBeforeOrEqual(weddingDate,wifeBirthDay):
            print "ERROR: The wedding date is before the birth of ", individuals[wifeID]["NAME"]
    #---------US02---------

    #---------US04---------
    # Marriage before divorce
    # Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    if weddingDate != "" and divorceDate != "" and isDateBeforeOrEqual(divorceDate,weddingDate):
        print "ERROR: Divorce date before Wedding date for " , individuals[husbandID]["NAME"], " and " , individuals[wifeID]["NAME"]
    #---------US04---------

    #---------US05---------
    # Marriage before death
    # Marriage should occur before death of either spouse
    if husbandID and wifeID and weddingDate:
        husbanddeathDay = individuals[husbandID]["DEAT"]
        wifedeathDay = individuals[wifeID]["DEAT"]
        if isDateBeforeOrEqual(husbanddeathDay, weddingDate):
            print "ERROR: The wedding date is after the death of ", individuals[husbandID]["NAME"]
        if isDateBeforeOrEqual(wifedeathDay, weddingDate):
            print "ERROR: The wedding date is after the death of ", individuals[wifeID]["NAME"]
    #---------US05-----------

    #---------US06---------
    # Divorce before death
    # Divorce can only occur before death of both spouses
    if husbandID and wifeID and divorceDate:
        if individuals[husbandID].has_key("DEAT") and isDateBeforeOrEqual(individuals[husbandID]['DEAT'], divorceDate):
            print "ERROR: The divorce date is after the death of ", individuals[husbandID]["NAME"]
        if individuals[wifeID].has_key("DEAT") and isDateBeforeOrEqual(individuals[wifeID]['DEAT'], divorceDate):
            print "ERROR: The divorce date is after the death of ", individuals[wifeID]["NAME"]
    #---------US06---------
