#####     __main__.py
#####     by Joe-Ansel Puplava
#####     Creates a 
import argparse
from opendp.mod import enable_features
enable_features('contrib', 'honest-but-curious')

# To make df look nicer
from tabulate import tabulate

from snsql.metadata import Metadata
from snsql.sql import PrivateReader
from snsql.sql.reader.pandas import PandasReader
from snsql.sql.reader.postgres import PostgresReader
from snsql.sql.privacy import Privacy

# helper files
from snsql.sql.metafile import *
from snsql.sql.seperateQ import *

# Uses snsql to run a query that can't be seperated privately
def privateQuery(query, dbName, epsilon):
    create_metaFile(dbName)
    # Gets meta data
    meta = Metadata.from_file('PUMZ.yaml')

    # Creates a PostgresReader
    reader = PostgresReader(host="localhost", database=dbName, user="postgres", password="")

    # Creates a private reader
    private_reader = PrivateReader(reader, meta, privacy=Privacy(epsilon=epsilon, delta=0.1))

    # Executes query privately
    rs = private_reader.execute(query)

    # Prints results
    print(tabulate(rs))

def main():
    parser = argparse.ArgumentParser(description="Wrapper for the psql command", add_help=False)

    # Capture all arguments to pass them directly to psql
    parser.add_argument('psql_args', nargs=argparse.REMAINDER, help="Arguments for psql command")
    parser.add_argument('-epsilon', required=False, type=float, help="Privacy budget for the query")
    parser.add_argument('-d', required=False, type=str, help="Database to be queried")

    # Parse the arguments and handle the --help option
    args, unknown_args = parser.parse_known_args()

    
    # Extract SQL query from arguments
    query = ""

    if ("-c" in unknown_args):
        query = "".join(args.psql_args[0])
    elif ("-c" in args.psql_args):
        query_index = args.psql_args.index('-c') + 1
        query = "".join(args.psql_args[query_index:])
    elif ("-f" in args.psql_args):
        query_index = args.psql_args.index('-f') + 1
        filePath = "".join(args.psql_args[query_index:])
        with open(filePath,"r") as f:
            query = f.read()
    elif ("-f" in unknown_args):
        filePath = "".join(args.psql_args[0])
        with open(filePath,"r") as f:
            query = f.read()
    else:
        query = None

    if args.epsilon is None:
        parser.error("The -epsilon argument is required for this query.")

    
    # Create Meta Data Table
    if args.d is None:
        parser.error("A database name is required for this query")
    else:
        # if canSeperate(query):
        #     sep_join(query, args.d, args.epsilon)
        #     # sep_query(query, args.d, args.epsilon)
        # else:
            privateQuery(query, args.d, args.epsilon)


if __name__ == "__main__":
    main()