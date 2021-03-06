watch:
	dev_appserver.py --host=0.0.0.0 app.yaml

test:
	python -m unittest discover

deploy:
	read -r -p "Version: " VERSION;\
	gcloud app deploy --version=$$VERSION
