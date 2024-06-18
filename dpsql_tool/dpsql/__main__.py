import argparse
import subprocess
import os
import sys
from opendp.mod import enable_features
enable_features('contrib', 'honest-but-curious')
from opendp.measurements import make_base_laplace, atom_domain, absolute_distance


def is_aggregate_query(query):
    # List of supported aggregate functions
    aggregates = ['sum', 'avg', 'count', 'max', 'min']
    return any(agg in query.lower() for agg in aggregates)

def apply_differential_privacy(query_result, epsilon):
    # Apply Laplace noise for differential privacy
    scale = 1.0 / epsilon
    base_laplace = make_base_laplace(
        atom_domain(T=float),
        absolute_distance(T=float),
        scale=scale)
    noisy_result = base_laplace(query_result)
    if noisy_result < 0: 
        noisy_result*=-1
    return noisy_result

def main():
    parser = argparse.ArgumentParser(description="Wrapper for the psql command", add_help=False)
    
    # Capture all arguments to pass them directly to psql
    parser.add_argument('psql_args', nargs=argparse.REMAINDER, help="Arguments for psql command")
    parser.add_argument('-epsilon', required=False, type=float, help="Privacy budget for the query")
    
    psql_command = ""

    # Parse the arguments and handle the --help option
    args, unknown_args = parser.parse_known_args()

    # Extract SQL query from arguments
    query = ""
    if ("-c" in unknown_args):
        query = "".join(args.psql_args[0])
    elif ("-c" in args.psql_args):
        query_index = args.psql_args.index('-c') + 1
        query = "".join(args.psql_args[query_index:])

    # Prepare the psql command
    if unknown_args :
        psql_command = ['psql'] + unknown_args + args.psql_args
    else:
        psql_command = ['psql'] + args.psql_args
    

    # Run the psql command
    result = subprocess.run(psql_command, capture_output=True, text=True)

    # Split the output into lines
    output_lines = result.stdout.splitlines()

    # Apply dp if the query is an aggregate
    if is_aggregate_query(query):
        if args.epsilon is None:
            parser.error("The --epsilon argument is required for this query.")
        else:
            result_value = output_lines[2].strip()
            query_result = float(result_value)
            noisy_result = apply_differential_privacy(query_result, args.epsilon)
            output_lines[2] = str(noisy_result)

    # Edit the first and last lines for help response
    if "--help" in unknown_args:
        output_lines[0] = "Wrapper for the psql command"
        output_lines[-2] = ""
        output_lines[-1] = ""

    # Join the modified lines back together
    modified_output = "\n".join(output_lines)
    
    # Print the modified output and errors to the console
    if modified_output:
        print(modified_output)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # Exit with the same return code as the psql command
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()



