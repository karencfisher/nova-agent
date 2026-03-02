import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from pathlib import Path
import json

from repositories.core_memory import CoreMemory
from DB.migrate import migrate_db
from DB.nova_db import NovaDB


def setUpModule():
    migrate_db('test_db.db', 'schema.sql', replace=True)
    CoreMemory.dbn = NovaDB('test_db.db')