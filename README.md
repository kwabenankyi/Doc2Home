# Doc2Home
Project files and report for Doc2Home, a doctors' surgery management system built for my A-Level Computer Science coursework. It scored 100%.

To run the program:

1. recreate virtual environment with instruction:
> "python -m venv venv"

2. run virtual environment
> "venv\Scripts\activate" on Windows OR "source venv/bin/activate" on Mac 

3. install modules with pip:
> "pip install -r requirements.txt"

4. identify the flask app "nea.py"
> "set FLASK_APP=nea.py" on Windows, "export FLASK_APP=nea.py" on Mac

5. run the application, and include " --host:0.0.0.0" at the end of the command to run the app on a local network.
> "flask run"

6. if ImportError is raised, run command "python nea.py" to install uninstalled packages

