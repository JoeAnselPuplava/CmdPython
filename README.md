# Command Line Python Tool for PostGres

A command line tool that allows private queries on postgres databases

# Table of Contents

- [Installation](#installation)
- [Use](#use)

# Installation

How to install and set up the tool

```bash
# Clone the repository
git clone https://github.com/ZyphersWeb/CmdPython.git
```

# Use

Ensure that you are in the directory displaying dpsql_tool, venv, and README.md

dpsql directly sends the commands to psql and should have all the same capabilities as psql, in addition to its added functionality

## For venv follow these directions
Start a virtual Python environment based on your shell

|              Bash              |             Fish               |
|--------------------------------|--------------------------------|
| source venv/bin/activate      | source venv/bin/activate.fish |

```bash
# bash
source venv/bin/activate
```
```bash
# fish
source venv/bin/activate.fish
```

Run a query on a postgres database like so
```bash
dpsql -c "Some query" -d databaseName
```
If the query is an aggregate query, add --epsilon at the beginning
```bash
dpsql --epsilon 1.0 -c "Some query" -d databaseName
```
Once you're done deactivate the virtual environment
```bash
deactivate
```
