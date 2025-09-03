from sqlalchemy import Column, Integer, String, Text, BigInteger
from db import Base

class Query(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String, unique=True, index=True)
    query_text = Column(Text)
    timestamp = Column(String)
    total_slot_ms = Column(BigInteger)
    total_bytes_processed = Column(BigInteger)
    total_rows = Column(Integer)
