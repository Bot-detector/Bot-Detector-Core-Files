docker build . --file Dockerfile-Dev -t bot-detector/bd-api:latest
docker tag bot-detector/bd-api:latest hub.osrsbotdetector.com/bot-detector/bd-api:latest
docker push hub.osrsbotdetector.com/bot-detector/bd-api:latest
kubectl rollout restart deploy bd-dev-api