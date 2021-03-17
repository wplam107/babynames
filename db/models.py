from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, PrimaryKeyConstraint

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

class StateEntry(Base):
    __tablename__ = 'state_pop'
    state = Column(String)
    year = Column(Integer)
    population = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('state', 'year'),
        {},
    )

    def __repr__(self):
        return "<StateEntry(state={}, year={}, population={})>"\
            .format(self.state, self.year, self.population)

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
    __table_args__ = (
        PrimaryKeyConstraint('name'),
        {},
    )

    def __repr__(self):
        return "<NameJSON(name={}, data=JSON)>"\
            .format(self.name)