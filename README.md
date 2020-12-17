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
  * [ElasticLoader](#elasticloader)
    + [Description](#description)
    + [Syntax](#syntax)
  * [SetHoldShelfToAllUsers](#setholdshelftoallusers)
    + [Description](#description-1)
    + [Syntax](#syntax-1)
  * [AddPermissionToUser](#addpermissiontouser)
    + [Description](#description-2)
    + [Syntax](#syntax-2)
  * [BatchPoster](#batchposter)
    + [Description](#description-3)
    + [Syntax](#syntax-3)
  * [ExtractItemInfoFromMARC](#extractiteminfofrommarc)
    + [Description](#description-4)
    + [Syntax](#syntax-4)
  * [JoinIdMaps](#joinidmaps)
    + [Description](#description-5)
    + [Syntax](#syntax-5)
  * [Add852ToMarc](#add852tomarc)
    + [Description](#description-6)
    + [Syntax](#syntax-6)
  * [XML2JSON](#xml2json)
    + [Description](#description-7)
    + [Syntax](#syntax-7)
  * [HarvestSierraData](#harvestsierradata)
    + [Description](#description-8)
    + [Syntax](#syntax-8)
  * [MARCChecker](#marcchecker)
    + [Description](#description-9)
    + [Syntax](#syntax-9)
  * [SetSourceToFOLIOForMissingSRSRecs](#setsourcetofolioformissingsrsrecs)
    + [Description](#description-10)
    + [Syntax](#syntax-10)
  * [RefDataBackupDeleteAndLoad](#refdatabackupdeleteandload)
    + [Description](#description-11)
    + [Syntax](#syntax-11)
  * [ListPermissions](#listpermissions)
    + [Description](#description-12)
    + [Syntax](#syntax-12)
  * [ListUsersByPermission](#listusersbypermission)
    + [Description](#description-13)
    + [Syntax](#syntax-13)
  * [EmptyInstanceIdentifierRemover](#emptyinstanceidentifierremover)
    + [Description](#description-14)
    + [Syntax](#syntax-14)
  * [IterateOverSRS](#iterateoversrs)
    + [Description](#description-15)
    + [Syntax](#syntax-15)
  * [ListRecallsWithAvailableItems](#listrecallswithavailableitems)
    + [Description](#description-16)
    + [Syntax](#syntax-16)
  * [CountMarcRecords](#countmarcrecords)
    + [Description](#description-17)
    + [Syntax](#syntax-17)
  * [InstanceIdentifierRemover](#instanceidentifierremover)
    + [Description](#description-18)
    + [Syntax](#syntax-18)
  * [OAIHarvest](#oaiharvest)
    + [Description](#description-19)
    + [Syntax](#syntax-19)
  * [MigrateOpenLoans](#migrateopenloans)
    + [Description](#description-20)
    + [Syntax](#syntax-20)
  * [OAIListIdentifiers](#oailistidentifiers)
    + [Description](#description-21)
    + [Syntax](#syntax-21)
  * [SingleObjectsPoster](#singleobjectsposter)
    + [Description](#description-22)
    + [Syntax](#syntax-22)
  * [AddHRIDToMARCRecords](#addhridtomarcrecords)
    + [Description](#description-23)
    + [Syntax](#syntax-23)
  * [DeleteInstances](#deleteinstances)
    + [Description](#description-24)
    + [Syntax](#syntax-24)
  * [MigrateUsers](#migrateusers)
    + [Description](#description-25)
    + [Syntax](#syntax-25)


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
