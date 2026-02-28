import sqlite3
from pathlib import Path
import os
import sys
from tqdm import tqdm


def migrate_db(db, schema, replace=True):
    db_path = Path(__file__).parent / db
    schema_path = Path(__file__).parent / schema

    verb = 'replacing' if replace else 'updating'
    print(f'{verb} {db_path}')

    try:
        with open(schema_path, 'r') as FILE:
            text = FILE.read()
        statements = [statement.strip() for statement in text.split(';')]
    except FileNotFoundError:
        print(f'Could not find {schema}')
        exit()

    if replace and os.path.exists(db_path):
        os.remove(db_path)

    with sqlite3.Connection(db_path) as conn:
        cursor = conn.cursor()
        for statement in tqdm(statements):
            try:
                cursor.execute(statement)
                conn.commit()
            except Exception as err:
                print(f'\n{str(err)}\n\nStatement: {statement}')
                continue
            

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Use:\nmigrate_db <db> <schema> <replace | update>\n')
        exit()
    replace = sys.argv[3] == 'replace'
    migrate_db(sys.argv[1], sys.argv[2], replace)

    


    
