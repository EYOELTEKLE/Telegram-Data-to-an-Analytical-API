from sqlalchemy.orm import Session
from sqlalchemy import text
from .schemas import TopProduct, ChannelActivity, MessageSearchResult
from typing import List

# Adjust table/column names as needed for your dbt models

def get_top_products(db: Session, limit: int) -> List[TopProduct]:
    sql = text('''
        SELECT product_name, COUNT(*) as mention_count
        FROM fct_messages
        WHERE product_name IS NOT NULL
        GROUP BY product_name
        ORDER BY mention_count DESC
        LIMIT :limit
    ''')
    result = db.execute(sql, {"limit": limit})
    return [TopProduct(product_name=row[0], mention_count=row[1]) for row in result]

def get_channel_activity(db: Session, channel_name: str) -> ChannelActivity:
    sql = text('''
        SELECT d.channel_name, m.date::date, COUNT(*)
        FROM fct_messages m
        JOIN dim_channels d ON m.channel_id = d.channel_id
        WHERE d.channel_name = :channel_name
        GROUP BY d.channel_name, m.date::date
        ORDER BY m.date::date
    ''')
    result = db.execute(sql, {"channel_name": channel_name})
    daily_activity = [{"date": str(row[1]), "count": row[2]} for row in result]
    return ChannelActivity(channel_name=channel_name, daily_activity=daily_activity)

def search_messages(db: Session, query: str) -> List[MessageSearchResult]:
    sql = text('''
        SELECT m.message_id, d.channel_name, m.message_text, m.date
        FROM fct_messages m
        JOIN dim_channels d ON m.channel_id = d.channel_id
        WHERE m.message_text ILIKE :query
        ORDER BY m.date DESC
        LIMIT 100
    ''')
    result = db.execute(sql, {"query": f"%{query}%"})
    return [MessageSearchResult(message_id=row[0], channel_name=row[1], message_text=row[2], date=str(row[3])) for row in result]
