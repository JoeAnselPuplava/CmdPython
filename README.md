# Command Line Python Tool for PostGres

A command line tool that allows private queries on postgres databases

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

How to install and set up the tool

```bash
# Clone the repository
git clone https://github.com/ZyphersWeb/CmdPython.git
```

## Use

Ensure that you are in the directory displaying dpsql_tool, venv, and README.md

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

Run dpsql with the query option
```bash
dpsql query "This is my query!"
```

Once you're done deactivate the virtual environment
```bash
deactivate
```
