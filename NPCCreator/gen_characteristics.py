#!/bin/python

CHARACTERISTIC_BLOCKS = [
  [2, 2, 2, 2, 1, 1, -1, -3],
  [3, 2, 2, 1, 1, 0, -1, -3],
  [3, 3, 1, 1, 0, -1, -2, -2],
  [3, 2, 2, 1, -1, -1, -1, -2],
  [2, 2, 2, 2, 1, 0, -2, -2],
  [3, 3, 0, 0, 0, -1, -1, -2],
  [2, 2, 2, 1, 0, 0, 0, -2],
  [3, 1, 1, 0, 0, 0, 0, -1],
]

CHARACTERISTICS = {
  "Intelligence" : 0,
  "Perception" : 0,
  "Strength" : 0,
  "Stamina" : 0,
  "Presence" : 0,
  "Communication" : 0,
  "Dexterity" : 0,
  "Quickness" : 0,
}

def generate_characteristics():
  import random
  these_characteristics = CHARACTERISTIC_BLOCKS[random.randint(0, len(CHARACTERISTIC_BLOCKS) - 1)].copy()
  random.shuffle(these_characteristics)
  for key in CHARACTERISTICS.keys():
    CHARACTERISTICS[key] = these_characteristics.pop()

  return CHARACTERISTICS
