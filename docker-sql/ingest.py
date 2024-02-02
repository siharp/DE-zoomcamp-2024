# import library used
import pandas as pd 
import argparse
from sqlalchemy import create_engine
import os
from time import time


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db_name = params.db_name
    tbl_name = params.tbl_name
    url = params.url

    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df= next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(0).to_sql(name=tbl_name, con=engine, if_exists='replace')

    df.to_sql(name=tbl_name, con=engine, if_exists='append')

    total_data = len(df)

    while True:

        try:
            time_start = time()
            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=tbl_name, con=engine, if_exists='append')

            total_data += len(df)
            time_end = time()
            print(f'Inserted another chunk, took {time_end - time_start:.3f} seconds, Total data: {total_data} rows')

        except StopIteration:
            print('all data complete ingest to postgres ')
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ingest data to postgres")
    
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db_name', required=True, help='database name for postgres')
    parser.add_argument('--tbl_name', required=True, help='table name for postgres')
    parser.add_argument('--url', required=True, help='url to download dataset')

    args = parser.parse_args()

    main(args)

    

