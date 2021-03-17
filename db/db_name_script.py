import time
import us

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI
from models import Base, NameEntry

# Database and webdriver variables
engine = create_engine(DATABASE_URI, executemany_mode='batch')
Session = sessionmaker(bind=engine)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.ssa.gov/oact/babynames/state/')

# Range variables
states = [ state.abbr for state in us.states.STATES ] + ['DC']
year_range = (2019, 1960)


#############################
# Selenium Scrape Functions #
#############################
def nav_to_state(state):
    state_elem = driver.find_element_by_id('state')
    select = Select(state_elem)
    select.select_by_value(state)
    go_btn = driver.find_element_by_xpath('/html/body/main/section[2]/div/div[2]/form[1]/p/input')
    go_btn.click()

def nav_to_next_year(year):
    form_field = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[1]/form/p[1]/input')
    form_field.clear()
    form_field.send_keys(year)
    go_btn = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[1]/form/p[2]/input')
    go_btn.click()

def nav_to_next_state(state, first_year):
    form_field = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[1]/form/p[1]/input')
    form_field.clear()
    form_field.send_keys(first_year)
    state_elem = driver.find_element_by_id('state')
    select = Select(state_elem)
    select.select_by_value(state)
    go_btn = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[1]/form/p[2]/input')
    go_btn.click()

def get_state():
    state_elem = driver.find_element_by_id('state')
    select = Select(state_elem)
    state_field = select.first_selected_option.text
    
    return state_field

def get_year():
    form_field = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[1]/form/p[1]/input')
    year_field = form_field.get_attribute('value')
    
    return year_field


##################
# Clean Database #
##################
def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


###############
# Main Script #
###############
def main():

    first_year = year_range[0]
    last_year = year_range[1]

    for i in range(len(states)):
        s = Session()
        current_state = states[i]
        if i == 0:
            nav_to_state(current_state)
        
        for j in range(first_year, last_year - 1, -1):
            rows = [
                driver.find_element_by_xpath(f'/html/body/table[2]/tbody/tr/td[2]/p[2]/table/tbody/tr[{i}]')
                for i in range(2, 102)
            ]
            state_field = get_state()
            year_field = get_year()
            
            objects = []
            for row in rows:
                values = row.text.split()
                
                male_name = NameEntry(
                    state=state_field,
                    year=year_field,
                    name=values[1],
                    gender='Male',
                    births=''.join(values[2].split(','))
                )
                
                female_name = NameEntry(
                    state=state_field,
                    year=year_field,
                    name=values[3],
                    gender='Female',
                    births=''.join(values[4].split(','))
                )
                objects.append(male_name)
                objects.append(female_name)
            
            s.bulk_save_objects(objects)
            s.commit()
            
            if j != last_year:
                time.sleep(1)
                nav_to_next_year(j-1)

        s.close()   
        
        if i < len(states) - 1:
            time.sleep(1)
            next_state = states[i+1]
            nav_to_next_state(next_state, first_year)
            
    driver.close()

if __name__ == '__main__':
    main()