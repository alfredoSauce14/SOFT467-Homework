import sys
import subprocess
import time
import json
import random
import string

# JSON info:
# Keys: always strings
# Values:
#   - Strings
#     - Any length but can assume < 1,000 characters
#     - Can include any printable character
#   - Integers
#     - Can be positive or negative
#     - Bound to the range [-10,000, 10,000]

def log(message):
    if logging:
        print(message, file=sys.stderr)

def read_input(path):
    with open(path) as c:
        contents = c.read()
    return contents

def chromosome(strings, values, length):
   return

def output_generation():
    output = {}
    output['done'] = False
    output['generation'] = 0
    output['evaluated'] = 0
    output['avg_fitness'] = 0
    output['best_fitness'] = 0
    if (output['done'] == True) or (output['generation'] == 0):
      output['best_individual'] = json.dumps()
    print(json.dumps(output), flush=True)

def generate_chromosome():
   chromosome = {}
   i = 0
   length = random.randint(0,10)
   while i < length:
      k = 0
      key_length = random.randint(1,100)
      key = ""
      while k < key_length:
         key += random.choice(string.printable)
         k += 1
      value_type = random.randint(1, 2)
      log(f'Value type at {i}: {value_type}\n')
      if value_type == 1:
         v = 0
         value_length = random.randint(1,100)
         value = ""
         while v < value_length:
            value += random.choice(string.printable)
            v += 1
      else:
         value = random.randint(-10000, 10000)
      chromosome[key] = value
      log(f'{i}th part of Chromosome: {chromosome[key]}\n')
      log(f'Chromosome at {i}: {chromosome}\n')
      i += 1          
   return chromosome

def create_population(size):
   population = []
   i = 0
   while i < size:
      population.append(generate_chromosome())
   return population

def crossover_chromosomes():
   return

def mutate_chromosomes():
  # roulette wheel (assign each a probability to be picked, higher the more fit they are, and select from there)
  # tournament style (select random to be in tournament and take best of those)
   return

def fitness():
    return

def evolve_match():
   return



if __name__ == "__main__":
  start_time = time.perf_counter() 

  if len(sys.argv) < 2 or len(sys.argv) > 3:
    sys.exit("usage: ga.py input_file [-log]")

  if len(sys.argv) == 3:
    if sys.argv[2] == "-log":
      logging = True
    else:
      sys.exit("usage: dd.py input_file oracle_script [-log]")
  else:
    logging = False

  log(f'logging: {logging}')

  input_file = sys.argv[1]

  log(f'input_file: {input_file}')


  #Tests:
  test_chromosome = generate_chromosome()
  log(f'Test Chromosome: {test_chromosome}\n')


  log(f'Time: {time.perf_counter() - start_time}')
