from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint

Base = declarative_base()

class NameEntry(Base):
    __tablename__ = 'babynames'
    state = Column(String)
    year = Column(Integer)
    name = Column(String)
    gender = Column(String)
    births = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('state', 'year', 'name', 'gender'),
        {},
    )

    def __repr__(self):
        return "<NameEntry(state={}, year={}, name={}, gender={}, births={})>"\
            .format(self.state, self.year, self.name, self.gender, self.births)
