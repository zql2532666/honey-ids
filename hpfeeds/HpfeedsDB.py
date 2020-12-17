import sqlite3
from sqlite3 import Error
import json


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
   
    return conn


#def insert_hpfeeds_users(conn, user_credentials):
#    insert_credentials_sql_statement = "INSERT INTO authkeys (owner, ident, secret, pubchans, subchans) VALUES (?,?,?,?,?)"
#    cur = conn.cursor()
#    cur.execute(insert_credentials_sql_statement, (user_credentials["owner"], user_credentials["identifier"], user_credentials["secret"], json.dumps(user_credentials['pubchans']), json.dumps(user_credentials['subchans'])))
#    conn.commit()
#    return cur.lastrowid


#def delete_hpfeeds_users(conn, identifier):
#    delete_credentials_sql_statement = "DELETE FROM authkeys WHERE ident=?"
#    cur = conn.cursor()
#    cur.execute(delete_credentials_sql_statement, (identifier,))
#    conn.commit()
#    return cur.lastrowid


def add_honeynode_hpfeeds_credentials(conn, hpfeeds_identifier, hpfeeds_secret, pubchans):
    sql_statement = "INSERT INTO authkeys (owner, ident, secret, pubchans, subchans) VALUES (?,?,?,?,?)"
    cur = conn.cursor()

    try:
        cur.execute(sql_statement, ('honeyids', hpfeeds_identifier, hpfeeds_secret, json.dumps(pubchans), json.dumps([])))
        conn.commit()
    except Exception as err:
        print(err)

    return cur.lastrowid


if __name__ == '__main__':
    OWNER = "honeyids"
    connection_object = create_connection("sqlite.db")

    '''
    hpfeeds_users = [
        {
            "identifier": "wordpot",
            "owner": "honeyids",
            "secret": "wordpot",
            "subchans": [],
            "pubchans": ["wordpot.events"]
        },

        {
            "identifier":"cowrie",
            "owner": "honeyids",
            "secret": "cowrie",
            "subchans": [],
            "pubchans": ["cowrie.sessions"]
        },

        {
            "identifier":"collector",
            "owner": "honeyids",
            "secret": "collector",
            "subchans": ["wordpot.events", "agave.events", "snort.alerts", "cowrie.sessions", "conpot.events", "elastichoney.events", "shockpot.events", "sticky_elephant.connections", "sticky_elephant.queries"],
            "pubchans": []
  
        },

        {   
            "identifier":"snort",
            "owner": "honeyids",
            "secret": "snort",
            "subchans": [],
            "pubchans": ["snort.alerts"]
        },

        {
            "identifier":"sticky_elephant",
            "owner": "honeyids",
            "secret": "sticky_elephant",
            "subchans": [],
            "pubchans": ["sticky_elephant.connections", "sticky_elephant.queries"]
        }
    ]

    for u in hpfeeds_users:
        last_row_id = insert_hpfeeds_users(connection_object, u)
        print(last_row_id)

    # delete_hpfeeds_users(connection_object, hpfeeds_users[-1]["identifier"])
    '''
