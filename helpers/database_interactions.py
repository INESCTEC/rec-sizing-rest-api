import os
import sqlite3


def connect_to_sqlite_db() -> (sqlite3.Connection, sqlite3.Cursor):
    """
    Function to return the connection and cursor to the SQLite database.
    :return:
    """
    # Define the path to the database file
    db_path = r'helpers/orders.db'

    # Connect to the SQLIte database
    # If the database doesn't exist, it will be created
    conn = sqlite3.connect(db_path, check_same_thread=False)
    curs = conn.cursor()

    # Check if the database file just got created
    if os.path.getsize(db_path) == 0:
        # The database file did not exist before, so we need to create the tables

        # TO STORE ORDERS ##############################################################################################
        # Create the Orders table
        curs.execute('''
        CREATE TABLE Orders (
        order_id TEXT PRIMARY KEY,
        processed BOOLEAN,
        error TEXT,
        message TEXT
        )
        ''')

        # TO STORE MILP OUTPUTS ########################################################################################
        # Create the General_MILP_Outputs, for single scalar values + the status of the MILP solution
        curs.execute('''
        CREATE TABLE General_MILP_Outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        objective_value REAL,
        milp_status TEXT,
        total_rec_cost REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')

        # Create the Individual_Costs, for main individual outputs
        curs.execute('''
        CREATE TABLE Individual_Costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        meter_id TEXT,
        individual_cost REAL,
        individual_savings REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')
        # Create the Meter_Costs, for outputs that are dependent on the meter ID but not time-varying
        curs.execute('''
        CREATE TABLE Meter_Costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        meter_id TEXT,
        meter_cost REAL,
        meter_savings REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')

        # TO STORE Investments Outputs ########################################################################################
        # Create the Meter_Investment_Outputs
        curs.execute('''
        CREATE TABLE Meter_Investment_Outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        meter_id TEXT,
        individual_cost REAL,
        individual_savings REAL,
        installed_pv REAL,
        installed_storage REAL,
        total_pv REAL,
        total_storage REAL,
        contracted_power REAL,
        retailer_exchange_costs REAL,
        sc_tariffs_costs REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')

        # TO STORE LEM Prices ########################################################################################
        # Create the Lem_Prices
        curs.execute('''
        CREATE TABLE Lem_Prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        datetime TEXT,
        value REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')

        # TO STORE Self Consumption Tariffs ########################################################################################
        # Create the Pool_Self_Consumption_Tariffs
        curs.execute('''
        CREATE TABLE Pool_Self_Consumption_Tariffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        datetime TEXT,
        self_consumption_tariff REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')


        # Create the Meter_Operation_Inputs, for the meter-dependent, time-varying inputs used to feed the MILP
        curs.execute('''
        CREATE TABLE Meter_Operation_Inputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        meter_id TEXT,
        datetime TEXT,
        energy_generated REAL,
        energy_consumed REAL,
        buy_tariff REAL,
        sell_tariff REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')

        # Create the Meter_Operation_Outputs, for the meter-dependent, time-varying outputs from the MILP
        curs.execute('''
        CREATE TABLE Meter_Operation_Outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        meter_id TEXT,
        datetime TEXT,
        energy_surplus REAL,
        energy_supplied REAL,
        energy_purchased_lem REAL,
        energy_sold_lem REAL,
        net_load REAL,
        bess_energy_charged REAL,
        bess_energy_discharged REAL,
        bess_energy_content REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
        )
        ''')




    return conn, curs
