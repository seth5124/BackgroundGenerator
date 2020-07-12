import random
import xml.etree.ElementTree as ET

test_race = "Dwarf"

root = ET.parse('backgroundData.xml').getroot()
races = root.find('Races')

traits = []


def roll(die_type, modifier=0, multiplier=1):
    return (random.randint(1, int(die_type)) * int(multiplier)) + int(modifier)


def table_roll(table):
    die_type = table.attrib['dieType']
    modifier = 0
    multiplier = 1
    if 'modifier' in table.attrib:
        modifier = table.attrib['modifier']

    if 'multiplier' in table.attrib:
        multiplier = table.attrib['multiplier']

    roll_value = roll(die_type, modifier, multiplier)

    return_string = str(roll_value) + ": "

    for result in table.findall('Result'):

        roll_upper_bound = result.attrib['upperBound']
        if roll_value <= int(roll_upper_bound):
            return_string += str(result.find('Name').text)

            if 'hasExtraRoll' in result.attrib:

                extra_rolls = result.findall('ExtraRoll')

                for extra_roll in extra_rolls:

                    table_source = extra_roll.find('Source').text

                    if table_source == "Local":

                        table_source = extra_roll.find('Table')
                    else:
                        table_source = root.find(table_source)

                    return_string += "\n \t" + table_roll(table_source)
            break
    return return_string


def roll_homeland(race=test_race):
    print(table_roll(races.find('%s/Homeland' % race)))


def roll_parents(race=test_race):
    print(table_roll(races.find('%s/Parents' % race)))


def roll_siblings(race=test_race):
    print(table_roll(races.find('%s/Siblings' % race)))


def roll_background(race=test_race):
    print("Race:" + race)
    print("Homeland:")
    roll_homeland()
    print("Parents:")
    roll_parents(race)
    print("Siblings:")
    roll_siblings(race)


# TODO: make result class, possibly use attribute values in each individual result and
#  import those as dictionary values to handle things like number of siblings etc.


roll_background()
