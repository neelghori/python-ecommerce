# # #!/bin/bash
# # pip install -r requirements.txt
# # python manage.py collectstatic --no-input

# python3.9 -m pip3 install -r requirements.txt
# python3.9 manage.py collectstatic --noinput --clear

echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python3.9 -m venv venv

# activate the virtual environment
source venv/bin/activate

# install all deps in the venv
pip install -r requirements.txt

# collect static files using the Python interpreter from venv
python manage.py collectstatic --noinput