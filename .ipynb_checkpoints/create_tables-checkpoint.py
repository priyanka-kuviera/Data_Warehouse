import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    #conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    #cur = conn.cursor()
    
    try:
        conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        '''conn = psycopg2.connect("host=dwhcluster.cppsmpgjzkzy.us-west-2.redshift.amazonaws.com dbname=dwh user=dwhuser password=Passw0rd")'''
    except psycopg2.Error as e: 
        print("Error: Could not make connection to the Postgres database")
        print(e)
    
    try: 
        cur = conn.cursor()
    except psycopg2.Error as e: 
        print("Error: Could not get cursor to the Database")
        print(e)
    
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()