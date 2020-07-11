import random
import xml.etree.ElementTree as ET


test_race = "Dwarf"

tree = ET.parse('backgroundData.xml')
root = tree.getroot()
races = root.find('Races')
misc_tables = root.find('MiscTables')

traits = []

def roll(die_type, modifier=0):
    return random.randint(1, int(die_type)) + modifier


def table_roll(table):
    die_type = table.attrib['dieType']
    roll_value = roll(die_type)
    return_string = ""

    for result in table.findall('Result'):

        roll_upper_bound = result.attrib['upperBound']
        if roll_value <= int(roll_upper_bound):
            name = str(result.find('Name').text)
            return_string = str(roll_value) + ": " + name

            if 'hasExtraRoll' in result.attrib:
                extra_roll = result.find('ExtraRoll')
                extra_roll_table = root.find(extra_roll.find('Table').text)
                return_string += "\n \t" + table_roll(extra_roll_table)
            break
        else:
            name = result.find('Name').text

    return return_string


def roll_homeland(race = test_race):
    print(table_roll(races.find('%s/Homeland' % race)))

def roll_parents(race = test_race):
    print(table_roll(races.find('%s/Parents' % race)))




def roll_background(race=test_race):
    roll_homeland()
    roll_parents()





