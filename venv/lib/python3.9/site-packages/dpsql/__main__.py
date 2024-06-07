#!/usr/bin/env python3
try:
    import argparse
    import psycopg2
    import psycopg2.extras
    import pandas as pd
    import json
    from IPython.display import display
    # print("libraries imported")
except ImportError as e:
    print(f"Error importing libraries: {e}")

global connection, cursor

CONFIG_FILE = "db_config.json"

#Function made in privateDS
def postgres_DB(dbname, user, host, password):
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname=dbname, user=user, host=host, password=password)
        try:
            # Create a cursor
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("Connected to database, cursor defined")
            save_config(dbname, user, host, password)
            return conn, cur
        except psycopg2.Error as e:
            print(f"Error creating cursor: {e}")
            # Close the connection in case of an error
            conn.close()
            return None, None      
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None, None

def query(args):
    config = load_config()
    _, cursor = postgres_DB(config["dbname"], config["user"], config["hostname"], config["password"])

    # Execute query
    cursor.execute(args.query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(cursor.fetchall(), columns=column_names)
    # return df
    display(df)

# Saves the database details so that the program can 
# connect to the database without prompting user for all the information
def save_config(dbname, user, host, password):
    config = {
        "hostname": host,
        "dbname": dbname,
        "user": user,
        "password": password,
    }
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# Loads the previously saved information about the database
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        return None

def connDB(args):
    print(f"DBName: {args.dbname}")
    print(f"Username: {args.user}")
    print(f"Hostname: {args.hostname}")
    print(f"Password: {args.password}")
    postgres_DB(f"{args.dbname}", f"{args.user}", f"{args.hostname}", f"{args.password}")

def main():
    parser = argparse.ArgumentParser(description="A command line tool to query PostGres databases")
    
    # Create subparsers for subcommands
    subparsers = parser.add_subparsers()

    # Query command
    parser_query = subparsers.add_parser('query',  help="Enter a query to search the database")
    parser_query.add_argument('query', type=str, help="The query to search the database")
    parser_query.set_defaults(func=query)

    # Connect command
    # Use defaults from config file if available
    config = load_config()
    def_dbname   = config["dbname"]   if config else "my_database"
    def_user     = config["user"]     if config else "my_user"
    def_hostname = config["hostname"] if config else "localhost"
    def_password = config["password"] if config else "my_password"

    parser_query = subparsers.add_parser('connect',  help="Enter a query to search the database")
    parser_query.add_argument('dbname',   nargs='?', type=str, default=def_dbname,   help="The name of the postgres database")
    parser_query.add_argument('user',     nargs='?', type=str, default=def_user,     help="The username to connect to postgres database")
    parser_query.add_argument('hostname', nargs='?', type=str, default=def_hostname, help="The hostname to connect to postgres database")
    parser_query.add_argument('password', nargs='?', type=str, default=def_password, help="The password to connect to postgres database")
    parser_query.set_defaults(func=connDB)
    
    # Parse arguments and call appropriate function
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

