install:
	#install commands
	pip install --upgrade pip &&\
		pip install -r requirements/local.txt
lint:
	#flake 8
test:
	#test
deploy:
	#deploy
all: install lint test deploy