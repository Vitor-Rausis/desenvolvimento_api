from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


Base = declarative_base()

class User(Base):
