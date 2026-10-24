from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from inventory_core.database import Base

class ActivityLog(Base):
  __tablename__ = "activity_logs"

  id = Column(Integer, primary_key=True, index=True)
  action = Column(String, nullable=False)
  timestamp = Column(DateTime, default=datetime.utcnow)


def log_activity(db, action_text):
  log = ActivityLog(action=action_text)
  db.add(log)
  db.commit()
