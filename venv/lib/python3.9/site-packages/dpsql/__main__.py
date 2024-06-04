#!/usr/bin/env python3

import argparse

def query(args):
    print(f"The query you entered is: {args.query}")

def main():
    parser = argparse.ArgumentParser(description="A command line tool for query postgres databases")
    
    # Create subparsers for subcommands
    subparsers = parser.add_subparsers()

    # Query command
    parser_query = subparsers.add_parser('query',  help="Enter a query to search the database")
    parser_query.add_argument('query', type=str, help="The query to search the database")
    parser_query.set_defaults(func=query)
    
    # Parse arguments and call appropriate function
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

