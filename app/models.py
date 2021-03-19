from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, PrimaryKeyConstraint

Base = declarative_base()

class Estimate(Base):
    __tablename__ = 'estimates'
    state = Column(String)
    year = Column(Integer)
    population = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('state', 'year'),
        {},
    )

    def __repr__(self):
        return "<Estimate(state={}, year={}, population={})>"\
            .format(self.state, self.year, self.population)

class NameJSON(Base):
    __tablename__ = 'name_json'
    name = Column(String)
    data = Column(JSON)
    birth_totals = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('name'),
        {},
    )

    def __repr__(self):
        return "<NameJSON(name={}, data=JSON)>"\
            .format(self.name)