# PoETL Makefile
# TODOs:
# * Check if pip3 exists. Install if it doesn't
# * Use pip3 to install 'virtualenv' package
# * source the virtual environment and install dependencies

target: init_dirs init_venv

init_dirs:
	@echo "Initializing directories"
	@mkdir -p output/
	@mkdir -p logs/

init_venv:
	@echo "Initializing venv"
	virtualenv venv
