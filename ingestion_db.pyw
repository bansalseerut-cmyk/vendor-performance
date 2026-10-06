import os
import time
import gc
import logging
import pandas as pd
from sqlalchemy import create_engine

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine = create_engine(
    "mysql+pymysql://root:password@localhost:3306/inventory"
)


def ingest_db(df, table_name, engine):
    '''this function will ingest the dataframe into database table'''
    df.to_sql(table_name, con=engine, if_exists='replace', index=False, chunksize=10000)


def ingest_csv_in_chunks(file_path, table_name, engine, chunksize=50000):
    '''this function reads and inserts a large CSV in small pieces to avoid high RAM usage'''
    first_chunk = True
    total_rows = 0
    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        chunk.to_sql(
            table_name,
            con=engine,
            if_exists='replace' if first_chunk else 'append',
            index=False
        )
        first_chunk = False
        total_rows += len(chunk)
        logging.info(f'{table_name}: {total_rows} rows inserted so far')
        del chunk
        gc.collect()
    logging.info(f'Finished ingesting {table_name}: {total_rows} total rows')


def load_raw_data():
    '''this function will load the CSVs as dataframe and ingest into db'''
    start = time.time()
    for file in os.listdir('data'):
        if '.csv' in file:
            table_name = file[:-4]
            try:
                logging.info(f'Ingesting {file} in db')
                # use chunked reading for large files to avoid MemoryError
                ingest_csv_in_chunks('data/' + file, table_name, engine)
                logging.info(f'Successfully ingested {file}')
            except Exception as e:
                logging.error(f'Failed to ingest {file}: {e}')
    end = time.time()
    total_time = (end - start) / 60
    logging.info('----------------Ingestion Complete------------')
    logging.info(f'\nTotal Time Taken: {total_time} minutes')


if __name__ == '__main__':
    load_raw_data()