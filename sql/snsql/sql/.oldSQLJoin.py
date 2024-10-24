
# def sep_join(query, dbName, epsilon):
#     # Make the ast tree for the query
#     root = parse_sql(query)
#     stmt = root[0]
#     sstmt = stmt.stmt
#     print("Original query")
#     print(RawStream()(stmt))
#     print("=================")
#     pprint(sstmt(skip_none=True))
#     print("=================")
#     tgtList = sstmt.targetList
#     frClause = sstmt.fromClause[0]

#     # General sql query
#     root = parse_sql("select * from db")
#     rightSelect = root[0]
#     # pprint(rightSelect.stmt(skip_none=True))

#     # Right select statement
#     rightSelect.stmt.targetList[0].val.fields = frClause.quals.rexpr.fields
#     rightSelect.stmt.fromClause[0].relname = frClause.quals.rexpr.fields[0].sval
#     # pprint(rightSelect(skip_none=True))
#     print("Right select statement\n" + RawStream()(rightSelect))

#     # Run right query on postgres
#     psql_command = ['psql', '-c', RawStream()(rightSelect), '-d', dbName]
#     result = subprocess.run(psql_command, capture_output=True, text=True)

#     # Clean the output
#     outputLines = result.stdout.splitlines()[:-2]
#     cleanLines = outputLines[0:1] + outputLines[2:]
#     cleanOutput = "\n".join(cleanLines)

#     # Create a df using the clean output
#     df1 = pd.read_csv(io.StringIO(cleanOutput), sep="|")

#     # Clean the columns
#     df1.columns = df1.columns.str.strip()

#     # General sql query
#     root = parse_sql("select * from db")
#     leftSelect = root[0]
#     # Left select statement
#     leftSelect.stmt.targetList[0].val.fields = frClause.quals.lexpr.fields
#     leftSelect.stmt.fromClause[0].relname = frClause.quals.lexpr.fields[0].sval
#     # pprint(leftSelect(skip_none=True))
#     print("\nLeft select statement\n" + RawStream()(leftSelect))

#     # Run left query on postgres
#     psql_command = ['psql', '-c', RawStream()(leftSelect), '-d', dbName]
#     result = subprocess.run(psql_command, capture_output=True, text=True)

#     # Clean the output
#     outputLines = result.stdout.splitlines()[:-2]
#     cleanLines = outputLines[0:1] + outputLines[2:]
#     cleanOutput = "\n".join(cleanLines)

#     # Create a df using the clean output
#     df2 = pd.read_csv(io.StringIO(cleanOutput), sep="|")

#     # Clean the columns
#     df2.columns = df2.columns.str.strip()

#     # General sql query
#     root = parse_sql("SELECT * FROM df1 JOIN df2 on df1." + frClause.quals.rexpr.fields[1].sval +
#                      " " + frClause.quals.name[0].sval +
#                      " df2." + frClause.quals.lexpr.fields[1].sval)
#     joinSelect = root[0]
#     print("\nJoin query\n" + RawStream()(joinSelect))
#     df3 = duckdb.query(RawStream()(joinSelect)).df()

#     # Final aggregate query
#     root = parse_sql("SELECT * FROM df3")
#     aggregateQuery = root[0]
#     aggregateQuery.stmt.targetList = tgtList
#     print("\nAggregate query\n" + RawStream()(aggregateQuery))
#     finalDf = duckdb.query(RawStream()(aggregateQuery)).df()