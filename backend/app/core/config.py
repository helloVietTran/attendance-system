import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = os.getenv("DB_HOST", "localhost") # Nếu không tìm thấy, dùng default
DB_USER: str = os.getenv("DB_USER", "root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DB_NAME: str = os.getenv("DB_NAME", "attendance_db")
DB_PORT: str = os.getenv("DB_PORT", "3306")

# DB local:
# DATABASE_URL = os.getenv("DATABASE_URL")

# DB deployment:
DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SECRET_KEY = os.getenv("SECRET_KEY")
OVER_TIME_MONTHLY_LIMIT_MINS = int(os.getenv("OVERTIME_MONTHLY_LIMIT_MINS", 2400))
OVER_TIME_YEARLY_LIMIT_MINS = int(os.getenv("OVERTIME_YEARLY_LIMIT_MINS", 12000))
OVERTIME_DAILY_LIMIT_MINS=int(os.getenv("OVERTIME_DAILY_LIMIT_MINS", 240))
