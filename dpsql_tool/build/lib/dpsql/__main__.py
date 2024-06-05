#!/usr/bin/env python3
try:
    import argparse
    import psycopg2
    import psycopg2.extras
    import pandas as pd
    print("libraries imported")
except ImportError as e:
    print(f"Error importing libraries: {e}")

#Function made in privateDS
def postgres_DB(dbname, user, host, password):
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname=dbname, user=user, host=host, password=password)
        try:
            # Create a cursor
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("Connected to database, cursor defined")
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
    print(f"The query you entered is: {args.query}")


def showTables(cursor):
    
    # Get table names from the information schema
    cursor.execute("SELECT TABLE_NAME \
                    FROM INFORMATION_SCHEMA.TABLES \
                   WHERE TABLE_TYPE = 'BASE TABLE' \
                     AND TABLE_SCHEMA='public' ")
    
    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]
    for x in column_names:
        print(x)

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(cursor.fetchall(), columns=column_names)
    display(df) 

def customQuery(cursor):
    # Ask user for a query
    print("Enter your query (type stop to end):")
    query = input()
    if (query == "stop"):
        return query
    # Execute query
    cursor.execute(query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(cursor.fetchall(), columns=column_names)
    # return df
    display(df)  
    print("Invalid Query")
        
    return query

def connDB(args):
    print(f"{args.name}")
    print(f"{args.username}")
    print(f"{args.hostname}")
    print(f"{args.password}")
    # postgres_DB({args.name}, {args.username}, {args.hostname}, {args.password})
    postgres_DB(f"{args.name}", f"{args.username}", f"{args.hostname}", f"{args.password}")

def userInput():
    # "university"
    print("Enter database name: ")
    # DBname = input()
    DBname = "university"

    # "postgres"
    print("Enter userName: ")
    # userName = input()
    userName = "postgres"

    # "localhost"
    print("Enter host name: ")
    # hostName = input()
    hostName = "localhost"

    # ""
    print("Enter password: ")
    # password = input()
    password = ""
    

    print("Connecting to PostGresDB")
    conn, curs = postgres_DB("university", "postgres", "localhost", "")
    # conn, curs = postgres_DB(DBname, userName, hostName, password)
    showTables(curs)
    query = ""
    while (query != "stop"):
        try:
            query = customQuery(curs)
        except:
            print("Invalid Query")
            conn, curs = postgres_DB(DBname, userName, hostName, password)

    print("Good Bye")


def main():
    parser = argparse.ArgumentParser(description="A command line tool to query PostGres databases")
    
    # Create subparsers for subcommands
    subparsers = parser.add_subparsers()

    # Query command
    parser_query = subparsers.add_parser('query',  help="Enter a query to search the database")
    parser_query.add_argument('query', type=str, help="The query to search the database")
    parser_query.set_defaults(func=query)

    # Connect command
    parser_query = subparsers.add_parser('connect',  help="Enter a query to search the database")
    parser_query.add_argument('name',     type=str, help="The name of the postgres database")
    parser_query.add_argument('username', type=str, help="The username to connect to postgres database")
    parser_query.add_argument('hostname', type=str, help="The hostname to connect to postgres database")
    parser_query.add_argument('password', type=str, help="The password to connect to postgres database")
    parser_query.set_defaults(func=connDB)
    
    # Parse arguments and call appropriate function
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

