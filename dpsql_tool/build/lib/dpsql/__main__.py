import argparse
import subprocess
import os
import sys
from opendp.mod import enable_features
enable_features('contrib', 'honest-but-curious')
from opendp.measurements import make_base_laplace, atom_domain, absolute_distance
from pglast import parse_sql, ast, visitors
from pprint import pprint


def is_aggregate_query(node):
    # List of aggregate querie names (add more as needed)
    aggregate_queries = {'count', 'sum', 'avg', 'min', 'max'}
    if node.funcname[0].sval in aggregate_queries:
        print("True!")
        return True
    print("False!")
    return False

# function assumes its a basic sql query (no potential sub queries)
def contains_aggregate_function(query):
    # Make the ast tree for the query
    root = parse_sql(query)
    stmt = root[0]
    sstmt = stmt.stmt
    for node in sstmt.targetList:
        subnode = traverse_targetList(node.val)
        if subnode is not None:
            return is_aggregate_query(subnode)
    return False

def traverse_targetList(node):
    # pprint(node(skip_none=True))
    if isinstance(node, ast.FuncCall):
        return node
    elif isinstance(node, ast.RowExpr):
        return traverse_targetList(node.val)
    return None


# def apply_dp_count():
#     #Code
# def apply_dp_sum():
#     #Code
# def apply_dp_mean():
#     #Code
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
    else:
        query = None

    # Prepare the psql command
    if unknown_args :
        psql_command = ['psql'] + unknown_args + args.psql_args
    else:
        psql_command = ['psql'] + args.psql_args
    

    # Run the psql command
    result = subprocess.run(psql_command, capture_output=True, text=True)

    # Split the output into lines
    output_lines = result.stdout.splitlines()

    # Check that the user is using a query
    if query is not None:
        # Apply dp if the query is an aggregate
        if contains_aggregate_function(query):
            if args.epsilon is None:
                parser.error("The --epsilon argument is required for this query.")
            else:
                print("It's an aggregate qurie!")
                # result_value = output_lines[2].strip()
                # query_result = float(result_value)
                # noisy_result = apply_differential_privacy(query_result, args.epsilon)
                # output_lines[2] = str(noisy_result)
        # Reject non-aggregate queries
        else:
            parser.error("Non-aggregate queries are not allowed")

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



