import subprocess
from pglast import parse_sql, ast, prettify
from pglast.ast import JoinExpr, RangeVar
from pglast.stream import RawStream
from pprint import pprint

# To make df look nicer
from tabulate import tabulate

import subprocess

import pandas as pd
import pandasql as ps
import duckdb
import io

from snsql.metadata import Metadata
from snsql.sql.reader.pandas import PandasReader
from snsql.sql.reader.postgres import PostgresReader
from snsql.sql import PrivateReader
from snsql.sql.privacy import Privacy

# helper files
from snsql.sql.metafile import *

# Checks if the node is an aggregate query
def is_aggregate_query(node):
    # List of aggregate querie names (add more as needed)
    aggregate_queries = {'count', 'sum', 'avg'}
    if node.funcname[0].sval in aggregate_queries:
        return True
    return False

# function assumes its a basic sql query (no potential sub queries)
def contains_aggregate_function(query):
    # Make the ast tree for the query
    root = parse_sql(query)
    stmt = root[0]
    sstmt = stmt.stmt
    
    # Looks for nodes that have a target list
    for node in sstmt.targetList:
        subnode = traverse_targetList(node.val)
        if subnode is not None:
            return is_aggregate_query(subnode)
    return False

def traverse_targetList(node):
    if isinstance(node, ast.FuncCall):
        return node
    elif isinstance(node, ast.RowExpr):
        for nodes in node.args:
            return traverse_targetList(nodes)
        # return traverse_targetList(node.args)
    return None


#     print(tabulate(finalDf))
def sep_join(query, dbName, epsilon):
    # Parse the SQL query to its AST representation
    root = parse_sql(query)
    stmt = root[0]
    sstmt = stmt.stmt
    
    print("Original query")
    print(RawStream()(stmt))
    print("=================")
    pprint(sstmt(skip_none=True))
    # print("=================")
    
    # Extract target list and from clause (which contains joins)
    tgtList = sstmt.targetList
    frClause = sstmt.fromClause[0]  # Start with the first join expression

    # Helper function to handle nested joins
    def process_join(frClause, df_counter):
        if isinstance(frClause, JoinExpr):
            # Recursively process the left (larg) and right (rarg) of the join
            if 'larg' in frClause:
                left_df_name, df_counter = process_join(frClause.larg, df_counter)
            if 'rarg' in frClause:
                right_df_name, df_counter = process_join(frClause.rarg, df_counter)

            # Extract the join condition (quals)
            join_condition = f"{left_df_name}.{frClause.quals.lexpr.fields[1].sval} {frClause.quals.name[0].sval} {right_df_name}.{frClause.quals.rexpr.fields[1].sval}"

            # Create the join query
            print(f"SELECT * FROM {left_df_name} JOIN {right_df_name} ON {join_condition}")
            join_query = f"SELECT * FROM {left_df_name} JOIN {right_df_name} ON {join_condition}"
            print(f"\nJoin query {df_counter}\n{join_query}")
            
            # Execute the join query in DuckDB
            latest_df = duckdb.query(join_query).df()

            # Register the resulting DataFrame for future joins
            new_df_name = f'df{df_counter}'
            duckdb.register(new_df_name, latest_df)

            return new_df_name, df_counter + 1

        elif isinstance(frClause, RangeVar):
            # If it's a RangeVar, it refers to a table, so fetch and register it
            table_name = frClause.relname

            # Execute the query to get the table data
            print(f"SELECT * FROM {table_name}")
            psql_command = ['psql', '-c', f"SELECT * FROM {table_name}", '-d', dbName]
            result = subprocess.run(psql_command, capture_output=True, text=True)

            # Clean the output and create a DataFrame
            outputLines = result.stdout.splitlines()[:-2]
            cleanLines = outputLines[0:1] + outputLines[2:]
            cleanOutput = "\n".join(cleanLines)
            df = pd.read_csv(io.StringIO(cleanOutput), sep="|")
            df.columns = df.columns.str.strip()

            # Register the DataFrame in DuckDB
            df_name = f'df{df_counter}'
            duckdb.register(df_name, df)

            return df_name, df_counter + 1

    # Start processing the first join expression
    final_df_name, _ = process_join(frClause, 1)

    # After processing joins, construct the final aggregate query
    root = parse_sql(f"SELECT * FROM {final_df_name}")
    aggregateQuery = root[0]
    aggregateQuery.stmt.targetList = tgtList
    print("\nFinal aggregate query\n" + RawStream()(aggregateQuery))

    # Execute the final aggregation query
    finalDf = duckdb.query(RawStream()(aggregateQuery)).df()
    
    # Display the result
    print(tabulate(finalDf))



# Takes a query 
def sep_query(query, dbName, epsilon):
    # Make the ast tree for the query
    root = parse_sql(query)
    stmt = root[0]
    sstmt = stmt.stmt
    print("Original query")
    print(RawStream()(stmt))
    print("=================")
    pprint(sstmt(skip_none=True))

    # Create target list with select *
    root = parse_sql("select *")
    select_all = root[0]
    targetListAll = select_all.stmt.targetList
    
    # Original SQL targetList
    ogTargetList = sstmt.targetList

    #Alter the SQL Tree objects
    sstmt.all = True
    sstmt.targetList = None
    sstmt.targetList = targetListAll

    # Save the filter query
    filterQuery = RawStream()(stmt)

    # Print Filter Query
    print("\nFilter Query")
    print(filterQuery)
    print("=================")

    # Create aggregate query with select all tree
    select_all.stmt.targetList = ogTargetList
    select_all.stmt.fromClause = sstmt.fromClause

    # Save the aggregate query
    aggregateQuery = RawStream()(select_all)

    # Print count query
    print("\nAggregate Query")
    print(aggregateQuery)

    # Run filter query on postgres
    psql_command = ['psql', '-c', filterQuery, '-d', dbName]
    result = subprocess.run(psql_command, capture_output=True, text=True)

    # Clean the output
    outputLines = result.stdout.splitlines()[:-2]
    cleanLines = outputLines[0:1] + outputLines[2:]
    cleanOutput = "\n".join(cleanLines)

    # Create a df using the clean output
    df = pd.read_csv(io.StringIO(cleanOutput), sep="|")

    # Clean the columns
    df.columns = df.columns.str.strip()
    
    # # Print
    # print("\n\n\n------")
    # if ogTargetList[0].name is not None:
    #     print(ogTargetList[0].name)
    # print(customCount(df))
    # print("------")

    # Create metafile with df
    metaFile_pandas(df, sstmt.fromClause)
    # metaFile_pandas(dbName, df, sstmt.fromClause)
    meta = Metadata.from_file('PUMZ.yaml')
    privateReader = PrivateReader.from_connection(df, privacy=Privacy(epsilon=epsilon, delta=0.1), metadata=meta)

    # Executes query privately
    rs = privateReader.execute(aggregateQuery)

    # Prints results
    print(tabulate(rs))

def customCount(df):
    return df.shape[0]

def canSeperate(query):
    # Make the ast tree for the query
    root = parse_sql(query)
    stmt = root[0]
    sstmt = stmt.stmt
    
    return sstmt.whereClause is not None and contains_aggregate_function(query)
