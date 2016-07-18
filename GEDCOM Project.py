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
    return (differenceInDate(date1, date2) - diffYear * 360) >= 0

def differenceInDate(date1,date2):
    # Parse dates
    d1 = stringToDate(date1)
    d2 = stringToDate(date2)

    difference = d2 - d1
    return difference.days

def stringToDate(date1):
    months = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

    date1year = int(date1[-4:])
    date1month = date1[-8:-5].upper()
    date1date = int(date1[:-9])
    return date(date1year,months[date1month],date1date)

# All the valid tags
zero_tags = ["HEAD", "TRLR", "NOTE"]
one_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"]
two_tags = ["DATE"]
tags = [zero_tags, one_tags, two_tags]

# Object for all the family members. Key is based off of the family ID
families = {}

# Object for all the individuals. Key is based off of the individual ID
individuals = {}

# Object for errors found in file parsing that should will print later

errors = []

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
            #---------US22---------
            if id_num in individuals:
                errors.append("Error: "+ id_num + " is already being used by " + individuals[id_num]["NAME"] + ". Don't trust relationships with " + id_num)
            #---------US22---------
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
    if individuals[individual_id].has_key("SEX"):
        print "Sex:", individuals[individual_id]["SEX"]
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

for item in errors:
    print item.upper()
print ""
print ""

for individual_id in individuals:
    individual = individuals[individual_id]

    #---------US01---------
    # Dates before current date
    # Dates (birth, marriage, divorce, death) should not be after the current date
    if individual.has_key('BIRT') and isDateBeforeOrEqual(currentDate, individual['BIRT']):
        print "ERROR: The birth date (" + individual['BIRT'] + ") is after current date (" + currentDate + ") for " , individual["NAME"] + "."
    if individual.has_key('DEAT') and isDateBeforeOrEqual(currentDate, individual['DEAT']):
        print "ERROR: The death date (" + individual['DEAT'] + ") is after current date (" + currentDate + ") for " , individual["NAME"] + "."
    #---------US01---------

    #---------US03---------
    # Birth before death
    # Birth should occur before death of an individual
    if individual.has_key('BIRT') and individual.has_key('DEAT') and isDateBeforeOrEqual(individual['DEAT'], individual['BIRT']):
        print "ERROR: The death date (" + individual['DEAT'] + ") is before birth date (" + individual['BIRT'] + ") for " , individual["NAME"] + "."
    #---------US03---------

    #---------US07---------
    # Age over 150 years old
    # Death minus Birth should be less than 150 years
    if individual.has_key('BIRT') and individual.has_key('DEAT'):
        if isDateBeforeOrEqual(individual['BIRT'], individual['DEAT'], 150):
            print "ANOMALY: " , individual["NAME"], " lived passed 150 years."
    elif individual.has_key('BIRT'):
        if isDateBeforeOrEqual(individual['BIRT'], currentDate, 150):
             print "ANOMALY: " , individual["NAME"], " is older than 150 years."
    #---------US07---------

# Contains the families for each parent
groupMarriagesByParent = {}

for family_id in families:
    family = families[family_id]

    husbandID = ""
    wifeID = ""
    weddingDate = ""
    divorceDate = ""
    kidDict = {}
    if family.has_key('HUSB'):
        husbandID = family['HUSB']
        if not husbandID in groupMarriagesByParent:
            groupMarriagesByParent[husbandID] = []
        groupMarriagesByParent[husbandID] += [family_id]
    if family.has_key('WIFE'):
        wifeID = family['WIFE']
        if not wifeID in groupMarriagesByParent:
            groupMarriagesByParent[wifeID] = []
        groupMarriagesByParent[wifeID] += [family_id]
    if family.has_key('MARR'): weddingDate = family['MARR']
    if family.has_key('DIV'): divorceDate = family['DIV']

    #---------US02---------
    # Birth before marriage
    # Birth should occur before marriage of an individual
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key("BIRT") and isDateBeforeOrEqual(individuals[husbandID]['BIRT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date (" + weddingDate + ") is before the birth of ", individuals[husbandID]["NAME"] + "."
        if individuals[wifeID].has_key("BIRT") and isDateBeforeOrEqual(individuals[wifeID]['BIRT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date (" + weddingDate + ") is before the birth of ", individuals[wifeID]["NAME"] + "."
    #---------US02---------


    for child_id in family['CHIL']:
        #---------US09---------
        # Birth before death of parents
        # Birth should occur before death a parent. Anomaly (Unusual circumstances could create the death of a parent before the birth of a child)
        if husbandID and individuals[husbandID].has_key("DEAT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[husbandID]['DEAT'],individuals[child_id]['BIRT']):
                print "ANOMALY: ", individuals[husbandID]["NAME"] , " died on (" + individuals[husbandID]['DEAT'] + ") prior to his child's birth."
        if wifeID and individuals[wifeID].has_key("DEAT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[wifeID]['DEAT'],individuals[child_id]['BIRT']):
                print "ERROR: ", individuals[wifeID]["NAME"] , " died on (" + individuals[wifeID]['DEAT'] + ") prior to her child's birth."
        #---------US09---------

        #---------US08---------
        # Birth during parents marriage
        # Birth should occur after parents are married and before they are divorced
        if weddingDate != "" and individuals[child_id].has_key("BIRT") and isDateBeforeOrEqual(individuals[child_id]["BIRT"],weddingDate):
            print "ANOMALY: ", individuals[child_id]["NAME"] , " was born before parents were married on (" + weddingDate + ")."
        if divorceDate != "" and individuals[child_id].has_key("BIRT") and isDateBeforeOrEqual(divorceDate,individuals[child_id]["BIRT"]):
            print "ANOMALY: ", individuals[child_id]["NAME"] , " was born after parents were divorced on (" + divorceDate + ")."
        #---------US08---------

        #---------US17---------
        # Parents not marrying children
        if husbandID:
            if husbandID == child_id:
                print "ERROR:",individuals[wifeID]["NAME"], "Married her child,",individuals[child_id]["NAME"]
        if wifeID:
            if wifeID == child_id:
                print "ERROR:",individuals[husbandID]["NAME"], "Married his child,",individuals[child_id]["NAME"]
        #---------US17---------


    #---------US13---------
    # Sibling spacing
    # makes sure the children are spaced less than 2 days or more than 280
    # note: starts in child loop ends outside of it. Yes this is ugly
        if individuals[child_id].has_key("BIRT"):
            kidDict[individuals[child_id]["BIRT"]] = child_id

    for date1 in kidDict:
        for date2 in kidDict:
            if differenceInDate(date1,date2) > 3 and differenceInDate(date1,date2) < 280:
                print "ERROR: ", individuals[kidDict[date1]]["NAME"], " and ", individuals[kidDict[date1]]["NAME"], " are not twins and are born less than 9 months apart."

    #---------US13---------

    #---------US10---------
    # Marriage after 14
    # Marriage should occur after the age of 14
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key("BIRT") and differenceInDate(weddingDate,individuals[husbandID]['BIRT']) < 14:
            print "ANOMALY (Fam " + family_id + "): The marriage of " + individuals[husbandID]["NAME"] + " took place before he was 14 years old."
        if individuals[wifeID].has_key("BIRT") and differenceInDate(weddingDate,individuals[wifeID]['BIRT']) < 14:
            print "ANOMALY (Fam " + family_id + "): The marriage of " + individuals[wifeID]["NAME"] + " took place before she was 14 years old."
    #---------US10---------

    #---------US34---------
    # List large age differences
    # The older spouse was more than twice as old as the younger spouse
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key('BIRT'):
            AgeofHusband = differenceInDate(weddingDate,individuals[husbandID]['BIRT'])
        if individuals[wifeID].has_key('BIRT'):
            AgeofWife = differenceInDate(weddingDate,individuals[wifeID]['BIRT'])
        if AgeofHusband > 2 * AgeofWife or AgeofWife > 2 * AgeofHusband:
            print "ANOMALY (Fam " + family_id + "): There is a large age difference between " + individuals[husbandID]['NAME'] + " and " + individuals[wifeID]['NAME'] + "."
    #---------US34---------

    #---------US04---------
    # Marriage before divorce
    # Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    if weddingDate != "" and divorceDate != "" and isDateBeforeOrEqual(divorceDate,weddingDate):
        print "ERROR (Fam " + family_id + "): Divorce date (" + divorceDate + ") is before Wedding date (" + weddingDate + ") for " , individuals[husbandID]["NAME"], " and " , individuals[wifeID]["NAME"] + "."
    #---------US04---------

    #---------US05---------
    # Marriage before death
    # Marriage should occur before death of either spouse
    if husbandID and wifeID and weddingDate:
        if individuals[husbandID].has_key("DEAT") and isDateBeforeOrEqual(individuals[husbandID]['DEAT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date (" + weddingDate + ") is after the death (" + individuals[husbandID]['DEAT'] + ") of ", individuals[husbandID]["NAME"] + "."
        if individuals[wifeID].has_key("DEAT") and isDateBeforeOrEqual(individuals[wifeID]['DEAT'], weddingDate):
            print "ERROR (Fam " + family_id + "): The wedding date (" + weddingDate + ") is after the death (" + individuals[wifeID]['DEAT'] + ") of ", individuals[wifeID]["NAME"] + "."
    #---------US05-----------

    #---------US06---------
    # Divorce before death
    # Divorce can only occur before death of both spouses
    if husbandID and wifeID and divorceDate:
        if individuals[husbandID].has_key("DEAT") and isDateBeforeOrEqual(individuals[husbandID]['DEAT'], divorceDate):
            print "ERROR (Fam " + family_id + "): The divorce date (" + divorceDate + ") is after the death (" + individuals[husbandID]['DEAT'] + ") of ", individuals[husbandID]["NAME"] + "."
        if individuals[wifeID].has_key("DEAT") and isDateBeforeOrEqual(individuals[wifeID]['DEAT'], divorceDate):
            print "ERROR (Fam " + family_id + "): The divorce date (" + divorceDate + ") is after the death (" + individuals[wifeID]['DEAT'] + ")  of ", individuals[wifeID]["NAME"] + "."
    #---------US06---------

    #---------US12---------
    # Parents not too old
    # Mother should be less than 60 years older than her children and father should be less than 80 years older than his children
    for child_id in family['CHIL']:
        if wifeID and individuals[wifeID].has_key("BIRT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[wifeID]['BIRT'], individuals[child_id]['BIRT'], 60):
                print "ANOMALY: (Fam " + family_id + "): The mother is more than 60 years older than her child, " + individuals[child_id]["NAME"] + "."
        if husbandID and individuals[husbandID].has_key("BIRT") and individuals[child_id].has_key("BIRT"):
            if isDateBeforeOrEqual(individuals[husbandID]['BIRT'], individuals[child_id]['BIRT'], 80):
                print "ANOMALY: (Fam " + family_id + "): The father is more than 80 years older than his child, " + individuals[child_id]["NAME"] + "."
    #---------US12---------

    #---------US16---------
    # Male last names
    # All male members of a family should have the same last name
    if husbandID:
        lastName = individuals[husbandID]["NAME"].split(' ')[-1]
        for child_id in family['CHIL']:
            if individuals[child_id].has_key("SEX") and individuals[child_id]["SEX"] != "M":
                continue
            if lastName != individuals[child_id]["NAME"].split(' ')[-1]:
                print "ANOMALY: (Fam " + family_id + "): The father has a different last name than his child, " + individuals[child_id]["NAME"] + "."
    #---------US16---------

    #---------US21---------
    # Correct gender for role
    # Husband in family should be male and wife in family should be female
    if wifeID and individuals[wifeID].has_key("SEX") and individuals[wifeID]["SEX"] != "F":
        print "ERROR (Fam " + family_id + "): The wife, " + individuals[wifeID]["NAME"] + ", should be female" + "."
    if husbandID and individuals[husbandID].has_key("SEX") and individuals[husbandID]["SEX"] != "M":
        print "ERROR (Fam " + family_id + "): The husband, " + individuals[husbandID]["NAME"] + ", should be male" + "."
    #---------US21---------


#---------US11---------
# No bigamy
# Marriage should not occur during marriage to another spouse
for parent_id in groupMarriagesByParent:
    family_group = filter(lambda fam: families[fam].has_key("MARR"),groupMarriagesByParent[parent_id])
    if len(family_group) < 2: continue
    def sortByMarr(family_id, family_id2):
        return differenceInDate(families[family_id2]['MARR'], families[family_id]['MARR'])
    family_group = sorted(family_group, sortByMarr)

    for i in range(len(family_group) - 1):
        if families[family_group[i]].has_key('DIV'):
            if isDateBeforeOrEqual(families[family_group[i]]['DIV'], families[family_group[i + 1]]['MARR']): continue
        print "ANOMALY: The family " + family_group[i] + " does not divorce before the marriage of family " + family_group[i + 1]  + "."
#---------US11---------
