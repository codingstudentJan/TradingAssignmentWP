from fastapi import Depends, FastAPI
from sql_app import models
from database_app.database import get_db, engine
import sql_app.models as models
import sql_app.schemas as schemas
from sql_app.repositories import TransactionRepo, CategoryRepo
from sqlalchemy.orm import Session
import uvicorn
from typing import List