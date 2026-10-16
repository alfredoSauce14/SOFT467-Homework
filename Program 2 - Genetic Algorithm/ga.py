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
    mutation_probability = 1.0 / len(mutated)
   else: mutation_probability = 0.5

   # Add gene
   if random.random() < 0.3:
      new_key, new_value = generate_gene()
      if new_key not in mutated:
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

   if missing_keys and extra_keys:
      for chromosome_key in extra_keys:
          lowest_levenshtein_distance = math.inf
          for target_key in missing_keys:
             levenshtein_distance = Levenshtein.distance(target_key, chromosome_key)
             if levenshtein_distance < lowest_levenshtein_distance:
                lowest_levenshtein_distance = levenshtein_distance
                paired_key = target_key
          fitness += lowest_levenshtein_distance
          paired_keys.append((chromosome_key, paired_key))

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
   # roulette wheel (assign each a probability to be picked, higher the more fit they are, and select from there)
   # tournament style (select random to be in tournament and take best of those)

   # population size must be factor of 4
   population_size_factor = 30
   population_size = 4 * population_size_factor   # 120

   initial_population = create_population(population_size)

   population = initial_population[:]
   done = False
   generation = 0
   chromosomes_evaluated = []

   while not done:
      chromosome_fitness_pairs = []
      total_fitness = 0
      # avg_fitness = 0
      best_fitness = math.inf
      # best_individual = {}

      for chromosome in population:
          if chromosome not in chromosomes_evaluated:
             chromosomes_evaluated.append(chromosome)
          fitness = find_fitness(chromosome, target_file)
          total_fitness += fitness
          if fitness == 0:
            done = True
          if fitness < best_fitness:
             best_fitness = fitness
             best_individual = chromosome
          chromosome_fitness_pairs.append((chromosome, fitness))

      evaluated = len(chromosomes_evaluated)
      avg_fitness = total_fitness / population_size

      if (time.perf_counter() - start_time) > 180:
        done = True
      
      if (generation % 50) == 0 or done:
        output_generation(done, generation, evaluated, avg_fitness, best_fitness, best_individual)

      generation += 1

      # Chromosome crossover
      tournament_attendees = random.choices(chromosome_fitness_pairs, k=((population_size * 3) // 2))
      chosen_parents = []
      total_tournament_fitness = 0
      for attendee in tournament_attendees: total_tournament_fitness += attendee[1]
      avg_tournament_fitness = total_tournament_fitness / (population_size / 2)
      for attendee in tournament_attendees:
         if attendee[1] <= avg_tournament_fitness:
            chosen_parents.append(attendee[0])

      offsprings = []
      o = 0
      while o < (population_size-1):
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
      population.append(best_individual)     


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
  # test_chromosome = generate_chromosome()
  # log(f'Test Chromosome: {test_chromosome}\n')

  # mutated_chromosome = mutate_chromosome(test_chromosome)
  # log(f'Mutated Chromosome: {mutated_chromosome}')

  # parent_1 = generate_chromosome()
  # parent_2 = generate_chromosome()
  # offspring = crossover_chromosomes(parent_1, parent_2)
  # log(f'parent_1: {parent_1}')
  # log(f'parent_2: {parent_2}')
  # log(f'offspring: {offspring}')

  # mutated_offspring = mutate_chromosome(offspring)
  # log(f'Mutated Offspring: {mutated_offspring}')

  # fitness = find_fitness(test_chromosome, target_file)
  # log(f'Test Fitness: {fitness}')

  # test_chromosome_1 = {'nam': 'Robt', 'age': 78}
  # test_chromosome_2 = {'binu': 'Barukd', 'age': 21, 'city': 'Lincoln'}
  # test_chromosome_3 = {'name': 'Robert', 'age': 21, 'city': 'Lincoln'}

  # fitness_1 = find_fitness(test_chromosome_1, target_file)
  # log(f'Test Fitness 1: {fitness_1}')
  # fitness_2 = find_fitness(test_chromosome_2, target_file)
  # log(f'Test Fitness 2: {fitness_2}')
  # fitness_3 = find_fitness(test_chromosome_3, target_file)
  # log(f'Test Fitness 3: {fitness_3}')

  log(f'Time: {time.perf_counter() - start_time}')
