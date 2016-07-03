# Team code for GEDCOM Project SSW 555
# Daniel Heyman, Danielle Romanoff, and Matthew Melachrinos

import sys  # graceful exit
import time # current date
from datetime import date # differences in date

# open and read GEDCOM file
fname = raw_input('Please enter the file name: ')

try:
    file = open(fname, 'r').read().replace("\xef\xbb\xbf", "").splitlines()
except IOError:
    print 'That is an incorrect file name.'
    sys.exit()

currentDate = time.strftime("%d %b %Y") # Ex: 19 JAN 2007

def isDateBeforeOrEqual(date1,date2,diffYear=0):
    months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

    # Parse first date
    date1year = int(date1[-4:]) + diffYear
    date1month = date1[-8:-5].upper()
    date1date = int(date1[:-9])

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

def differenceInDate(date1,date2):
    months = ["JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12]

    # Parse first date
    date1year = int(date1[-4:])
    date1month = date1[-8:-5].upper()
    date1date = int(date1[:-9])
    d1 = date(date1year,months[date1month],date1date)

    # Parse second date
    date2year = int(date2[-4:])
    date2month = date2[-8:-5].upper()
    date2date = int(date2[:-9])
    d2 = date(date2year,months[date2month],date2date)

    difference = d2-d1
    return difference.days

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
            families[id_num] = {}
            families[id_num]['CHIL'] = []
    # Ensure that the tag is valid
    elif int(parts[0]) < 3 and parts[1] in tags[int(parts[0])]:
        # Add a tag to the family or individual
        if parts[0] == '1' and len(parts) > 2:
            if id_type == 'INDI':
                individuals[id_num][parts[1]] = ' '.join(parts[2:])
            if id_type == 'FAM':
                if parts[1] == "CHIL":
                    families[id_num]['CHIL'] += [' '.join(parts[2:])]
                else:
                    families[id_num][parts[1]] = ' '.join(parts[2:])
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
                families[id_num][date_type] = ' '.join(parts[2:])

            date_type = ''


print "\nIndividuals:"
print "***************\n"
for individual_id in sorted(individuals.keys()):
    print "Individual ID:", individual_id
    print "Name:", individuals[individual_id]["NAME"]
    if individuals[individual_id].has_key('BIRT'):
        print "Birth:", individuals[individual_id]["BIRT"]
    print ""

print "\nFamilies:"
print "************\n"
for family_id in sorted(families.keys()):
    print "Family ID:", family_id
    for member in [["HUSB", "Husband"], ["WIFE", "Wife"]]:
        if families[family_id].has_key(member[0]):
            print member[1] + ": " + individuals[families[family_id][member[0]]]['NAME']
    for child_id in families[family_id]['CHIL']:
        print 'Child' + ": " + individuals[child_id]['NAME']
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

    #---------US07---------
    # Age over 150 years old
    # Death minus Birth should be less than 150 years
    if individual.has_key('BIRT') and individual.has_key('DEAT'):
        if isDateBeforeOrEqual(individuals['BIRT'], individuals['DEAT'], 150):
            print "ANOMALY: " , individual["NAME"], " lived passed 150 years."
    #---------US07---------

for family_id in families:
    family = families[family_id]

    husbandID = ""
    wifeID = ""
    weddingDate = ""
    divorceDate = ""
    if family.has_key('HUSB'): husbandID = family['HUSB']
    if family.has_key('WIFE'): wifeID = family['WIFE']
    if family.has_key('MARR'): weddingDate = family['MARR']
    if family.has_key('DIV'): divorceDate = family['DIV']

    #---------US02---------
    # Birth before marriage
    # Birth should occur before marriage of an individual
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key("BIRT") and isDateBeforeOrEqual(individuals[husbandID]['BIRT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date is before the birth of ", individuals[husbandID]["NAME"]
        if individuals[wifeID].has_key("BIRT") and isDateBeforeOrEqual(individuals[wifeID]['BIRT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date is before the birth of ", individuals[wifeID]["NAME"]
    #---------US02---------


    for child_id in family['CHIL']:
        #---------US09---------
        # Birth before death of parents
        # Birth should occur before death a parent. Anomaly (Unusual circumstances could create the death of a parent before the birth of a child)
        if husbandID and individuals[husbandID].has_key("DEAT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[husbandID]['DEAT'],individuals[child_id]['BIRT']):
                print "ANOMALY: ", individuals[husbandID]["NAME"] , " died prior to his child's birth."
        if wifeID and individuals[wifeID].has_key("DEAT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[wifeID]['DEAT'],individuals[child_id]['BIRT']):
                print "ERROR: ", individuals[wifeID]["NAME"] , " died prior to her child's birth."
        #---------US09---------

        #---------US08---------
        # Birth during parents marriage
        # Birth should occur after parents are married and before they are divorced
        if weddingDate != "" and individuals[child_id].has_key("BIRT") and isDateBeforeOrEqual(individuals[child_id]["BIRT"],weddingDate):
            print "ANOMALY: ", individuals[child_id]["NAME"] , " was born before parents were married."
        if divorceDate != "" and individuals[child_id].has_key("BIRT") and isDateBeforeOrEqual(divorceDate,individuals[child_id]["BIRT"]):
            print "ANOMALY: ", individuals[child_id]["NAME"] , " was born after parents were divorced."
        #---------US08---------

    #---------US04---------
    # Marriage before divorce
    # Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    if weddingDate != "" and divorceDate != "" and isDateBeforeOrEqual(divorceDate,weddingDate):
        print "ERROR (Fam " + family_id + "): Divorce date before Wedding date for " , individuals[husbandID]["NAME"], " and " , individuals[wifeID]["NAME"]
    #---------US04---------

    #---------US05---------
    # Marriage before death
    # Marriage should occur before death of either spouse
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key("DEAT") and isDateBeforeOrEqual(individuals[husbandID]['DEAT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date is after the death of ", individuals[husbandID]["NAME"]
        if individuals[wifeID].has_key("DEAT") and isDateBeforeOrEqual(individuals[wifeID]['DEAT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date is after the death of ", individuals[wifeID]["NAME"]
    #---------US05-----------

    #---------US06---------
    # Divorce before death
    # Divorce can only occur before death of both spouses
    if husbandID and wifeID and divorceDate:
        if individuals[husbandID].has_key("DEAT") and isDateBeforeOrEqual(individuals[husbandID]['DEAT'], divorceDate):
            print "ERROR (Fam " + family_id + "): The divorce date is after the death of ", individuals[husbandID]["NAME"]
        if individuals[wifeID].has_key("DEAT") and isDateBeforeOrEqual(individuals[wifeID]['DEAT'], divorceDate):
            print "ERROR (Fam " + family_id + "): The divorce date is after the death of ", individuals[wifeID]["NAME"]
    #---------US06---------

    #---------US12---------
    # Parents not too old
    # Mother should be less than 60 years older than her children and father should be less than 80 years older than his children
    for child_id in family['CHIL']:
        if wifeID and individuals[wifeID].has_key("BIRT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[wifeID]['BIRT'], individuals[child_id]['BIRT'], 60):
                print "ANOMALY: (Fam " + family_id + "): The mother is more than 60 years older than", individuals[child_id]["NAME"]
        if husbandID and individuals[husbandID].has_key("BIRT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[husbandID]['BIRT'], individuals[child_id]['BIRT'], 80):
                print "ANOMALY: (Fam " + family_id + "): The father is more than 80 years older than", individuals[child_id]["NAME"]
    #---------US12---------

    #---------US21---------
    # Correct gender for role
    # Husband in family should be male and wife in family should be female
    if wifeID and individuals[wifeID].has_key("SEX") and individuals[wifeID]["SEX"] != "F":
        print "ERROR (Fam " + family_id + "): The wife, " + individuals[wifeID]["NAME"] + ", should be female"
    if husbandID and individuals[husbandID].has_key("SEX") and individuals[husbandID]["SEX"] != "M":
        print "ERROR (Fam " + family_id + "): The husband, " + individuals[husbandID]["NAME"] + ", should be male"
    #---------US21---------
