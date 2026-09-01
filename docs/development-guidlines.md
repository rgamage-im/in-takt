## Source Repository
* GitHub repo https://github.com/rgamage-im/in-takt.git

## Development Environment
* Windows 11 machine; the repo now lives natively at `C:\github\in-takt` (was previously developed under WSL Ubuntu — both still work)
* Development testing - run the web app from the checkout above and access it from your Windows browser (or via WSL if you prefer)
* This checkout includes a local Python virtual environment at `venv/`
* Activate it before running Python tooling: `venv\Scripts\Activate.ps1` (PowerShell) / `venv\Scripts\activate` (cmd) / `source venv/bin/activate` (WSL/bash)
* If `python`, `pytest`, or `manage.py` report missing modules, first confirm the shell is using the venv's python (`venv\Scripts\python` on Windows, `venv/bin/python` in WSL)

## Architecture Goals
* Code should be modular whenever possible, for ease of maintenance and extensibility
* Back End API code should be separate from UI code
* Various API services should be separated, i.e. MS Graph, QuickBooks APIs should be developed as separate, independent modules or classes / services
