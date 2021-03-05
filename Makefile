create-env:
	conda update conda --all -y
	conda create "$(shell basename $(CURDIR))" python=3.8

activate-env:
	conda activate $(shell basename $(CURDIR))

run:
	conda activate $(shell basename $(CURDIR)) && python python/audio_analysis.py