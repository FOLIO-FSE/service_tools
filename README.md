# service_tools
A set of scripts and a GUI for performing service tasks and migration work. 
Works on Windows as well as Linux. Might work on MacOS     
![](image.png?raw=true)

# Table of contents
- [Installation](#installation)
  * [Prerequisites](#prerequisites)
  * [Clone this repository to your local computer](#clone-this-repository-to-your-local-computer)
  * [Create a virtual environment using pipenv or venv](#create-a-virtual-environment-using-pipenv-or-venv)
- [Running](#running)
  * [Running the CLI version](#running-the-cli-version)
  * [Running the GUI](#running-the-gui)
- [Available tasks](#available-tasks)
 


# Installation
## Prerequisites
* [pipenv](https://pipenv.pypa.io/en/latest/)
* python 3.7.* installed. Tested with 3.7.1 and 3.7.8. 3.8+ will make some dependencies crash.

## Clone this repository to your local computer
```git clone git@github.com:FOLIO-FSE/service_tools.git```   
## Create a virtual environment using pipenv or venv
Go to the folder where the repo is located and do the following:
* ```pipenv install python --3.7.8 ``` to create the environment and install dependencies

# Running
This repo can either be run through its GUI, using python main.py, or the command line, using python main_cli.py

## Running the CLI version
To see the list of available tasks, run ```pipenv run python main_cli.py -h```
The print out is a bit messy, but then pick one of the available tasks from the list below:   
```pipenv run python main_cli.py SetHoldShelfToAllUsers -h```
That shows you the syntax for running the specific task.

## Running the GUI
*You must use the environment that you will run the program in. Using WSL2 to run this in windows will not work*   
From the command line, run ```pipenv run python main.py```
You then should see something like this:   
![](image.png?raw=true)


# Available tasks
## ElasticLoader
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## SetHoldShelfToAllUsers
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## AddPermissionToUser
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## BatchPoster
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## ExtractItemInfoFromMARC
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## JoinIdMaps
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## Add852ToMarc
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## XML2JSON
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## HarvestSierraData
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## MARCChecker
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## SetSourceToFOLIOForMissingSRSRecs
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## RefDataBackupDeleteAndLoad
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## ListPermissions
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## ListUsersByPermission
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## EmptyInstanceIdentifierRemover
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## IterateOverSRS
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## ListRecallsWithAvailableItems
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## CountMarcRecords
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## InstanceIdentifierRemover
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## OAIHarvest
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## MigrateOpenLoans
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## OAIListIdentifiers
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## SingleObjectsPoster
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## AddHRIDToMARCRecords
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## DeleteInstances
### Description   
### Syntax   
```pipenv run python main_cli.py ...```   
    
## MigrateUsers
### Description   
### Syntax   
```pipenv run python main_cli.py ...``` 
