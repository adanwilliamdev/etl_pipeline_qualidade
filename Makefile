.PHONY: install test run dry-run docker-build docker-run clean

install:
	pip install -r requirements.txt

test:
	pytest -v

run:
	python main.py

dry-run:
	python main.py --dry-run

docker-build:
	docker build -t etl-qualidade .

docker-run:
	docker run --rm -v $(PWD)/data:/app/data -v $(PWD)/logs:/app/logs etl-qualidade

clean:
	rm -rf data/processed/* data/quarantine/* logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} +
