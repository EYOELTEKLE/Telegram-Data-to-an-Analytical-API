import os
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from ultralytics import YOLO

# Load environment variables
load_dotenv()

PG_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PG_PORT = os.getenv('POSTGRES_PORT', '5432')
PG_DB = os.getenv('POSTGRES_DB')
PG_USER = os.getenv('POSTGRES_USER')
PG_PASS = os.getenv('POSTGRES_PASSWORD')

IMAGE_DIR = Path('data/raw/telegram_images')
MODEL_NAME = 'yolov8n.pt'  # You can change to yolov8s.pt, yolov8m.pt, etc.

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
    CREATE TABLE IF NOT EXISTS raw.image_detections (
        id BIGSERIAL PRIMARY KEY,
        message_id BIGINT,
        image_path TEXT,
        detected_object_class TEXT,
        confidence_score FLOAT,
        bbox TEXT,
        detection_time TIMESTAMP
    );
    '''
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()

def extract_message_id(image_path):
    # Try to extract message_id from filename (e.g., 123456789.jpg)
    stem = Path(image_path).stem
    try:
        return int(stem)
    except ValueError:
        return None

def main():
    ensure_table()
    model = YOLO(MODEL_NAME)
    image_files = glob.glob(str(IMAGE_DIR / '*' / '*' / '*.jpg'))
    detections = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            for img_path in image_files:
                results = model(img_path)
                for r in results:
                    for box in r.boxes:
                        class_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                        class_name = model.model.names[class_id]
                        message_id = extract_message_id(img_path)
                        cur.execute('''
                            INSERT INTO raw.image_detections 
                            (message_id, image_path, detected_object_class, confidence_score, bbox, detection_time)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (
                            message_id,
                            img_path,
                            class_name,
                            conf,
                            str(bbox),
                            datetime.now()
                        ))
            conn.commit()
    print(f"Processed {len(image_files)} images and stored detections in the database.")

if __name__ == '__main__':
    main()
