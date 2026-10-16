import sys
import time
import json
import random
import string
import math
from rapidfuzz.distance import Levenshtein

def log(message):
    if logging:
        print(message, file=sys.stderr)

def output_generation(done, generation, evaluated, avg_fitness, best_fitness, best_individual):
    output = {}
    output['done'] = done
    output['generation'] = generation
    output['evaluated'] = evaluated
    output['avg_fitness'] = avg_fitness
    output['best_fitness'] = best_fitness
    if (done == True) or (generation == 0):
      output['best_individual'] = json.dumps(best_individual)
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
            if value1 == value2:
               offspring[key] = value1
            else:
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
   integer_mutation_type = random.choice(['small nudge', 'small nudge', 'large nudge', 'random reset'])
   
   if integer_mutation_type == 'small nudge':
      n += random.randint(-10, 10)

   if integer_mutation_type == 'large nudge':
       n += random.randint(-100, 100)

   if integer_mutation_type == 'random reset':
      n = random.randint(-10000, 10000)

   return max(-10000, min(10000, n))

def mutate_chromosome(chromosome):
   mutated = dict(chromosome)
   if len(mutated) > 1:
    mutation_probability = 1.0 / len(mutated) / 2
   else: mutation_probability = 0.5

   # Add gene
   if random.random() < 0.1  :
      new_key, new_value = generate_gene()
      if new_key not in mutated:
        mutated[new_key] = new_value

   # Delete gene
   if random.random() < 0.1 and mutated:
      del mutated[random.choice(list(mutated))]

   # Gene mutations
   for key in list(mutated):
      if random.random() < mutation_probability:
         mutation_type = random.choice(['key', 'key', 'value', 'value', 'switch_value_type'])
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

         if mutation_type == 'switch_value_type':
            if isinstance(value, str):
               mutated[key] = random.randint(-10000, 10000)
            else:
               value_length = random.randint(0, 10)
               mutated[key] = random_printable_string(value_length)
  
   return mutated


def find_fitness(chromosome, target_file):
   # Only reads target file on the first call and then caches the target
   if not hasattr(find_fitness, "target"):
      with open(target_file) as f:
         find_fitness.target = json.loads(f.read())
   target = find_fitness.target

   fitness = 0

   missing_keys = []
   extra_keys = []
   keys_in_both = []

   for key in set(chromosome) | set(target):
      if key not in chromosome:
         missing_keys.append(key)
      elif key not in target:
         extra_keys.append(key)
      else:
         keys_in_both.append(key)

   fitness += (abs(len(missing_keys) - len(extra_keys)) * 1000)

   paired_keys = []
   paired_keys_candidates = []

   for chromosome_key in extra_keys:
      for target_key in missing_keys:
         paired_keys_candidates.append((Levenshtein.distance(target_key, chromosome_key), chromosome_key, target_key))
   paired_keys_candidates.sort()

   used_chromosome_keys = set()
   used_target_keys = set()
   
   for distance, chromosome_key, target_key in paired_keys_candidates:
      if chromosome_key not in used_chromosome_keys and target_key not in used_target_keys:
        used_chromosome_keys.add(chromosome_key)
        used_target_keys.add(target_key)
        fitness += distance
        paired_keys.append((chromosome_key, target_key))

   for key in keys_in_both:
      paired_keys.append((key, key))

   for chromosome_key, target_key in paired_keys:
      chromosome_value = chromosome[chromosome_key]
      target_value = target[target_key]
      distance = 0
      if isinstance(chromosome_value, str) and isinstance(target_value, str):
          distance = Levenshtein.distance(target_value, chromosome_value)
      elif isinstance(chromosome_value, str) or isinstance(target_value, str):
          distance = 1000
      else:
          distance = math.ceil(abs(chromosome_value - target_value) / 30)
      fitness += distance
      
   return fitness

def evolve_match(target_file):
   population_size = 120

   initial_population = create_population(population_size)

   population = initial_population[:]
   done = False
   generation = 0
   fitness_cache = {}

   while not done:
      chromosome_fitness_pairs = []
      total_fitness = 0
      best_fitness = math.inf
      elite_chromosomes = []

      for chromosome in population:
          cache_key = json.dumps(chromosome, sort_keys=True)
          if cache_key not in fitness_cache:
            fitness_cache[cache_key] = find_fitness(chromosome, target_file)
          fitness = fitness_cache[cache_key]
          
          total_fitness += fitness
          
          if fitness == 0:
            done = True
          
          if fitness < best_fitness:
             best_fitness = fitness
             best_individual = chromosome

          chromosome_fitness_pair = (chromosome, fitness)

          if len(elite_chromosomes) < 5:
             elite_chromosomes.append(chromosome_fitness_pair)
          elif fitness < elite_chromosomes[4][1]:
             elite_chromosomes[4] = chromosome_fitness_pair
             elite_chromosomes.sort(key=lambda x: x[1])
          
          chromosome_fitness_pairs.append(chromosome_fitness_pair)

      evaluated = len(fitness_cache)
      avg_fitness = total_fitness / population_size

      if (time.perf_counter() - start_time) > 170:
        done = True
      
      if (generation % 50) == 0 or done:
        output_generation(done, generation, evaluated, avg_fitness, best_fitness, best_individual)

      if done:
         break

      generation += 1

      # Chromosome crossover
      tournament_attendees = random.sample(chromosome_fitness_pairs, k=(population_size // 2))
      tournament_attendees.sort(key=lambda x: x[1])
      chosen_parents = []
      for attendee in tournament_attendees[:(population_size // 4)]:
         chosen_parents.append(attendee[0])

      offsprings = []
      o = 0
      while o < (population_size-5):
         parent1 = random.choice(chosen_parents)
         parent2 = random.choice(chosen_parents)
         offspring = crossover_chromosomes(parent1, parent2)
         offsprings.append(offspring)
         o += 1

      mutated_offsprings = []
      for offspring in offsprings:
         mutated = mutate_chromosome(offspring)
         mutated_offsprings.append(mutated)

      population = mutated_offsprings
      for elite in elite_chromosomes:
        population.append(elite[0])     


if __name__ == "__main__":
  start_time = time.perf_counter() 

  if len(sys.argv) < 2 or len(sys.argv) > 3:
    sys.exit("usage: ga.py target_file [-log]")

  if len(sys.argv) == 3:
    if sys.argv[2] == "-log":
      logging = True
    else:
      sys.exit("usage: dd.py target_file [-log]")
  else:
    logging = False

  log(f'logging: {logging}')

  target_file = sys.argv[1]
  log(f'target_file: {target_file}')

  evolve_match(target_file)

  #Tests:
 

  log(f'Time: {time.perf_counter() - start_time}')
