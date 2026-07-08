import streamlit as st
import math
from datetime import datetime, timedelta
# timedelta represents how much time has passed(days, hours, minuetes,seconds)
#date works with days, months, years
from datetime import datetime
import sqlite3

# database set up
def init_database():
    # create connection to SQLite database
    conn = sqlite3.connect("mall_parking_system.db")
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()

    # parking sessions tables
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS parking_sessions(
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number_plate TEXT,
                    entry_timestamp DATETIME,
                    exit_timestamp DATETIME,
                    grace_period_applied INTEGER,
                    allocated_slot INTEGER,
                    session_status TEXT
                    ) 
                    """)

    # Payments table
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Payments(
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    amount_kes REAL NOT NULL,
                    payment_timestamp DATETIME NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES parking_sessions(session_id)
                    )
                     """)
    conn.commit()
    conn.close()




# SMS Receipt generation (digital)
def sms_receipt(number_plate, amount_paid, currency, session_id, phone_number):
    return (
        f'\n PARKING RECEIPT\n'
        f'-----------------\n'
        f'Vehicle: {number_plate}\n'
        f'Ticket No.: {session_id}'
        f'Total Paid: {currency} {amount_paid:,.2f}\n'
        f'Status: Settled.\n'
        f'Thank you for visiting!'
    )

# create a function for vehicle entry
def vehicle_check_in(number_plate):
    conn = sqlite3.connect("mall_parking_system.db")
    cursor = conn.cursor()
    # strip to remove any gaps and upper to write in upper case
    number_plate = number_plate.strip().upper()

    # automatic slot allocation
    cursor.execute("""
                   SELECT allocated_slot FROM parking_sessions WHERE session_status = 'Active'
                   """)
    occupied_slots = {row[0] for row in cursor.fetchall()}

    allocated_slots = None
    for slot in range(1, 101):
        if slot not in occupied_slots:
            allocated_slots = slot
            break

    if allocated_slots is None:
        conn.close()
        return 'ERROR: Parking slot is full!'

    # cutoff timestamp for 90 days
    current_time = datetime.now()
    entry_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    ninety_days_time = (current_time - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S.%f')
    
 # Count completed visits for this number plate in the last 90 days
    cursor.execute("""
                   SELECT COUNT (*) FROM parking_sessions
                   WHERE number_plate = ? AND entry_timestamp >= ? AND session_status = "Completed"
                   """, (number_plate, ninety_days_time))
    
    num_of_visits = cursor.fetchone()[0]
    # setting the grace period for loyal and normal customers
    grace_period_applied = 80 if num_of_visits >= 20 else 50
    
    # creating active parking sessions
    cursor.execute("""
                   INSERT INTO parking_sessions (number_plate, entry_timestamp, exit_timestamp, grace_period_applied, allocated_slot, session_status)
                   VALUES (?, ?, NULL, ?, ?, 'Active')
                   """, (number_plate, entry_time_str, grace_period_applied, allocated_slots))
    conn.commit()
    conn.close()

    return f'Success! vehicle {number_plate} registered. Allocated to slot {allocated_slots}. Tier: {'Loyal' if grace_period_applied == 80 else 'Standard'}. Grace Period: {grace_period_applied} minutes allocated.', True

# Create function for vehicle exit
def vehicle_check_out(number_plate, phone_number, simulation_mins=None):
    conn = sqlite3.connect("mall_parking_system.db")
    cursor = conn.cursor()
    number_plate = number_plate.strip().upper()
        
        # get the active session for the vehicle
    cursor.execute("""
                    SELECT session_id, entry_timestamp, grace_period_applied, allocated_slot
                    FROM parking_sessions
                    WHERE number_plate = ? AND session_status = 'Active'
                    """, (number_plate,)) 
    session = cursor.fetchone()

        # safety net to confirm if car checked in
    if not session:
        conn.close()
        return f'Error: No active session found for {number_plate}.', 0, 0, True
        
    # this is the data displayed after vehicle gets to check out
    session_id, entry_timestamp, grace_period_applied, allocated_slot = session
    current_time = datetime.now()
    exit_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')

    if simulation_mins is not None and simulation_mins > 0:
        total_mins = int(simulation_mins)
    else:
        entry_timestamp = datetime.strptime(entry_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        stay_duration = current_time - entry_timestamp
        total_mins = max(0, int(stay_duration.total_seconds() / 60))

    # Step4: billing
    parking_fee = 0

    # 24-hour parking (1440 minutes)
    if total_mins >= 1440:
        days_parked = math.ceil(total_mins / 1440)
        #days_parked stored in minutes
        parking_fee = days_parked * 3000
    else:
        extra_time = total_mins - grace_period_applied
        if extra_time > 0:
            penalty_fee = math.ceil(extra_time / 20)
            parking_fee = penalty_fee * 200
    
    final_amount = float(parking_fee)
    
    cursor.execute("""
        INSERT INTO Payments (session_id, amount_kes, payment_timestamp)
        VALUES (?, ?, ?)
    """, (session_id, final_amount, exit_time_str))
        
    cursor.execute("""
                    UPDATE parking_sessions
                    SET exit_timestamp = ?, session_status = 'Completed'
                    WHERE session_id = ?
                    """, (exit_time_str, session_id))
        
    conn.commit()
    conn.close()

        # process sms deliveries
    receipt_msg = sms_receipt(number_plate, final_amount, session_id, phone_number, allocated_slot)
    return receipt_msg, total_mins, parking_fee

def revenue_report():
    conn = sqlite3.connect('mall_parking_system.db')
    cursor = conn.cursor()

    # total active parked cars
    cursor.execute("""
                   SELECT COUNT(*) FROM parking_sessions WHERE session_status = 'Active'
                   """)
    active_cars = cursor.fetchone()[0] 

    # lifetime revenue collected
    cursor.execute("""
                   SELECT SUM(amount_kes) FROM Payments
                   """)
    total_rev = cursor.fetchone()[0] or 0.0

    # grouped daily revenue list
    cursor.execute("""
                   SELECT 
                        SUBSTR(payment_timestamp, 1, 10) AS payment_date,
                        COUNT(payment_id) AS total_transaction,
                        SUM(amount_kes) AS daily_total
                   FROM Payments
                   GROUP BY payment_date
                   ORDER BY payment_date DESC
                   """)
    daily_rows = cursor.fetchall()
    conn.close()

    return active_cars, total_rev, daily_rows

#streamlit user interface       
def main():
    st.set_page_config(page_title='Mall Parking System.', layout='centered')
    init_database()

    st.title('Automated Mall Parking System')

    tab0, tab1, tab2, tab3 = st.tabs([
        'About System',
        'Vehicle Check-In',
        'Vehicle Check-out',
        'Admin Dashboard and Reports' 
    ])
     
    # front page with details about system
    with tab0:
        st.subheader('Welcome to the Automated Mall Parking System control panel')
        st.markdown("""
                    This automated system manages vehicle entries, exits, grace period applied and multi-currency payments for the mall's parking facilities.
                    """)
        
        # system features
        st.markdown('Core Capabilities')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                        Smart Entry: Assigns numerical parking bays sequentially based on active lot vacancy.\n
                        Loyalty Recognition: Automatically reviews the last 90 days of history to reward frequent visitors.
                        """)
        with col2: 
            st.markdown("""
                        Billing Automation: Computes penalty fees instantly when exceeding allocated timers.\n
                        Live Auditing: Generates analytical overview tables of incoming daily revenue reports.
                        """)
        
        st.write('---')
        st.markdown('Parking Policies and Fee')

        with st.expander('Grace Period Policy'):
            st.write("""
                    The system dynamically awards grace periods based on customer loyalty data over the last 90 days:\n
                    Regular Customers (< 20 visits): 50 Minutes Free Parking.\n
                    Loyal Customers (>= 20 visits): 80 Minutes Free Parking.
                     """)
        with st.expander('Tariff and Penalty Structures'):
            st.write("""
                     Standard Parking Fine: If a vehicle stays past its designated grace period, a fee of KES 200 is charged for every 20-minute block exceeded.\n
                    Long-Term Parking Rate: Vehicles parked for 24 hours or longer are automatically billed at a flat rate of KES 3,000 per day.
                     """)

    #Check in
    with tab1:
        st.header('Register Entry')
        plate_in = st.text_input('Enter enter entering vehicle number plate: ', key='plate_in').strip().upper()
        if st.button('Confirm Check-in', type='primary'):
            if plate_in:
                message, success = vehicle_check_in(plate_in)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                 st.error('Please enter number plate.')
    #Check-out
    with tab2:
        st.header('Process exit and payment')
        plate_out = st.text_input('Enter leaving vehicle number plate: ', key='plate_out').strip().upper()
        phone_num = st.text_input('Enter drivers phone number for receipt: ', key='phone').strip()
        
        st.markdown('---')
        st.caption('Developer Diagnostics Control')
        use_simulation = st.checkbox('Simulate custom parking duration (Time Travel)')
        
        sim_mins = 0
        if use_simulation:
            sim_mins = st.number_input("Enter simulated duration in minutes:", min_value=1, max_value=5000, value=60, step=10)
        st.markdown('---')

        if st.button('Complete check out and pay'):
            if plate_out and phone_num:
                test_mins = sim_mins if use_simulation else None
                receipt_text, duration, fee = vehicle_check_out(plate_out, phone_num, simulation_mins=test_mins)
                if 'Error' in receipt_text:
                    st.error(receipt_text)
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                         st.metric(label="Total Parking Duration", value=f"{duration} Mins")
                    with col2:
                        st.metric(label="Base Fee Calculated", value=f"KES {fee:,.2f}")
                    st.text_area("Digital SMS Receipt Details", value=receipt_text, height=200)
                    st.success(f"Check out complete. Proceed to exit {plate_out}!")
            else:
                st.error("Error: Number plate and phone number cannot be empty.")

        with tab3:
            st.header('System Management Analytics')
            active_cars, total_rev, daily_rows = revenue_report()

            c1, c2 = st.columns(2)
            with c1:
                st.metric(label='Active Vehicles Parked', value=f'{active_cars} / {101} Slots')
        with c2:
            st.metric(label='Total Lifetime Earnings', value=f'KES {total_rev:,.2f}')
            
        st.subheader('Daily Revenue Reports Summary')
        if daily_rows:
            # Format rows nicely into an interactive summary table
            report_data = []
            for row in daily_rows:
                report_data.append({
                    'Date': row[0],
                    'Settled Invoices': row[1],
                    'Total Collected (KES)': f'KES {row[2]:,.2f}'
                })
            st.table(report_data)
        else:
            st.info('No revenue records available in the ledger yet. Complete a check-out to log historical report rows.')
        
if __name__ == "__main__":
    main()
            





# def main_loop():
#     init_database()
#     exchange_rates()

#     # to loop continuously
#     while True:
#         print('\n--- Mall Parking System ---')
#         print('1. Vehicle Check-In')
#         print('2. Vehicle Check-Out and exit')
#         print('3. Exchange rate')
#         print('4. Shut down system terminal')
#         choice = input('\nSelect an option (1-4): ').strip()

#         if choice == "1":
#             number_plate = input('Enter vehicle number plate: ').strip().upper()
#             if number_plate:
#                 vehicle_check_in(number_plate)
#             else:
#                 print('Error: Number plate cannot be empty.')
#         elif choice == "2":
#             number_plate = input('Enter the leaving vehicle number plate: ').strip().upper()    
#             phone_number = input('Enter phone number: ').strip()
#             if number_plate and phone_number:
#                 vehicle_check_out(number_plate, phone_number)
#             else:
#                 print("Error: Number plate and phone number cannot be empty.")
#         elif choice == "3":
#             exchange_rates()
#         elif choice == "4":
#             print("Shutting down the system terminal. Goodbye!")
#             break
#         else:
#             print("Invalid option. Please try again.")

# if __name__ == "__main__":
#     # this is the loop function that handles database tables, APIs and gate menus
#     main_loop()















