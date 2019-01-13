# Question-answering system for Macedonian test collection

This project was an attempt to create a system that automatically answers multiple-choice exams in the Macedonian language. In order for the system to answer the questions, lecture material needs to be supplied.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

This project works currently only on Ubuntu 16.04.4 LTS. The system requires the following third-party tools.

* [Python 3.6](https://www.python.org/downloads/) - the programming language in which the program is written in.

### Directory structure

- ./main.py
   This module contains the code for the question-answering system.
- ./config.yaml
   This file contains the configuration for running the program including lecture material, exam, symbols that should be filtered out etc.
- ./data
   This folder contains the resources for the question-answering system.

### Running

In order to run the program, the user needs to enter the home directory of the project and the following command on the terminal should be run:

```
$ sudo ./main.py

```

## Authors

* Stevica Bozhinoski stevica.bozhinoski@tum.de
* Ivana Bozhinova
* Jasmina Armenska

## Acknowledgments

We would like to thank our professor and mentor prof. pr. Katerina Zdravkova for her guidance and support during this project.
