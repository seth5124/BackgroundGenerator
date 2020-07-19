import os
import random
import xml.etree.ElementTree as ET
import discord
from dotenv import load_dotenv
# TODO: convert to more efficient string concatenation solution
# TODO: ensure trait list doesn't include duplicates
# TODO: Convert traits to custom data type
# TODO: Relationships with fellow adventurers


load_dotenv()
token_file = open("token.txt", "r")
TOKEN = token_file.read()
GUILD = "Server"

test_race = "Dwarf"

root = ET.parse('backgroundData.xml').getroot()
races = root.find('Races')
classes = root.find('Classes')
list_of_half_races = {"Half-Elf", "Half-Orc"}
list_of_races = {"Dwarf", "Elf", "Gnome", "Human", "Halfling"}
list_of_classes = {"Alchemist", "Barbarian", "Bard", "Cavalier",
                   "Cleric", "Druid", "Fighter", "Gunslinger", "Inquisitor",
                   "Magus", "Monk", "Oracle", "Paladin", "Ranger", "Rogue", "Sorcerer",
                   "Summoner", "Witch", "Wizard"}

traits = dict()

number_of_siblings = 0


def roll(die_type, modifier=0, multiplier=1):
    return (random.randint(1, int(die_type)) * int(multiplier)) + int(modifier)


def table_roll(table):
    die_type = table.attrib['dieType']  # Pulls die type from table
    modifier = 0  # stores die roll modifier e.g 1d4 +1
    multiplier = 1  # Handles multiple dice e.g 2d4
    CP = 0
    global number_of_siblings

    if 'modifier' in table.attrib:
        modifier = table.attrib['modifier']  # Pulls die modifier from table

    if 'multiplier' in table.attrib:
        multiplier = table.attrib['multiplier']  # pulls die multiplier from table

    roll_value = roll(die_type, modifier, multiplier)  # generates die roll

    outcome = Result()
    outcome.add_to_return(str(roll_value) + ": ")  # Beginning of returned string

    for result in table.findall('Result'):  # iterates over results to determine which one was rolled

        roll_upper_bound = result.attrib['upperBound']  # pulls result upper bound from table attribute
        if roll_value <= int(roll_upper_bound):
            outcome.add_to_return(str(result.find('Name').text))  # appends to the output string in the result object

            if result.find('Text') is not None:
                outcome.set_text(result.find("Text").text)

            if result.findall('Trait') is not None:  # checks if the result gives you access to any traits
                for trait in result.findall('Trait'):
                    outcome.add_trait(trait.text, trait.attrib["type"])   # adds the trait as a dictionary with the
                    # value being the trait type (Could be done better with a Trait class perhaps)

            if 'hasExtraRoll' in result.attrib:  # checks if the result requires any extra rolls
                extra_rolls = result.findall('ExtraRoll')
                for extra_roll in extra_rolls:
                    table_source = extra_roll.find('Source').text  # pulls location of the necessary table for the
                    # extra roll

                    if table_source == "Local":  # local tables are located within the result itself

                        table_source = extra_roll.find('Table')
                    else:
                        table_source = root.find(table_source)  # if not local, the result will include the full path
                        # to the table

                    outcome.extra_roll(table_roll(table_source))

            if 'CP' in result.attrib:
                outcome.add_cp(int(result.attrib['CP']))


            number_of_siblings += outcome.get_num_siblings()  # Takes any addition to sibling count and adds it to
            # the overall total
            break

    return outcome


def roll_homeland(race=test_race):

    return table_roll(races.find('%s/Homeland' % race)).get_return_string()


def roll_parents(race=test_race):
    return table_roll(races.find('%s/Parents' % race)).get_return_string()


def roll_circumstance_of_birth():
    data = table_roll(root.find('MiscTables/Circumstances_Of_Birth'))
    return data.get_return_string() + '\n' + data.get_text()


def roll_major_childhood_event():
    data = table_roll(root.find('MiscTables/Major_Childhood_Event'))
    return data.get_return_string() + "\n" + data.get_text()


def roll_class_background(chosen_class):
    data = table_roll(classes.find(chosen_class))
    return data.get_return_string() + "\n" + data.get_text()


def roll_crime():
    data = table_roll(root.find('MiscTables/Crime'))
    return data.get_return_string()


def roll_punishment():
    data = table_roll(root.find('MiscTables/Punishment'))
    return data.get_return_string()


def roll_influential_associates():
    data = table_roll(root.find('MiscTables/Influential_Associates'))
    return data.get_return_string() + "\n" + data.get_text()


def print_traits():
    return_string = "You gain access to the following traits: \n"
    for trait in traits:
        if traits[trait] != 'Special':
            return_string += trait + "("+traits[trait]+") \n"
    return return_string


def roll_parents_profession():
    return_string = ""

    if 'Lower-Class' in traits:
        return_string += table_roll(root.find('MiscTables/d20_Parents_Profession')).get_return_string()
    else:
        return_string += table_roll(root.find('MiscTables/Parents_Profession')).get_return_string()
    if 'Adopted' in traits:
        traits.pop('Adopted')
        return_string += "\n Adopted Parent's Profession: \n" + roll_parents_profession()

    return return_string


def roll_siblings(race=test_race):
    global number_of_siblings
    num_older = 0
    num_younger = 0
    is_twin = False
    is_triplet = False

    data = table_roll(races.find('%s/Siblings' % race))
    return_string = ""
    if number_of_siblings >= 2:
        traits['Kin Guardian'] = 'Combat'  # adds the Kin Guardian combat trait if you have more than 1 sibling
    if number_of_siblings != 0:
        for sibling in range(0, number_of_siblings):
            result = table_roll(root.find('MiscTables/Relative_Age_Sibling')).get_return_string()
            if 'Older' in str(result):
                num_older += 1
            if 'Younger' in str(result):
                num_younger += 1
            if 'Twins' in str(result):
                if is_twin:
                    is_triplet = True
                else:
                    is_twin = True
    return_string += data.get_return_string() + "\n"

    relative_string = ""
    if num_older == num_younger:
        relative_string += "You're the middle child"
        return return_string + relative_string
    if num_older != 0:
        relative_string += "\n" + "You're younger than " + str(num_older) + " sibling(s) \n"
    else:
         relative_string += "\n You're the eldest sibling \n"
    if num_younger != 0:
        relative_string += "\n" + "You're older than " + str(num_younger) + " sibling(s) \n"
    else:
        relative_string += "\n You're the youngest sibling"
    if is_twin:
        if is_triplet:
            relative_string += "\n You are part of triplets"
        else:
            relative_string += "\n You have a twin"
    return_string += relative_string

    return return_string

def roll_conflict():
    total_CP = 0
    conflict = table_roll(root.find('MiscTables/Conflicts'))
    total_CP += conflict.get_cp()
    subject = table_roll(root.find('MiscTables/Conflict_Subject'))
    total_CP += subject.get_cp()
    motivation = table_roll(root.find('MiscTables/Conflict_Motivation'))
    total_CP += motivation.get_cp()

    return_string = conflict.get_return_string() + "  (CP: " + str(conflict.get_cp()) + ")\n"\
        + "Subject: \n" \
        + subject.get_return_string() + "  (CP:" + str(subject.get_cp()) + ")\n"\
        + "Motivation: \n" \
        + motivation.get_return_string() + " (CP:" + str(motivation.get_cp()) + ")\n" \
        + "Total Conflict Points: " + str(total_CP)
    return return_string


def roll_romantic_relationships():
    if 'd12_Romantic' in traits:
        data = table_roll(root.find('MiscTables/d12_Romantic_Relationships'))
    else:
        data = table_roll(root.find('MiscTables/Romantic_Relationships'))
    return data.get_return_string() + "\n" + data.get_text()


def roll_drawback():
    data = table_roll(root.find('MiscTables/Character_Drawback'))
    return data.get_return_string() + "\n" + data.get_text()


def roll_background(race): # Function returns the entire background in one large string so it can be easily sent
    global number_of_siblings
    return_string = ""
    traits.clear()
    number_of_siblings = 0
    return_string += "Race: " + race + "\n" \
           + "Homeland: " + "\n" \
           + roll_homeland(race) + "\n \n" \
           + "Parents: " + "\n" \
           + roll_parents(race) + "\n \n" \
           + "Siblings: " + "\n" \
           + roll_siblings(race) + "\n \n" \
           + "Circumstance of Birth: " + "\n" \
           + roll_circumstance_of_birth() + "\n \n" \
           + "Parent's Profession: " + "\n" \
           + roll_parents_profession() + "\n." \

    return return_string



def roll_background_2(chosen_class):
    return_string = ""
    "Major Childhood Event: " + "\n" \
    + roll_major_childhood_event() + "\n \n"
    return_string += "Class: " + chosen_class + "\n" \
                     + roll_class_background(chosen_class) + "\n \n"
    if "Criminal" in traits:
        return_string += "Crime: " + "\n" + roll_crime() + "\n" \
                                                           "Punishment: " + "\n" \
                         + roll_punishment() + "\n"
    return_string += "Your Influential Associate: \n" + \
                     roll_influential_associates() + "\n \n" \
                     + "Conflict: " + "\n" \
                     + roll_conflict() + "\n \n" \
                     + "Romantic Relationships: \n" \
                     + roll_romantic_relationships() + "\n \n" \
                     + "Character Drawback:  \n" \
                     + roll_drawback() + "\n \n" \
                     + print_traits()
    return return_string

class Result:

    def __init__(self):
        self.return_string = ""
        self.num_siblings = 0
        self.cp = 0
        self.traits = dict()
        self.text = ""

    def add_cp(self, CP):
        self.cp += CP

    def get_cp(self):
        return self.cp

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

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
        self.text = result.text


client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user.display_name} has connected to ' + str(client.guilds))

    channel = discord.utils.get(client.get_all_channels(), name="roll-dice")
    await channel.send("Hello! " + client.user.mention + " is now taking requests!")


@client.event
async def on_message(message):
    user = message.author
    race_found = False
    class_found = False

    if user == client.user:
        return
    if '/background' in message.content:
        chosen_race = ""
        chosen_class = ""
        for race in list_of_half_races:
            if race.lower() in message.content.lower():
                chosen_race = race
                race_found = True
        if not race_found:
            for race in list_of_races:
                if race.lower() in message.content.lower():
                    chosen_race = race
                    race_found = True
        for player_class in list_of_classes:
            if player_class.lower() in message.content.lower():
                chosen_class = player_class
                class_found = True

        if not race_found or not class_found:
            await message.channel.send(user.mention + ", You are missing information. You need include a race and a class.")
            return
        await message.channel.send(user.mention + "'s Background\n" + roll_background(chosen_race))
        await message.channel.send("\n \n" + roll_background_2(chosen_class))


def run_bot():

    client.run(TOKEN)

run_bot()
