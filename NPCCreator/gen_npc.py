#!/bin/python
from abilities import ACADEMIC_ABILITIES
from abilities import ALL_ABILITIES
from abilities import EARLY_LIFE_ABILITIES
from abilities import GENERAL_ABILITIES
from abilities import LATE_LIFE_ABILITIES
from abilities import MARTIAL_ABILITIES
from abilities import PROFESSIONAL_ABILITIES
from abilities import SOCIAL_ABILITIES
from abilities import SURVIVAL_ABILITIES
from flask import Flask, flash, redirect, render_template, \
     request, url_for

app = Flask(__name__)
app.debug = True

def gen_options():
  import argparse
  parser = argparse.ArgumentParser(
    description="ABC 123",
    formatter_class=argparse.RawTextHelpFormatter,
  )

  parser.add_argument(
    '--variant',
    type=str,
    default='grog',
    help='The variant of NPC. Choices are "grog", "noble", "covenfolk", "specialist".'
  )

  parser.add_argument(
    '--age',
    type=int,
    default=25,
    help='The age of this NPC. Available range is 6 and above.'
  )

  parser.add_argument(
    '--specialty',
    type=str,
    default="any",
    help='''
      The ability focus of this NPC.
      In addition to naming a specific ability, several "classes" can be specified.
      Available ability classes are: "academic", "religious", "merchant", "social", 
      For Grogs, choices are "great", "single", and "ranged".
      For Nobles, these are "Artsy", "Fartsy", and "Entitled".
      For Specialists you can choose "academic", "crafter", "professional", or "teacher".
      For Covernfolk you get what you get.
    '''
  )
  return parser


class NPC:
  def __init__(self, variant="grog", age=25, specialty=None):
    self.variant = variant
    self.age = age
    self.specialty = specialty
    self.abilities = {}
    self.characteristics = {}
    self.primary_ability = ""
    self.secondary_abilities = {}

  def randomize_abilities(abilities):
    import random
    from collections import defaultdict
    if type(abilities) == dict or type(abilities) == defaultdict:
      abilities = list(abilities.keys())

    random_ability = random.choice(abilities)

    return random_ability

  def gen_characteristics():
    from gen_characteristics import generate_characteristics
    return generate_characteristics()


  def gen_early_abilities(self):
    from collections import defaultdict
    abilities = defaultdict(int)
    abilities["Native Language"] = 75
    available_points = 45

    while available_points > 0:
      stat_to_increase = NPC.randomize_abilities(EARLY_LIFE_ABILITIES)
      while stat_to_increase == "Native Language":  # <-- Do not want Native Language to increase further
        stat_to_increase = NPC.randomize_abilities(EARLY_LIFE_ABILITIES)
      abilities[stat_to_increase] += 5
      available_points -= 5

    return abilities


  def gen_later_abilities(self):
    self.primary_ability = self.set_primary_ability()
    primary_ability = self.primary_ability
    self.secondary_abilities = self.set_secondary_abilities()
    secondary_abilities = self.secondary_abilities

    current_abilities = self.abilities.copy()
    current_abilities[self.primary_ability]  # <-- Ensures primary_ability is in current_abilities
    current_abilities.update(secondary_abilities)
    base_ability_count = len(current_abilities.keys())

    for i in range(5, self.age):
      current_ability_count = len(current_abilities.keys())
      # FIXME: Check the EXP requirements for level 7 ability
      if primary_ability:
        if current_abilities[primary_ability] < 150:
          import random
          # Give primary ability exp 80% of the time
          if random.randint(0, 5) < 4:
              current_abilities[primary_ability] += 5
          else:
            current_abilities[NPC.randomize_abilities(secondary_abilities)] += 5
        else:
          current_abilities[NPC.randomize_abilities(current_abilities)] += 5
      # For NPCs with no "primary" ability
      else:
        current_abilities[NPC.randomize_abilities(secondary_abilities)] += 5

      # Give the character's secondary abilities +5 exp
      current_abilities[NPC.randomize_abilities(secondary_abilities)] += 5

      # Randomly give one of any of the character's abilities +5 exp
      ability_to_raise = NPC.randomize_abilities(current_abilities)
      if ability_to_raise == "Native Language":
        ability_to_raise = NPC.randomize_abilities(current_abilities)  # <-- Make Native Language a rarer roll
      current_abilities[NPC.randomize_abilities(current_abilities)] += 5

      # Add a new ability to the general abilities every 10 years, starting at 21
      if (i / 10) > (current_ability_count - base_ability_count + 2):
        new_ability = NPC.randomize_abilities(GENERAL_ABILITIES)
        # Ensure the new ability is actually new
        while new_ability in current_abilities.keys():
          new_ability = NPC.randomize_abilities(GENERAL_ABILITIES)

        current_abilities[new_ability]

    return current_abilities

  def set_primary_ability(self):
    if self.specialty != None:
      return self.specialty

    if self.variant == "grog":
      return NPC.randomize_abilities(MARTIAL_ABILITIES)
    elif self.variant == "noble":
      return NPC.randomize_abilities(SOCIAL_ABILITIES)
    elif self.variant == "covenfolk":
      return None
    elif self.variant == "specialist":
      return NPC.randomize_abilities(PROFESSIONAL_ABILITIES)
    else:
      # Should not actually ever be used
      return NPC.randomize_abilities(GENERAL_ABILITIES)

  def set_secondary_abilities(self):
    secondaries = {}
    number_of_secondaries = 0
    secondary_selection = None
    tertiary_selection = None

    if self.variant == "grog":
      number_of_secondaries = 3
      secondary_selection = SURVIVAL_ABILITIES
      tertiary_selection = SOCIAL_ABILITIES
      if self.specialty != None:
        if self.specialty not in MARTIAL_ABILITIES:
          secondaries[NPC.randomize_abilities(MARTIAL_ABILITIES)] = 0
    elif self.variant == "noble":
      number_of_secondaries = 4
      secondary_selection = SOCIAL_ABILITIES
      tertiary_selection = GENERAL_ABILITIES
    elif self.variant == "specialist":
      number_of_secondaries = 3
      secondary_selection = PROFESSIONAL_ABILITIES
      tertiary_selection = GENERAL_ABILITIES
    elif self.variant == "covenfolk":
      number_of_secondaries = 5
      secondary_selection = GENERAL_ABILITIES
      tertiary_selection = SOCIAL_ABILITIES

    while len(secondaries.keys()) < number_of_secondaries:
      this_ability = NPC.randomize_abilities(secondary_selection)
      if this_ability != self.primary_ability:
        secondaries[this_ability] = 0

    while len(secondaries.keys()) < (number_of_secondaries + 2):
      this_ability = NPC.randomize_abilities(tertiary_selection)
      if this_ability not in secondaries.keys():
        secondaries[this_ability] = 0

    return secondaries

  def gen_ability_levels(self):
    from math import sqrt, floor
    abilities = self.abilities.copy()
    for ability in abilities:
      ability_exp = abilities[ability]
      ability_level = floor((sqrt(8 * (ability_exp / 5) + 1) - 1) / 2)
      abilities[ability] = {'exp': ability_exp, 'level': ability_level}

    return abilities

  def gen_useful_data(self):
    abilities = self.abilities.copy()
    if "brawl" in abilities.keys():
      abilities["brawl"]["calculations"] = 1234


def create_npc(variant, age, specialty=None):
  new_npc = NPC(variant, age, specialty)
  new_npc.abilities = new_npc.gen_early_abilities()
  new_npc.characteristics = NPC.gen_characteristics()
  if new_npc.age > 5:
    new_npc.abilities = new_npc.gen_later_abilities()
  new_npc.abilities = new_npc.gen_ability_levels()
  # TODO: Return to this later
  #new_npc.abilities = new_npc.gen_useful_data()
  return new_npc


def main():
  args = vars(gen_options().parse_args())
  new_npc = create_npc(**args)
  return new_npc

if __name__ == '__main__':
  exit(main())


@app.route('/')
def gen_index():
    variants = ['grog', 'noble', 'specialist', 'covenfolk']
    ages = list(range(5, 71))
    specialties = sorted(ALL_ABILITIES)
    return render_template(
      'gen_npc.html',
      # FIXME: Figure out how to properly pass lists through Flask
      variants=[{'variant': variant} for variant in variants],
      ages=[{'age': age} for age in ages],
      specialties=[{'specialty': specialty} for specialty in specialties],
    )

@app.route('/random/generated_npc', methods=['GET', 'POST'])
def generated_npc():
  variant = request.form.get('variant')
  age = int(request.form.get('age'))
  specialty = request.form.get('specialty')
  if specialty == "None":
    specialty = None
  new_npc = create_npc(variant, age, specialty)
  return render_template(
    'show_npc.html',
    npc=new_npc,
    abilities=new_npc.abilities
  )

@app.route('/random/npc/')
def randomized_npc():
  import random
  variant = random.choice(['grog', 'noble', 'specialist', 'covenfolk'])
  new_npc = create_npc(variant, random.randint(5, 70))
  return render_template(
    'show_npc.html',
    npc=new_npc,
    abilities=new_npc.abilities
  )
