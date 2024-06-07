import argparse
import subprocess
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Wrapper for the psql command", add_help=False)
    
    # Capture all arguments to pass them directly to psql
    parser.add_argument('psql_args', nargs=argparse.REMAINDER, help="Arguments for psql command")
    
    psql_command = ""

    # Parse the arguments and handle the --help option
    args, unknown_args = parser.parse_known_args()
    if unknown_args :
        print("Unknown!")
        psql_command = ['psql'] + unknown_args
    else:
        # Prepare the psql command
        print("Known!")
        psql_command = ['psql'] + args.psql_args

    # Run the psql command
    result = subprocess.run(psql_command, capture_output=True, text=True)
    
    # Split the output into lines
    output_lines = result.stdout.splitlines()

    # Edit the first and last lines
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



