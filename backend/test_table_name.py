from app.models.user import TOTPSecret, User
from sqlalchemy.inspection import inspect

# Check the actual table name that SQLAlchemy will use
print(f"TOTPSecret.__tablename__ = {TOTPSecret.__tablename__}")
print(f"User.__tablename__ = {User.__tablename__}")

# Use SQLAlchemy's inspection to verify the table name
totp_mapper = inspect(TOTPSecret)
user_mapper = inspect(User)

print(f"\nSQLAlchemy mapper for TOTPSecret:")
print(f"Table name: {totp_mapper.mapped_table.name}")

print(f"\nSQLAlchemy mapper for User:")
print(f"Table name: {user_mapper.mapped_table.name}")

print("\nThis confirms whether our fix is working correctly.")