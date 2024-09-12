#!/bin/bash

jupyter nbconvert --to script starter.ipynb

# install dependencies and activate them in terminal using pipenv
pipenv --python 3.12.4
pipenv install
pipenv shell