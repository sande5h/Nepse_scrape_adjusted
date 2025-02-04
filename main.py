from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import re
import json
import pandas as pd
import os
import random
from datetime import datetime
import shutil

#get random string of 5 characters

# print(random_word)
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-infobars")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)


def check_for_symbols():
    driver = webdriver.Chrome(options=options)

    try:
        if os.path.exists('symbols/symbols.csv'):
            os.remove('symbols/symbols.csv')
            print('check_for_symbols() -> Old File removed.')

        driver.get("https://nepsealpha.com/traded-stocks")
        time.sleep(2)

        select_element = driver.find_element(By.NAME, 'DataTables_Table_0_length')
        select = Select(select_element)
        select.select_by_value('100')

        def extract_table_data(i):
            table = driver.find_element(By.ID, 'DataTables_Table_0')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            with open(f'symbols/symbols.csv', 'a') as f:
                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    if columns:
                        data = [column.text.replace(',', '') if ',' in column.text else column.text for column in columns]
                        f.write(','.join(data) + '\n')

        for i in range(0, 10):
            next = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_next"]')
            extract_table_data(i)

            if next.get_attribute('class') == 'paginate_button next disabled':
                # print('No more pages left.')
                break
            else:
                button = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_next"]')
                # print('Clicking the next button')
                button.click()

    finally:
        driver.quit()

    columns = ['Symbol', 'Company_Name', 'LTP', 'Share_outstanding', 'Floated_shares', 'Marketcap', 'Floated_Marketcap', 'Nepse_Weight', 'Volume']
    df = pd.read_csv('symbols/symbols.csv', header=None, names=columns)
    df = df[['Symbol', 'Company_Name', 'LTP', 'Marketcap', 'Nepse_Weight']]
    df.to_csv('symbols/symbols.csv', index=False)
    print('check_for_symbols() -> Symbols saved to symbols/symbols.csv')

def historical_data(symbol,folder = 'data'):
    random_word = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://nepsealpha.com/trading/1/history?fsk={random_word}&symbol={symbol}&resolution=1D&pass=ok")
    time.sleep(2)
    page_source = driver.page_source
    match = re.search(r'({"s":.*?})', page_source)
    if match:
        json_data = match.group(1)
        with open(f"response/{symbol}.json", "w", encoding="utf-8") as file:
            file.write(json_data)
    else:
        print(page_source[0:100])
        print("historical_data() -> No JSON data found in the page source.")
        driver.quit()
        return False
    
    driver.quit()

    with open (f'response/{symbol}.json', 'r') as f:
        data = json.load(f)
    if os.path.exists(f'{folder}'):
        pass
    else:
        os.makedirs(f'{folder}')

    if data['s'] == 'ok':
        df = pd.DataFrame(data)
        df.drop(columns='s', inplace=True)
        df.columns = [ 'open', 'high', 'low', 'close', 'volume' , 'timestamp']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df.to_csv(f'{folder}/{symbol}.csv')

    else:
        print("historical_data() -> No data found in the JSON.")

def main():
    check_for_symbols()
    with open('symbols/symbols.csv', 'r') as f:
        for line in f:
            symbol = line.split(',')[0]
            if symbol == 'Symbol':
                continue
            print("main() -> Getting historical data for: ", symbol)
            result = historical_data(symbol)
            if not result:
                print("main() -> Trying again for: ", symbol)
                time.sleep(1)
                historical_data(symbol)
            


def fetch():
    dfn = pd.read_csv("index/NEPSE.csv")
    random_file = select_random_file('data')
    if not random_file:
        print("fetch() -> Running for the first time")
        main()

    else:
        df = pd.read_csv(f'data/{random_file}')
        if df['timestamp'].iloc[-1] == dfn['timestamp'].iloc[-1]:
            print("fetch() -> No New Data")
        else:
            print("fetch() -> New Data Found Running Main")
            main()

def select_random_file(folder):
    files = os.listdir(folder)
    if not files:
        print("select_random_file() -> No files found in the folder.")
        return None
    return random.choice(files)

def backup_data_folder(folder='data'):

    if not os.listdir(folder):
        print("backup_data_folder() -> No data found in the folder.")
        return None

    dfn = pd.read_csv("index/NEPSE.csv")
    backup_filename = f"backup_{dfn['timestamp'].iloc[-1]}"

    # print(backup_filename)
    backup_path = os.path.join('backup', backup_filename)
    
    shutil.make_archive(backup_path, 'zip', folder)
    print(f"backup_data_folder() -> Backup created: {backup_path}")

def unzip():
    dfn = pd.read_csv("index/NEPSE.csv")
    backup_filename = f"backup_{dfn['timestamp'].iloc[-1]}.zip"
    backup_path = os.path.join('backup', backup_filename)
    extract_dir = 'data'

    print(f"unzip() -> Unzipping backup file: {backup_path}")
    if not os.path.exists(backup_path):
        print(f"unzip() -> Backup file does not exist: {backup_path}")
        return
    
    shutil.unpack_archive(backup_path, extract_dir)

def clean_dir( paths = ['response','index','symbols']):
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)

def init_dir(): 
    os.mkdir('data') if not os.path.exists('data') else None
    os.mkdir('backup') if not os.path.exists('backup') else None
    os.makedirs('response') if not os.path.exists('response') else None
    os.makedirs('symbols') if not os.path.exists('symbols') else None
    os.makedirs('index') if not os.path.exists('index') else None
    os.makedirs('backups_month') if not os.path.exists('backups_month') else None

def monthy_backup(): 
    files = os.listdir('backup')
    if not files:
        print("monthy_backup() -> No files found in the folder.")
        return None
    else:
        files.sort()
        for i in range(len(files) - 1 ):
            if files[i].split('_')[1].split('-')[1]  != files[i+1].split('_')[1].split('-')[1]:
                year_month = files[i].split('_')[1].split('-')[0] + '-' + files[i].split('_')[1].split('-')[1]
                os.makedirs(f'backups_month/backup_{year_month}') if not os.path.exists(f'backups_month/backup_{year_month}') else None
                for i in range(len(files) - 1):
                    if files[i].split('_')[1].split('-')[0] + '-' + files[i].split('_')[1].split('-')[1]  == year_month:
                        shutil.move(f'backup/{files[i]}', f'backups_month/backup_{year_month}/{files[i]}')
                backup_files = os.listdir(f'backups_month/backup_{year_month}')
                backup_files.sort()
                #keep only the first backup of the month
                for i in range(1, len(backup_files)):
                    os.remove(f'backups_month/backup_{year_month}/{backup_files[i]}')
                break



time1 = time.time()
init_dir()
historical_data("NEPSE","index")
unzip()
fetch()
backup_data_folder()
monthy_backup()
clean_dir()
time2 = time.time()
print("\nTime taken: ", time2-time1)