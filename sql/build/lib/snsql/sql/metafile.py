#####     metafile.py
#####     by Joe-Ansel Puplava
#####     Creates a 

import pandas as pd
from pglast import parse_sql, ast, prettify
from pglast.stream import RawStream
from pprint import pprint
import subprocess

# To make df look nicer
from tabulate import tabulate



# Creates the needed yaml file for snsql to privately query a pandas dataframe
def metaFile_pandas(df, fromClause):
    file_name = 'PUMZ.yaml'
    start_text = f'\"\":\n  \"\":\n    {RawStream()(fromClause)}:\n      row_privacy: True\n      rows: 1000\n'

    # Open the file in write mode and write the custom text to it
    with open(file_name, 'w') as file:
        file.write(start_text)

    # Sets columns to dataframe columns
    columnNames = df.columns
    for name in columnNames:
        # Checks each result to see if it's a string, and names each type as such
        result = df[name].apply(lambda x: isinstance(x, str)).all()
        if result:
            df[name] = df[name].astype('string')

        with open(file_name, 'a') as file:
            if df[name].dtype == "int64":
                file.write(f"      {name}:\n        type: int\n        lower: 0\n        upper: 1000\n")
            elif df[name].dtype == "float64":
                file.write(f"      {name}:\n        type: float\n        lower: 0\n        upper: 1000\n")
            elif df[name].dtype == "string":
                file.write(f"      {name}:\n        type: string\n")
            else:
                file.write(f"      {name}:\n        type: object\n")

# Creates a yaml file for snsql to privately query a psql database
def create_metaFile(db_name):
    file_name = 'PUMZ.yaml'
    start_text = '\"\":\n  \"\":\n'

    # Open the file in write mode and write the custom text to it
    with open(file_name, 'w') as file:
        file.write(start_text)

    # Get table names from the given database
    psql_command = [
        'psql',
        '-c',
        "SELECT table_name \
        FROM information_schema.tables \
        WHERE table_schema = 'public'",
        '-d', db_name]
    result = subprocess.run(psql_command, capture_output=True, text=True)
    output_lines = (result.stdout.splitlines())[2:-2]


    for table in output_lines:
        with open(file_name, 'a') as file:
            file.write(f"    {table[1:]}:\n      row_privacy: True\n      rows: 1000\n")

        # Get the columns and data types from the tables
        psql_command = [
            'psql',
            '-c',
            f"SELECT column_name, data_type, character_maximum_length \
            FROM information_schema.columns \
            WHERE table_name = '{table[1:]}'",
            '-d', db_name]
        result = subprocess.run(psql_command, capture_output=True, text=True)
        output_lines = result.stdout.splitlines()
        output_lines = output_lines[2:-2]
        
        for column in output_lines:
            # Split the string by '|'
            parts = column.split('|')
            
            # Strip whitespace from each part
            column_name = parts[0].strip()
            data_type = parts[1].strip()
            
            with open(file_name, 'a') as file:
                if data_type == "integer":
                    file.write(f"      {column_name}:\n        type: int\n        lower: 0\n        upper: 1000\n")
                elif data_type == "character varying":
                    file.write(f"      {column_name}:\n        type: string\n")
                else:
                    file.write(f"      {column_name}:\n        type: float\n        lower: 0\n        upper: 1000\n")
