# Issue Tracker System

## About

This project can be used to create teams and assign issues/tasks to members of the team. The issue description page also has features to start comment threads. Good consideration has given to privacy and so only authorized users can access certain features of this appliation. A remarkable feature of this project is that it uses NLP to extract Key Phrases and Named Entities along with its category from the title and description of the new issue which is going to be created, to analyse if a similar issue already exists. This is done by comparing the new issue text analytics parameters with the existing relevant issue text analytics parameters, and hence providing the user the option to discard the new issue creation, therefore avoiding redundancy, and the second option to create the issue anyway. For Text Analytics, the REST API of [Microsoft Azure Text Analytics Cognitive Service](https://docs.microsoft.com/en-in/azure/cognitive-services/text-analytics/) has been used.

## Pre-requisites

[Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/)

## Setup

1. Clone the repository
2. Change directory to the cloned repo
3. Run `pip install -r requirements.txt`
4. Run the following commands next:

```shell
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

5. Visit `localhost:8000` in a web browser and explore the app

## Demonstration Video

A demonstration video of the project is available at <https://youtu.be/UvtNgWeEHAM>
