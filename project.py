# import streamlit as st
import math
from datetime import datetime, timedelta
# timedelta represents how much time has passed(days, hours, minuetes,seconds)
#date works with days, months, years
import requests
from datetime import datetime
import sqlite3

# database set up
def init_database():
    # create connection to SQLite database
    conn = sqlite3.connect("mall_parking_system.db")
    # enforce foreign key
    conn.execute("PRAGMA foreign_keys = ON")
    # try and except to throw an error when you try to insert a child record without a matching parent record
    try:
        conn.execute("PRAGMA foreign_keys = ON")
    except sqlite3.IntegrityError as e:
        print(f"Blocked! invalid data! Error: {e}")
    cursor = conn.cursor()

# parking sessions tables
    cursor.execute("""
               CREATE TABLE IF NOT EXISTS parking_sessions(
               session_id INTEGER PRIMARY KEY AUTOINCREMENT,
               number_plate TEXT,
               entry_timestamp DATETIME,
               exit_timestamp DATETIME,
               grace_period_applied INTEGER,
               session_status TEXT
               ) 
               """)
    conn.commit()

    #Exchange rate table
    cursor.execute("""
               CREATE TABLE IF NOT EXISTS Exchange_rate(
               rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
               currency_code TEXT,
               rate_to_kes REAL,
               last_updated DATETIME
               )
               """)
    conn.commit()

    # Payments table
    cursor.execute("""
               CREATE TABLE IF NOT EXISTS Payments(
               payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
               session_id INTEGER,
               amount_kes REAL NOT NULL,
               currency_used TEXT NOT NULL,
               amount_paid_foreign REAL NOT NULL,
               exchange_rate REAL NOT NULL,
               payment_timestamp DATETIME NOT NULL,
               FOREIGN KEY (session_id) REFERENCES parking_sessions(session_id)
               )
               """)
    conn.commit()
    conn.close()

# foreign currency exchange to kes
#to fetch latest conversion rates from frankfurter and save to exchange rates table
def exchange_rates():
    api_url = f'https://api.frankfurter.dev/v2/rates?base=KES'
    print('Fetching latest exchange rates')

    # initialize variables
    usd_rate = None
    eur_rate = None

    # use try and except
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print('Raw API data received: ', data)

            # check if it is a list and unpack the first item
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            # extract kes worth against foreign money
            rates = data.get('rate', {})

            if isinstance(rates, dict):
                usd_rate = rates.get('USD')
                eur_rate = rates.get('EUR')
    
            # connect to database to log in fresh prices
            if usd_rate is not None and eur_rate is not None:
                conn = sqlite3.connect('mall_parking_system.db')
                cursor = conn.cursor()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # insert data updating rows 
                cursor.execute("""
                               INSERT OR REPLACE INTO Exchange_rate (currency_code, rate_to_kes, last_updated)
                               VALUES (?, ?, ?)
                               """, ('USD', usd_rate, current_time))
                cursor.execute("""
                                INSERT OR REPLACE INTO Exchange_rate (currency_code, rate_to_kes, last_updated)
                                VALUES (?, ?, ?)
                                """, ('EUR', eur_rate, current_time))
                conn.commit()
                #lock changes permanently
                conn.close()
                print('exchange_rates updated!')
                print(f'1 KES = {usd_rate} USD | 1 KES = {eur_rate} EUR')
                return
         
            print('API responded but rates are missing.')
    except requests.RequestException as e:
        # incase of a network error
        print(f'Error: Could not connect to frankfurter API ({e}). System defaults to last cached database rates')


# SMS Receipt generation (digital)
def sms_receipt(number_plate, amount_paid, currency, session_id, phone_number):
    message = (
        f'\n PARKING RECEIPT\n'
        f'Vehicle: {number_plate}\n'
        f'Ticket No.: {session_id}'
        f'Paid: {currency} {amount_paid:,.2f}\n'
        f'Status: Settled.\n'
        f'Thank you for visiting!'
    )
    print(f'\n [SMS sent to {phone_number}]: ')
    print('-' * 35 + message + '\n' + '-' * 35)


# create a function for vehicle entry
def vehicle_check_in(number_plate):
    conn = sqlite3.connect("mall_parking_system.db")
    cursor = conn.cursor()

    # strip to remove any gaps and upper to write in upper case
    number_plate = number_plate.strip().upper()

    # cutoff timestamp for 90 days
    current_time = datetime.now()
    ninety_days_time = current_time - timedelta(days=90)
    
 # Count completed visits for this number plate in the last 90 days
    cursor.execute("""
                   SELECT COUNT (*) FROM parking_sessions
                   WHERE number_plate = ?
                   AND entry_timestamp >= ?
                   AND session_status = "Completed"
                   """, (number_plate, ninety_days_time))
    
    num_of_visits = cursor.fetchone()[0]

    # setting the grace period for loyal and normal customers
    if num_of_visits >= 20:
        grace_period_applied = 80
        # initial 50 minutes grace period plus the extra 30 minutes 
        print(f"Loyal customer! with {num_of_visits} visits. Total grace period is 80 minutes.")
    else:
        grace_period_applied = 50
        print(f"Normal customer with {num_of_visits} visits. Total grace period is 50 minutes.")
    
    # creating active parking sessions
    cursor.execute("""
                   INSERT INTO parking_sessions
                   (number_plate, entry_timestamp, exit_timestamp, grace_period_applied, session_status)
                   VALUES (?, ?, NULL, ?, 'Active')
                   """, (number_plate, current_time, grace_period_applied))
    conn.commit()

    print(f"Vehicle {number_plate} checked in successfully at {current_time.strftime('%Y-%m-%d %H:%M:%S')}.\n")


# Create function for vehicle exit
def vehicle_check_out(number_plate, phone_number):
    conn = sqlite3.connect("mall_parking_system.db")
    cursor = conn.cursor()

    number_plate = number_plate.strip().upper()
        
        # get the active session for the vehicle
    cursor.execute("""
                       SELECT session_id, entry_timestamp, grace_period_applied
                       FROM parking_sessions
                       WHERE number_plate = ? AND session_status = 'Active'
                       """, (number_plate,)) 
    session = cursor.fetchone()

        # safety net to confirm if car checked in
    if not session:
        print(f'Error: No active session found for {number_plate}!')
        conn.close()
        return
        
    # this is the data displayed after vehicle gets to check out
    session_id, entry_timestamp, grace_period_applied = session
    
    #convert string back to python datetime 
    entry_timestamp = datetime.strptime(entry_timestamp, '%Y-%m-%d %H:%M:%S.%f')
    current_time = datetime.now()

    # calculate total time stay in minutes
    stay_duration = current_time - entry_timestamp
    total_mins = int(stay_duration.total_seconds() / 60)
    print(f'`Total parking time: {total_mins} minutes.')

    # Step4: billing
    parking_fee = 0

    # 24-hour parking (1440 minutes)
    if total_mins >= 1440:
        days_parked = math.ceil(total_mins / 1440)
        #days_parked stored in minutes
        parking_fee = days_parked * 3000
        print(f'Long term parking: Checked in {days_parked} ago, total fee is {parking_fee}')
    else:
        extra_time = total_mins - grace_period_applied
        if extra_time > 0:
            penalty_fee = math.ceil(extra_time / 20)
            parking_fee = penalty_fee * 200
            print(f'Exceeded grace period by {extra_time} minutes, a {penalty_fee} fine to be paid. ')
        else:
            print(f'Within grace period. Parking is free!')

        # currenvy conversion selection
    choice = 'KES'
    rate_row = None
    chosen_currency = 'KES'
    final_amount = parking_fee
    applied_rate = 1.0
    
    if parking_fee > 0:
        print(f'Balance Due: KES {parking_fee:,.2f}')
        choice = input("Select checkout currency (KES, USD, EUR): ").strip().upper()
        
        if choice in ['USD', 'EUR']:
            cursor.execute('SELECT rate_to_kes FROM Exchange_Rate WHERE currency_code = ?', (choice,))
            rate_row = cursor.fetchone()
            
            if rate_row:
                applied_rate = rate_row[0]
                chosen_currency = choice
                final_amount = parking_fee * applied_rate
            else:
                print(f'Exchange rates for {choice} not loaded. Defaulting transaction to KES.')

        print(f'Total fee: {chosen_currency} {final_amount:,.2f}')

        #update database
        now = datetime.now()
        checkout_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    
        cursor.execute("""
            INSERT INTO Payments (session_id, amount_kes, currency_used, amount_paid_foreign, exchange_rate, payment_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, parking_fee, chosen_currency, final_amount, applied_rate, checkout_time))
        
        cursor.execute("""
                       UPDATE parking_sessions
                       SET exit_timestamp = ?, session_status = 'Completed'
                       WHERE session_id = ?
                       """, (current_time, session_id))
        
        conn.commit()
        conn.close()

        # process sms deliveries
        sms_receipt(number_plate, final_amount, chosen_currency, session_id, phone_number)
        print(f'Check out complete. Proceed to exit {number_plate}!\n')

def main_loop():
    init_database()
    exchange_rates()

    # to loop continuously
    while True:
        print('\n--- Mall Parking System ---')
        print('1. Vehicle Check-In')
        print('2. Vehicle Check-Out and exit')
        print('3. Exchange rate')
        print('4. Shut down system terminal')
        choice = input('\nSelect an option (1-4): ').strip()

        if choice == "1":
            number_plate = input('Enter vehicle number plate: ').strip().upper()
            if number_plate:
                vehicle_check_in(number_plate)
            else:
                print('Error: Number plate cannot be empty.')
        elif choice == "2":
            number_plate = input('Enter the leaving vehicle number plate: ').strip().upper()    
            phone_number = input('Enter phone number: ').strip()
            if number_plate and phone_number:
                vehicle_check_out(number_plate, phone_number)
            else:
                print("Error: Number plate and phone number cannot be empty.")
        elif choice == "3":
            exchange_rates()
        elif choice == "4":
            print("Shutting down the system terminal. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    # this is the loop function that handles database tables, APIs and gate menus
    main_loop()















