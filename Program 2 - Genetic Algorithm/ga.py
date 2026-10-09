import sys
import subprocess
import time
import json

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

def fitness():
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

  log(f'Time: {time.perf_counter() - start_time}')
