from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa

DATABASE = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
ENGINE = sa.create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
)

maker = sessionmaker(bind=ENGINE)

# modelで使用する
# Base = declarative_base()
# Base.query = Session().query_property()
