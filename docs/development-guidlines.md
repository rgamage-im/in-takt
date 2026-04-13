## Source Repository
* GitHub repo https://github.com/rgamage-im/in-takt.git

## Development Environment
* Windows 11 machine, running WSL Ubuntu
* Scripts and app are stored and run on the Ubuntu machine
* Files are mapped to a windows folder, accessed by VS Code, for editing source files
* Development testing - run web app in WSL instance, access from Windows 11 browser
* This checkout includes a local Python virtual environment at `venv/`
* Activate it before running Python tooling: `source venv/bin/activate`
* If `python`, `pytest`, or `manage.py` report missing modules, first confirm the shell is using `venv/bin/python`

## Architecture Goals
* Code should be modular whenever possible, for ease of maintenance and extensibility
* Back End API code should be separate from UI code
* Various API services should be separated, i.e. MS Graph, QuickBooks APIs should be developed as separate, independent modules or classes / services
