#!/bin/bash

jupyter nbconvert --to script starter.ipynb

# install pipenv
pipenv --python 3.12.4
pipenv install