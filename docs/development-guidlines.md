## Source Repository
* GitHub repo https://github.com/rgamage-im/in-takt.git

## Development Environment
* Windows 11 machine, running WSL Ubuntu
* Scripts and app are stored and run on the Ubuntu machine
* Files are mapped to a windows folder, accessed by VS Code, for editing source files
* Development testing - run web app in WSL instance, access from Windows 11 browser

## Architecture Goals
* Code should be modular whenever possible, for ease of maintenance and extensibility
* Back End API code should be separate from UI code
* Various API services should be separated, i.e. MS Graph, QuickBooks APIs should be developed as separate, independent modules or classes / services
