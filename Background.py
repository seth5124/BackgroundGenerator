import random
import xml.etree.ElementTree as ET


test_race = "Dwarf"

tree = ET.parse('backgroundData.xml')
root = tree.getroot()
races = root.find('Races')


def roll(die_type, modifier=0):
    return random.randint(1, int(die_type)) + modifier


def roll_background(race=test_race):
    print(roll_homeland(race))
    print(roll_parents(race))


def roll_homeland(race=test_race):
    homeland_table = races.find('%s/Homeland' % race)
    die_type = homeland_table.attrib['dieType']
    roll_value = roll(die_type)
    homeland_return_string = "Homeland \n" + "You Rolled: " + str(roll_value) + ", "

    for x in (homeland_table.findall('Result')):
        if x.find('Name').text == "Unusual Homeland":
            homeland_return_string += "Unusual Homeland! "
            homeland_return_string += roll_unusual_homeland(race)
            break
        if roll_value <= int(x.attrib['upperBound']):
            homeland_return_string += x.find('Name').text
            break
    return homeland_return_string


def roll_unusual_homeland(race=test_race):

    unusual_homeland_table = root.find("MiscTables/Unusual_Homeland")
    roll_value = roll(100)
    return_string = "Rolled: " + str(roll_value) + ", "

    for x in unusual_homeland_table.findall('Result'):
        if roll_value <= int(x.attrib['upperBound']):
            return_string += x.find('Name').text
            break

    return return_string


def roll_parents(race=test_race):
    parents_table = races.find('%s/Parents' % race)
    die_type = parents_table.attrib['dieType']
    roll_value=roll(die_type)
    parents_return_string = "Parents \n" + "You Rolled: " + str(roll_value) + ", "

    for result in parents_table.findall('Result'):
        if roll_value <= int(result.attrib['upperBound']):
            parents_return_string += result.find('Name').text
            break

    return parents_return_string



