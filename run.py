'''
Entry point
'''

# run.py

import os

from hm_api.app import app

if __name__ == "__main__":
    app.run(os.getenv('FLASK_RUN_HOST', "0.0.0.0"), port=int(
        os.getenv('FLASK_RUN_PORT', '5000')), debug=os.getenv('DEBUG'))
