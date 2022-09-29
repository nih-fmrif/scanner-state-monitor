
#!/bin/sh

export FLASK_APP=./publish_scanner_state_app/index.py
export FLASK_ENV=development

# -h 0.0.0.0 runs service on *ALL* network interfaces.
# Withouth this, the app should just run on 'localhost'

flask run -h 0.0.0.0

