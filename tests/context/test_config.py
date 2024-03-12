import os
import tempfile
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMP_DIR = tempfile.TemporaryDirectory()
    FILES_DIR = Path(TEMP_DIR.name)
