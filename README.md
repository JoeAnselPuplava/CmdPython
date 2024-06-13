# Command Line Python Tool for PostGres

A command line tool that allows private queries on postgres databases

# Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

# Installation

How to install and set up the tool

```bash
# Clone the repository
git clone https://github.com/ZyphersWeb/CmdPython.git
```

# Use

Ensure that you are in the directory displaying dpsql_tool, venv, venv2, and README.md

There are two versions of dpsql that the user can use

* venv uses custom commands to connect and enter queries

* venv2 directly sends the commands to psql and should have all the same capabilities as psql

## For venv follow these directions (venv2 below)
Start a virtual Python environment based on your shell

|              Bash              |             Fish               |
|--------------------------------|--------------------------------|
| source venv/bin/activate       | source venv/bin/activate.fish  |

```bash
# bash
source venv/bin/activate
```
```bash
# fish
source venv/bin/activate.fish
```

Connect to your desired postgres database
```bash
dpsql connect dbname username hostname password
```

Run a query on the database
```bash
dpsql query "Some query"
```

If the query is an aggregate add the --epsilon command
```bash
dpsql query "Some aggregate query" -epsilon 1.0
```

Once you're done deactivate the virtual environment
```bash
deactivate
```
## For venv2 follow these directions
Start a virtual Python environment based on your shell

|              Bash              |             Fish               |
|--------------------------------|--------------------------------|
| source venv2/bin/activate      | source venv2/bin/activate.fish |

```bash
# bash
source venv2/bin/activate
```
```bash
# fish
source venv2/bin/activate.fish
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
