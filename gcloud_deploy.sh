# Build
gcloud builds submit \
   --tag us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest

# Deploy simple
gcloud run deploy notif-challenge-service \
   --image us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest \
   --region us-east4
