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
    '--specialization',
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
  def __init__(self, variant="grog", age=25, specialization=None):
    self.variant = variant
    self.age = age
    self.specialization = specialization
    self.abilities = {}
    self.characteristics = {}
    self.primary_ability = None
    self.secondary_abilities = {}

  def randomize_abilities(abilities):
    import random
    from collections import defaultdict
    if type(abilities) == dict or type(abilities) == defaultdict:
      abilities = list(abilities.keys())

    return random.choice(abilities)

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
    primary_ability = self.set_primary_ability()
    self.primary_ability = primary_ability
    secondary_abilities = self.set_secondary_abilities()
    self.secondary_abilities = secondary_abilities

    current_abilities = self.abilities.copy()
    current_abilities[primary_ability]  # <-- Ensures priamry_ability is in current_abilities
    current_abilities.update(secondary_abilities)
    base_ability_count = len(current_abilities.keys())

    for i in range(5, self.age):
      current_ability_count = len(current_abilities.keys())
      # FIXME: Check the EXP requirements for level 7 ability
      if current_abilities[primary_ability] < 150:
        current_abilities[primary_ability] += 5
      else:
        current_abilities[NPC.randomize_abilities(current_abilities)] += 5

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
    if self.variant == "grog":
      if self.specialization not in MARTIAL_ABILITIES:
        weapon_choice = NPC.randomize_abilities(MARTIAL_ABILITIES)
        return weapon_choice
      else:
        return self.specialization
    elif self.variant == "noble":
      if self.specialization:
        return self.specialization
      else:
        return NPC.randomize_abilities(SOCIAL_ABILITIES)
    elif self.variant == "covenfolk":
      if self.specialization:
        return self.specialization
      else:
        return None
    elif self.variant == "specialist":
      if self.specialization:
        return self.specialization
      else:
        return NPC.randomize_abilities(PROFESSIONAL_ABILITIES)
    else:
      return NPC.randomize_abilities(GENERAL_ABILITIES)

  def set_secondary_abilities(self):
    secondaries = {}
    if self.variant == "grog":
      # Give grogs some combat abilities
      while len(secondaries.keys()) < 3:
        this_ability = NPC.randomize_abilities(SURVIVAL_ABILITIES)
        if this_ability != self.primary_ability:
          secondaries[this_ability] = 0

      while len(secondaries.keys()) < 5:
        this_ability = NPC.randomize_abilities(SOCIAL_ABILITIES)
        if this_ability != self.primary_ability:
          secondaries[this_ability] = 0

      return secondaries


def main():
  args = vars(gen_options().parse_args())
  new_npc = NPC(**args)
  new_npc.abilities = new_npc.gen_early_abilities()
  new_npc.characteristics = NPC.gen_characteristics()
  if new_npc.age > 5:
    new_npc.abilities = new_npc.gen_later_abilities()
  print("NPC Type:", new_npc.variant)
  print("NPC Age:", new_npc.age)
  print("NPC Characteristics:", new_npc.characteristics)
  print("NPC Abilities:", new_npc.abilities)

  return new_npc

if __name__ == '__main__':
  exit(main())


@app.route('/')
def gen_index():
    variants = ['turb', 'grog', 'noble', 'specialized', 'covenfolk']
    ages = list(range(5, 71))
    specialties = ALL_ABILITIES
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
  specialization = request.form.get('specialty')
  #return str(variant), str(age), str(specialty)
  #return str(variant)
  #return "Age: " + str(age) + "\nVariant: " + str(variant)
  new_npc = NPC(variant=variant, age=age, specialization=specialization)
  new_npc.abilities = new_npc.gen_early_abilities()
  new_npc.characteristics = NPC.gen_characteristics()
  if new_npc.age > 5:
    new_npc.abilities = new_npc.gen_later_abilities()
  #print("NPC Type:", new_npc.variant)
  #print("NPC Age:", new_npc.age)
  #print("NPC Characteristics:", new_npc.characteristics)
  #print("NPC Abilities:", new_npc.abilities)
  return vars(new_npc)

@app.route('/random/npc/')
def randomized_npc():
  import random
  #npc_variant = ['turb', 'grog', 'noble', 'specialized', 'covenfolk']
  npc_variant = ['grog']
  new_npc = NPC(variant=random.choice(npc_variant), age=random.randint(5, 45), specialization=None)
  new_npc.abilities = new_npc.gen_early_abilities()
  new_npc.characteristics = NPC.gen_characteristics()
  if new_npc.age > 5:
    new_npc.abilities = new_npc.gen_later_abilities()
  print("NPC Type:", new_npc.variant)
  print("NPC Age:", new_npc.age)
  print("NPC Characteristics:", new_npc.characteristics)
  print("NPC Abilities:", new_npc.abilities)
  return vars(new_npc)
