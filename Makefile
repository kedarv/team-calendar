.PHONY: install data assets build clean

install:
	( \
	   source venv/bin/activate; \
	   pip install -r requirements.txt; \
	)

data:
	python main.py

assets:
	yarn --cwd ./frontend build 

build: data assets

clean:
	rm -rf venv
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete