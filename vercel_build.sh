# #!/bin/bash
# pip install -r requirements.txt
# python manage.py collectstatic --no-input

python3.9 -m pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput --clear