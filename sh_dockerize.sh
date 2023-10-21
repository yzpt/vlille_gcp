gcloud config list

# gcloud set project
gcloud config set project vlille-gcp

# build du container Docker
docker build -t europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container dashboard/app/

# Push Docker --> GCP Artifact Registry
docker push europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container

# Création d'un service Cloud Run
gcloud run deploy dashboard-service --image europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container --region europe-west9 --platform managed --allow-unauthenticated



