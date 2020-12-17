# service_tools
A set of scripts and a GUI for performing service tasks and migration work. 
Works on Windows as well as Linux. Might work on MacOS  



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

## Running the GUI
*You must use the environment that you will run the program in. Using WSL2 to run this in windows will not work*   
From the command line, run ```pipenv run python main.py```
You then should see something like this:
![](image.png?raw=true)
