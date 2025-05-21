# ============================================================================
# We are using SQLAlchemy, to utilize its ORM functionality
# Which helps to map Python Classes into Actual database tables
# Example: Class Bus -> BUS Table in the database
# ============================================================================


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ===============================
# Set Up the SQLAlchemy Database 
# ===============================

# Step 1: We need to provide the database we are using - in our case it is SQLite - and path to the database file/server
SQL_ALCHEMY_DATABASE_URL = "sqlite:///aigul.db"

# Step 2: We need to create an engine for the databse to operate. For that provide the URL of the database,
#         check_same_thread = False enbales different threads to operate with the database(if multiple threads are active)
Engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Step 3: We need to create a Session(which sets connection with the database and supports its operations) and bind the
#         engine that we created above to the Session
SessionLocal = sessionmaker(bind=Engine, autocommit=False, autoflush=False)

# Step 4: We need to create a Base. Base enables to create actual SQL Tables as Python classes. Example: Class SomeTable(Base)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

