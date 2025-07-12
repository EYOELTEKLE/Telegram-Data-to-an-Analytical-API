from fastapi import FastAPI, Query
from .database import get_db
from .schemas import TopProduct, ChannelActivity, MessageSearchResult
from .crud import (
    get_top_products,
    get_channel_activity,
    search_messages
)
from typing import List

app = FastAPI(title="Telegram Analytical API")

@app.get("/api/reports/top-products", response_model=List[TopProduct])
def top_products(limit: int = 10):
    db = get_db()
    return get_top_products(db, limit)

@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivity)
def channel_activity(channel_name: str):
    db = get_db()
    return get_channel_activity(db, channel_name)

@app.get("/api/search/messages", response_model=List[MessageSearchResult])
def search_messages_api(query: str = Query(..., min_length=1)):
    db = get_db()
    return search_messages(db, query)
