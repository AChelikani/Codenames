#! /bin/bash

if ! [ -x "$(command -v pip3)" ]; then
  echo 'error: pip3 is not installed, install and run again' >&2
  exit 1
fi

if ! [ -x "$(command -v virtualenv)" ]; then
  echo 'error: virtualenv is not installed, install and run again' >&2
  exit 1
fi

# set up the virtualenv
cd ../../
virtualenv Codenames
cd Codenames

pip3 install -r requirements.txt

# install flake8's git hook
flake8 --install-hook git
git config --bool flake8.strict true

exit 0
