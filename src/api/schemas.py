from pydantic import BaseModel
from typing import List, Optional

class TopProduct(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivity(BaseModel):
    channel_name: str
    daily_activity: List[dict]  # e.g., [{"date": "2025-07-10", "count": 123}]

class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    date: str
