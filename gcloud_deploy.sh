# Build
gcloud builds submit \
   --tag us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest

# Deploy
# gcloud run deploy notif-challenge-service \
#    --image us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest \
#    --region us-east4 \
#    --allow-unauthenticated \
#    --command /bin/sh \
#    --args '-c,exec fastapi run --host 0.0.0.0 --port "${PORT:-8000}" src/main.py --proxy-headers --forwarded-allow-ips "*"'
# Deploy simple (TODO: check if it works)
gcloud run deploy notif-challenge-service \
   --image us-east4-docker.pkg.dev/notifications-challenge/notif-challenge-repo/notif-challenge-api:latest \
   --region us-east4
