SERVER=84.201.130.175
cd deploy_tools
fab deploy:host=aleks@$SERVER
cd ..
STAGING_SERVER=$SERVER ../venv/bin/python manage.py test functional_tests