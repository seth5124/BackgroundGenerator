import random
import xml.etree.ElementTree as ET

test_race = "Dwarf"

root = ET.parse('backgroundData.xml').getroot()
races = root.find('Races')

traits = dict()
number_of_siblings = 0




def roll(die_type, modifier=0, multiplier=1):
    return (random.randint(1, int(die_type)) * int(multiplier)) + int(modifier)


def table_roll(table):
    die_type = table.attrib['dieType']  # Pulls die type from table
    modifier = 0  # stores die roll modifier e.g 1d4 +1
    multiplier = 1  # Handles multiple dice e.g 2d4
    global number_of_siblings

    if 'modifier' in table.attrib:
        modifier = table.attrib['modifier']  # Pulls die modifier from table

    if 'multiplier' in table.attrib:
        multiplier = table.attrib['multiplier']  # pulls die multiplier from table

    roll_value = roll(die_type, modifier, multiplier)  # generates die roll

    return_string = str(roll_value) + ": "  # initiates the output string
    outcome = Result()    # instantiates a result object that will store output string, traits and number of siblings
    outcome.add_to_return(str(roll_value) + ": ")

    for result in table.findall('Result'):  # iterates over results to determine which one you rolled

        roll_upper_bound = result.attrib['upperBound']  # pulls result upper bound from table
        if roll_value <= int(roll_upper_bound):
            # return_string += str(result.find('Name').text)  # appends the name of the result to the output string
            outcome.add_to_return(str(result.find('Name').text))  # appends to the output string in the result object
            if result.findall('Trait') is not None:  # checks if the result gives you access to any traits
                for trait in result.findall('Trait'):
                    outcome.add_trait(trait.text, trait.attrib["type"])   # adds the trait as a dictionary with the value being the trait type

            if 'hasExtraRoll' in result.attrib:  # checks if the result requires any extra rolls

                extra_rolls = result.findall('ExtraRoll')

                for extra_roll in extra_rolls:

                    table_source = extra_roll.find('Source').text  # pulls location of the necessary table for the extra roll

                    if table_source == "Local":  # local tables are located within the result itself

                        table_source = extra_roll.find('Table')
                    else:
                        table_source = root.find(table_source)  # if not local, the result will include the full path to the table

                    outcome.extra_roll(table_roll(table_source))



            number_of_siblings += outcome.get_num_siblings()
            break




    return outcome


def roll_homeland(race=test_race):
    print((table_roll(races.find('%s/Homeland' % race)).get_return_string()))


def roll_parents(race=test_race):
    print(table_roll(races.find('%s/Parents' % race)).get_return_string())


def roll_siblings(race=test_race):
    global number_of_siblings
    print(table_roll(races.find('%s/Siblings' % race)).get_return_string())
    if number_of_siblings >= 2:
        traits['Kin Guardian'] = 'Combat'



def roll_background(race=test_race):
    global number_of_siblings
    traits.clear()
    number_of_siblings = 0
    print("Race:" + race)
    print("Homeland:")
    roll_homeland(race)
    print("Parents:")
    roll_parents(race)
    print("Siblings:")
    roll_siblings(race)
    print(traits)
    print(number_of_siblings)
    print("Yeet")





class Result:

    def __init__(self):
        self.return_string = ""
        self.num_siblings = 0
        self.traits = dict()

    def add_to_return(self, addition):
        self.return_string += addition

    def get_return_string(self):
        return self.return_string

    def add_trait(self, trait, trait_type):
        if trait_type == "numSiblings":
            self.num_siblings += int(trait)
        else:
            traits[trait] = trait_type




    def get_num_siblings(self):
        return self.num_siblings

    def get_traits(self):
        return self.traits

    def extra_roll(self, result):
        self.add_to_return("\n \t" + result.get_return_string())



roll_siblings()
