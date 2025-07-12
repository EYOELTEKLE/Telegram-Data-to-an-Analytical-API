import os
import json
import glob
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

PG_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PG_PORT = os.getenv('POSTGRES_PORT', '5432')
PG_DB = os.getenv('POSTGRES_DB')
PG_USER = os.getenv('POSTGRES_USER')
PG_PASS = os.getenv('POSTGRES_PASSWORD')

RAW_DATA_PATH = Path('data/raw/telegram_messages')

# Connect to PostgreSQL
def get_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASS
    )

def ensure_table():
    ddl = '''
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        id BIGSERIAL PRIMARY KEY,
        message_id BIGINT,
        channel VARCHAR(255),
        message_text TEXT,
        date TIMESTAMP,
        from_id VARCHAR(255),
        raw_json JSONB
    );
    '''
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()

def extract_fields(msg):
    return {
        'message_id': msg.get('id'),
        'channel': msg.get('peer_id', {}).get('channel_id'),
        'message_text': msg.get('message'),
        'date': msg.get('date'),
        'from_id': msg.get('from_id', {}).get('user_id'),
        'raw_json': json.dumps(msg, default=str)
    }

def load_messages():
    ensure_table()
    files = glob.glob(str(RAW_DATA_PATH / '*' / '*.json'))
    total_inserted = 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            for file in files:
                channel = Path(file).stem
                with open(file, 'r', encoding='utf-8') as f:
                    msgs = json.load(f)
                for msg in msgs:
                    fields = extract_fields(msg)
                    cur.execute('''
                        INSERT INTO raw.telegram_messages (message_id, channel, message_text, date, from_id, raw_json)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (message_id, channel) DO NOTHING
                    ''', (
                        fields['message_id'],
                        channel,
                        fields['message_text'],
                        fields['date'],
                        fields['from_id'],
                        fields['raw_json'],
                    ))
                    total_inserted += 1
        conn.commit()
    print(f"Inserted {total_inserted} messages into raw.telegram_messages.")

if __name__ == '__main__':
    load_messages()
