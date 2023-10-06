git init
git add .
git commit -m "avg-bar and timeline ok"
git remote add origin https://github.com/yzpt/vlille_dashboard.git
git push --set-upstream origin master

python -m venv venv
.\venv\Scripts\activate

mkdir templates

pip install flask
pip install google-cloud-bigquery
pip install requests

mkdir app
cd app
..\venv\Scripts\activate  
pip freeze > requirements.txt

# > Dockerfile
# > run Docker 

# docker cmd
docker build -t europe-west9-docker.pkg.dev/vlille/flask-dashboard/dashboard-vlille:latest app/

# test du container Docker
# docker run -p 8080:8080 europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest
# ================ MARCHE PAS EN LOCAL WHY ? =================

# push du container Docker
docker push europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest

# create cloud run service
gcloud run deploy dashboard-vlille --image europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest --platform managed --region europe-west9 --allow-unauthenticated
# il fallait activer l'api run pour le projet upwrk
gcloud config list
gcloud config set project vlille-396911

# ====================
# bq get the schema of a table
bq show --schema --format=prettyjson vlille-396911:flask_dataset.transactions_test > transactions_test_schema.json

# powershell command to run a .sh file
./journal.sh

