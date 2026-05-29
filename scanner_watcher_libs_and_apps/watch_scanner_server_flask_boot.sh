
#!/bin/sh

export FLASK_APP=./watch_scanner_server_flask.py
export FLASK_ENV=development

# flask run -h 0.0.0.0

# -h 0.0.0.0 runs service on *ALL* network interfaces.

flask run

# Withouth this, the app should just run on 'localhost'

