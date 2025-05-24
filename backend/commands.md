Из src всё делать

ngrok http 7777

docker build -t website_image:latest .

docker network create myNetwork

docker run --name website_db \
    -p 6432:5432 \
    -e POSTGRES_USER=abcde \
    -e POSTGRES_PASSWORD=abcde \
    -e POSTGRES_DB=website \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:16

docker run --name website_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis:7.4

docker run --name website_back \
    -p 7777:8000 \
    --network=myNetwork \
    website_image


Остановка контейнера бэка

docker stop website_back
docker rm website_back

Удаление образа
docker rmi website_image:latest