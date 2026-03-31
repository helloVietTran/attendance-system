import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
OVER_TIME_MONTHLY_LIMIT_MINS = int(os.getenv("OVERTIME_MONTHLY_LIMIT_MINS", 2400))
OVER_TIME_YEARLY_LIMIT_MINS = int(os.getenv("OVERTIME_YEARLY_LIMIT_MINS", 12000))