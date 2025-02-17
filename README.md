# Mennica Migration Script 
Python script that:converts data from Mennica 1.0 to Mennica 2.0 (unmanaged code => managed code), in particular:
- Maps and converts Record Types,
- Maps and converts field names based including namespace,
- Import records in order to guarantee lookup relations,
- Users Rest & Bulk API to automate whole process,
- Matches records based on specific api field name set in config.py

## Setup Python

*1. Install python*

    https://www.python.org/downloads/

*2. Verify if python is properly installed, in terminal type*

    python --version
	
*3. Verify if pip is properly installed, in terminal type*

    pip check

## Build Project

*1. Clone this repository*

*2. Go to repository folder and install requirements*

	pip install -r requirements.txt
	
*3. Stop tracking changes towards config file to prevent leak of access data to org*

	git update-index --skip-worktree config/data_file.json
	
*4. Configure config.py file with login data for source and target orgs.*

## Run script
From console execute 

    python getEditableFields.py