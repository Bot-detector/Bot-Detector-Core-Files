docker build . --file Dockerfile-Prod -t bot-detector/bd-api:production
docker tag bot-detector/bd-api:production hub.osrsbotdetector.com/bot-detector/bd-api:production
docker push hub.osrsbotdetector.com/bot-detector/bd-api:production
kubectl rollout restart deploy bd-prod-api