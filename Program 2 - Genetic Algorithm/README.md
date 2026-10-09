To run the tester, run the command: "python3 ga.py input_file [-log]". With input_file being replaced with the text file containing the target object and [-log] being an optional argument to include so that the program sends useful prints for debugging that would mess up the JSON.

Description of programming decisions

AI Usage

1. What is the initial population size?: #
2. How do you evaluate an individual? I.e., explain the formula that produces the fitness score.
3. What are the stopping criteria? (the GA loop stops when ...)
4. How do you select the chromosomes? (Using tournament selection or other methods? What are the tournament sizes? etc.)
5. How often do you perform crossover and mutation? Are the crossover and mutation rates fixed or adaptive?
6. How many chromosomes do you need to evaluate to achieve a chromosome with perfect fitness for the given test JSON? Due to the randomness of the algorithm, this number will fluctuate. Try to give some rough upper/lower bounds.  Note that your solution might not reach the target within the allowed time, but you should try to at least run once until it finds the target and report that here.