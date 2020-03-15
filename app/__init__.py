from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_cors import CORS

app = Flask(__name__)
# cors = CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

abr_files = ['/out_5k.mp4', '/out_2k.mp4', '/out_1k.mp4']
frag_files = ['/out_5k_frag.mp4', '/out_2k_frag.mp4', '/out_1k_frag.mp4']

app.config['UPLOAD_FOLDER'] = 'content'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['DASH_VIDEO_5000'] = " -c:v libx264 -maxrate 5000k -bufsize 10000k -f mp4 -y "
app.config['DASH_VIDEO_2000'] = " -c:v libx264 -maxrate 2000k -bufsize 4000k -f mp4 -y "
app.config['DASH_VIDEO_1000'] = " -c:v libx264 -maxrate 1000k -bufsize 2000k -f mp4 -y "
app.config['FFMPEG_PATH'] = 'ffmpeg -i '
app.config['MP4_FRAG'] = "bin/mp4fragment "
app.config['MP4_DASH'] = "bin/mp4dash "
app.config['MANIFEST_SUFFIX'] = '/parts'
app.debug = True

from app import routes, models
