#! /bin/bash

# Copy the yapf pre-commit hook
echo 'copying yapf pre-commit hook'
cp config/pre-commit .git/hooks/

# check if pip is installed
if ! [ -x "$(command -v pip3)" ]; then
  echo 'error: pip3 is not installed.' >&2
  exit 1
fi

# check if virtualenv is installed
if ! [ -x "$(command -v virtualenv)" ]; then
  echo 'error: virtualenv is not installed.' >&2
  exit 1
fi

# set up the virtualenv
cd ../
virtualenv Codenames
cd Codenames

# run initial pip install
pip3 install -r requirements.txt

exit 0
