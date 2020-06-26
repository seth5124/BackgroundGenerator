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


def roll_homeland(race=test_race):
    homeland = races.find('%s/Homeland' % race)
    die_type = homeland.attrib['dieType']
    roll_value = roll(die_type)
    homeland_return_string = "You Rolled: " + str(roll_value) + " Your homeland is: "

    for x in (homeland.findall('Result')):
        if x.find('Name').text == "Unusual Homeland":
            homeland_return_string += "Unusual! "
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




