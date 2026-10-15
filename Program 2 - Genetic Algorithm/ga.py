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

def output_generation(done, generation, evaluated, avg_fitness, best_fitness):
    output = {}
    output['done'] = done
    output['generation'] = generation
    output['evaluated'] = evaluated
    output['avg_fitness'] = avg_fitness
    output['best_fitness'] = best_fitness
    if (done == True) or (generation == 0):
      output['best_individual'] = json.dumps()
    print(json.dumps(output), flush=True)

def random_printable_string(length):
   s = ""
   i = 0
   while i < length:
       s += random.choice(string.printable)
       i += 1
   return s
   
def generate_gene():
   key_length = random.randint(0,10)
   key = random_printable_string(key_length)
   value_type = random.choice(['string', 'integer'])
   if value_type == 'string':
     value_length = random.randint(0,10)
     value = random_printable_string(value_length)
   else:
     value = random.randint(-10000, 10000)
   return key, value

def generate_chromosome():
   chromosome = {}
   i = 0
   length = random.randint(0,10)
   while i < length:
      key, value = generate_gene()
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
      i += 1
   return population

def crossover_chromosomes(parent1, parent2):
   offspring = {}
   for key in set(parent1) | set(parent2):
      parent1_key = key in parent1
      parent2_key = key in parent2
      if parent1_key and parent2_key:
         value1 = parent1[key]
         value2 = parent2[key]
         if isinstance(value1, str) and isinstance(value2, str):
            split1 = random.randint(0, len(value1))
            split2 = random.randint(0, len(value2))
            offspring[key] = value1[:split1] + value2[split2:]
            offspring[key] = (offspring[key])[:1000]
         else:
            offspring[key] = random.choice([value1, value2])
      else:
         if random.random() < 0.5:
            if parent1_key:
               offspring[key] = parent1[key]
            else:
               offspring[key] = parent2[key]
   return offspring

def mutate_string(s):
   string_mutation_type = random.choice(['substitution', 'insertion', 'deletion'])
   if not s:
      string_mutation_type = 'insertion'
   
   if string_mutation_type == 'substitution':
      mutation_pos = random.randrange(len(s))
      s = s[:mutation_pos] + random.choice(string.printable) + s[mutation_pos+1:]

   if string_mutation_type == 'insertion':
      mutation_pos = random.randint(0, len(s))
      s = s[:mutation_pos] + random.choice(string.printable) + s[mutation_pos:]

   if string_mutation_type == 'deletion':
      mutation_pos = random.randrange(len(s))
      s = s[:mutation_pos] + s[mutation_pos+1:]
      
   return s[:1000]

def mutate_integer(n):
   n += random.randint(-10, 10)
   return max(-10000, min(10000, n))

def mutate_chromosome(chromosome):
   mutated = dict(chromosome)
   if len(mutated) > 1:
    mutation_probability = 1.0 / len(mutated)
   else: mutation_probability = 0.5

   # Add gene
   if random.random() < 0.3:
      new_key, new_value = generate_gene()
      mutated[new_key] = new_value

   # Delete gene
   if random.random() < 0.3 and mutated:
      del mutated[random.choice(list(mutated))]

   # Gene mutations
   for key in list(mutated):
      if random.random() < mutation_probability:
         mutation_type = random.choice(['key', 'value'])
         value = mutated[key]

         if mutation_type == 'key':
            new_key = mutate_string(key)
            if new_key not in mutated:
               del mutated[key]
               mutated[new_key] = value

         if mutation_type == 'value':
            if isinstance(value, str):
               mutated[key] = mutate_string(value)
            else:
               mutated[key] = mutate_integer(value)
         

  #  mutated = chromosome[:]
  #  mutation_probability = 1.0 / len(mutated)
  #  for key in set(mutated):
  #     if random.random() < 
   return mutated

def fitness():
    # roulette wheel (assign each a probability to be picked, higher the more fit they are, and select from there)
    # tournament style (select random to be in tournament and take best of those)
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
      sys.exit("usage: dd.py input_file [-log]")
  else:
    logging = False

  log(f'logging: {logging}')

  input_file = sys.argv[1]

  log(f'input_file: {input_file}')


  #Tests:
  test_chromosome = generate_chromosome()
  log(f'Test Chromosome: {test_chromosome}\n')

  # parent_1 = generate_chromosome()
  # parent_2 = generate_chromosome()
  # offspring = crossover_chromosomes(parent_1, parent_2)
  # log(f'parent_1: {parent_1}')
  # log(f'parent_2: {parent_2}')
  # log(f'offspring_1: {offspring}')

  mutated_chromosome = mutate_chromosome(test_chromosome)
  log(f'Mutated Chromosome: {mutated_chromosome}')


  log(f'Time: {time.perf_counter() - start_time}')
