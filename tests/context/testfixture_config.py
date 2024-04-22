import os
import tempfile
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY: str = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///' + os.path.join(basedir, 'test.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    TEMP_DIR: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
    FILES_DIR: Path = Path(TEMP_DIR.name)

    @classmethod
    def get_cls(cls):
        cls.TEMP_DIR: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        cls.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(cls.TEMP_DIR.name, 'test.sqlite')
        return cls
