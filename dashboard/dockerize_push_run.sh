# docker cmd
docker build -t europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest app/

# push du container Docker
docker push europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest

# create cloud run service
gcloud run deploy dashboard-vlille --image europe-west9-docker.pkg.dev/vlille-396911/flask-dashboard/dashboard-vlille:latest --platform managed --region europe-west9 --allow-unauthenticated
