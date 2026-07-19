
build:
	docker compose build

up:
	docker compose up

run:
	docker compose up --build

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build

logs:
	docker logs -f load_balancer

rep:
	curl http://localhost:5000/rep

analysis:
	python analysis.py

analysis2:
	python analysis_A2.py

clean:
	docker compose down --volumes --remove-orphans
	docker system prune -f