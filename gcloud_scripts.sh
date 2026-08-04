## Initial setup

#gcloud services enable run.googleapis.com
#gcloud services enable cloudbuild.googleapis.com
#gcloud services enable artifactregistry.googleapis.com

## Set the nearest location to the db to decrease latency at minimum
## https://docs.cloud.google.com/artifact-registry/docs/repositories/repo-locations?hl=es-419#location-r
# gcloud artifacts repositories create notif-challenge-repo --repository-format=docker --location=us-east4

## Build and Push to Artifact Registry
# gcloud builds submit \
#    --tag us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest

## Deploy to Cloud Run
# gcloud run deploy notif-challenge-service \
#    --image us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest \
#    --region us-east4 \
#    --allow-unauthenticated \
#    --command /bin/sh \
#    --args '-c,exec fastapi run --host 0.0.0.0 --port "${PORT:-8000}" src/main.py --proxy-headers --forwarded-allow-ips "*"'

## After deploy, update env vars in google console
## generate a new jwt secret
#python3 -c "import secrets; print(secrets.token_hex(32))"
## go to project cloud run instance and go to "Edit & deploy new revision"
## and then to "variable & secrets"

## Add custom domain
## Validate ownership first with https://search.google.com
## Then
# gcloud beta run domain-mappings create \
#     --service=notif-challenge-service \
#     --domain=notif-api.gorandp.com \
#     --region=us-east4

## And it takes a long time until google certificates, like 15-40 minutes
## to check the status, run:
# gcloud beta run domain-mappings describe --domain notif-api.gorandp.com --region=us-east4
