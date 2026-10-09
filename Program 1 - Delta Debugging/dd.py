import sys
import subprocess
import time
import json


def log(message):
    if logging:
        print(message, file=sys.stderr)

def read_input(path):
    with open(path) as c:
        contents = c.read()
    return contents

def split_lines(contents):
    lines = contents.splitlines(True)
    return lines

def split_characters(contents):
    characters = list(contents)
    return characters

def run_script(input, script, newline_count=None):
    if newline_count is not None:
        if "".join(input).count("\n") != newline_count:
            return 1

    with open("candidate.txt", "w") as c:
        c.write("".join(input))
    process = subprocess.run(
        ["bash", script, "candidate.txt"],
        capture_output=True,
        text=True
    )
    interesting = process.returncode
    return interesting


def delta_debug(input, script, phase, newline_count=None):
    variants = 1
    log(f'Phase: {phase}, Granularity: N/A, Index: N/A, Segment: {input}, Variants: {variants}')

    interesting = run_script(input, script, newline_count)

    if interesting != 0:
        return input, variants

    tested = {}
    granularity = 2

    while len(input) >= 2:
        if granularity > len(input):
            granularity = len(input)
        reduced = False

        if granularity == 2:
            i = 0
            while i < granularity and (reduced == False):
                start = i * len(input) // granularity
                end = (i + 1) * len(input) // granularity
                subset = input[start:end]
                key = "".join(subset)

                if key in tested:
                    interesting = tested[key]
                else:
                    variants += 1
                    log(f'Phase: {phase}, Granularity: {granularity}, Index: Subset{i}, Segment: {subset}, Variants: {variants}')
                    interesting = run_script(subset, script, newline_count)
                    tested[key] = interesting

                if interesting == 0:
                    input = subset
                    granularity = 2
                    reduced = True
                else:
                    i += 1

        else:
            j = 0
            while j < granularity and (reduced == False):
                start = j * len(input) // granularity
                end = (j + 1) * len(input) // granularity
                complement = input[:start] + input[end:]
                key = "".join(complement)

                if key in tested:
                    interesting = tested[key]
                else:
                    variants += 1
                    log(f'Phase: {phase}, Granularity: {granularity}, Index: Complement{j}, Segment: {complement}, Variants: {variants}')
                    interesting = run_script(complement, script, newline_count)
                    tested[key] = interesting

                if interesting == 0:
                    input = complement
                    granularity = max((granularity-1), 2)
                    reduced = True
                else:
                    j += 1

        if reduced == False:
            if granularity == len(input):
                return input, variants
            else:
                granularity = min(len(input), granularity*2)

    return input, variants


if __name__ == "__main__":
    start_time = time.perf_counter()

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        sys.exit("usage: dd.py input_file oracle_script [-log]")

    if len(sys.argv) == 4:
        if sys.argv[3] == "-log":
            logging = True
        else:
            sys.exit("usage: dd.py input_file oracle_script [-log]")
    else:
        logging = False

    log(f'logging: {logging}')

    input_file = sys.argv[1]
    oracle_script = sys.argv[2]

    log(f'input_file: {input_file}')
    log(f'oracle_script: {oracle_script}')

    input_read = read_input(input_file)

    #Starting Lines Phase
    input_lines = split_lines(input_read)
    output_lines, variants_lines = delta_debug(input_lines, oracle_script, "Lines")

    remain_lines = len(output_lines)
    removed_lines = len(input_lines) - len(output_lines)
    reduced_lines = "".join(output_lines)

    #Starting Characters Phase
    input_characters = split_characters(reduced_lines)
    newline_count = reduced_lines.count("\n")

    output_characters, variants_characters = delta_debug(input_characters, oracle_script, "Characters", newline_count)

    remain_characters = len(output_characters)
    removed_characters = len(input_characters) - len(output_characters)
    reduced_characters = "".join(output_characters)

    #Build Output Dictionary and print JSON
    output = {}
    output['lines'] = {}
    output["lines"]['remain'] = remain_lines
    output["lines"]['removed'] = removed_lines
    output["lines"]['variants'] = variants_lines
    output["lines"]['reduced'] = reduced_lines

    output['characters'] = {}
    output["characters"]['remain'] = remain_characters
    output["characters"]['removed'] = removed_characters
    output["characters"]['variants'] = variants_characters
    output["characters"]['reduced'] = reduced_characters

    log("")
    print(json.dumps(output, indent=4))

    log(f'\nRaL: {remain_lines}, RoL: {removed_lines}, VL: {variants_lines}, RdL: {reduced_lines}\nRaC: {remain_characters}, RoC: {removed_characters}, VC: {variants_characters}, RdC: {reduced_characters}')

    log(f'Time: {time.perf_counter() - start_time}')
