import datetime
import requests
import csv
import pandas as pd
import mysql.connector
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

### NOTES ###
# The SeatGeek API is running on EDT

# SeatGeek API details, where client_id is the username and client_secret is the password
client_id = 'id'
client_secret = 'secret'
data_dir = "C:\\Users\\example_user\\OneDrive\\Desktop\\folder\\"


params = (('client_id', 'client_secret'),)


def get_event_list_jsons():
    def get_event_ids():
        event_ids = []
        while len(event_ids) < 4:
            event_id = input(f"Enter event ID {len(event_ids) + 1} (or type 'DONE' to finish): ")
            if event_id.upper() == 'DONE':
                break
            elif not event_id:
                raise ValueError("Event ID cannot be empty")
            try:
                event_ids.append(int(event_id))
            except ValueError:
                raise ValueError("Event ID must be an integer")
        return event_ids

    def get_event_jsons(event_id_list):
        response_list = []
        for id in event_id_list:
            response_list.append(requests.get(
                f'https://api.seatgeek.com/2/events/{id}?client_id={client_id}&client_secret={client_secret}').json())
        return response_list

    try:
        event_ids = get_event_ids()
        print("Event IDs:", event_ids)  # Print event IDs just for confirmation
        return get_event_jsons(event_ids)
    except ValueError as ve:
        print("Error:", ve)
        return []

jsons = get_event_list_jsons()

# Keys: columns
# Values: data
def get_stats(json_data):
    stats = {'id': json_data['id'], 'title': json_data['title'], 'listing_count': json_data['stats']['listing_count'],
             'lowest_price': json_data['stats']['lowest_price'], 'median_price': json_data['stats']['median_price'],
             'average_price': json_data['stats']['average_price'], 'highest_price': json_data['stats']['highest_price'],
             'announced': json_data['announce_date'], 'event_timestamp': json_data['datetime_local'],
             'current_tme': datetime.datetime.utcnow().isoformat()[:-4]}
    return stats


def get_stats_dict_list(jsons_list):
    dict_list = []
    for i in range(len(jsons_list)):
        dict_list.append(get_stats(jsons_list[i]))
    return dict_list


stats_dict_list = get_stats_dict_list(jsons)
print(stats_dict_list)


def convert_dicts_to_csv(dict_list):
    def get_name():
        name = input("Enter name for creation of csv: ")
        return name

    username = get_name()
    """
    Writes a list of dictionaries to a CSV file, where each dictionary represents a row in the CSV file.
    """
    if not dict_list:
        print("No data to write.")
        return

    # Extract fieldnames from the first dictionary in the list
    fieldnames = dict_list[0].keys()

    with open(f'{username}.csv', 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write each dictionary as a row in the CSV file
        for dictionary in dict_list:
            writer.writerow(dictionary)

convert_dicts_to_csv(stats_dict_list)

# ----------------DATABASE SECTION ---------------- #

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database='database'
)

mycursor = db.cursor()

# Creates a table stats with columns named after the stats dictionary
def create_user_table():
    # Defines a function get_name, gets the name of the discord user and creates a sql table with their data.
    def get_name():
        name = input("Enter name for creation of table: ")
        return name

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="password",
        database='database'
    )

    mycursor = db.cursor()

    mycursor.execute(f"CREATE TABLE {get_name()} (id int, title varchar(250), "
                     "listing_count int,"
                     "lowest_price int,"
                     "median_price int,"
                     "average_price int,"
                     "highest_price int,"
                     "announced varchar(50),"
                     "event_timestamp varchar(50),"
                     "current_tme varchar(50)"
                     ");")



# create_user_table()

# Export data to database
def add_csv_to_db():
    def get_name():
        name = input("Enter name for adding csv to db: ")
        return name

    username = get_name()
    with open(f'{username}.csv', 'r') as file:
        reader = csv.reader(file)
        columns = next(reader)
        # converts query to table=username, VALUES(%s, %s, %s, %s, ... ,%s) SQL syntax
        query = f'INSERT INTO {username}({",".join(columns)}) VALUES({",".join(["%s"] * len(columns))})'
        for data in reader:
            print(f"Successfully Inserted ID {data[0]}, '{data[1]}' into {username} table")
            mycursor.execute(query, data)
            # must use this command to commit the executions to the database
            db.commit()


add_csv_to_db()

def create_df(table_name):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="portal2gunIV!",
        database='price_tracker_stats'
    )

    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM {}".format(table_name))
    table = mycursor.fetchall()
    # figure out how to make this modular
    mycursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'price_tracker_stats' AND table_name = N'{}'
            ORDER BY ordinal_position
    """.format(table_name))
    columns = mycursor.fetchall()

    column_names = [column[0].strip("(),'") for column in columns]
    df = pd.DataFrame(table, columns=column_names)
    return df

# Admin Usage Only
def clear_table(table_name):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="portal2gunIV!",
        database='price_tracker_stats'
    )

    mycursor = db.cursor()
    mycursor.execute("DELETE FROM {}".format(table_name))
    db.commit()
    print("Successfully deleted all entries in {}".format(table_name))


# ----------------PLOTTING---------------- #

def get_data():
    def get_name():
        name = input("Enter name for data retrieval and plotting: ")
        return name

    username = get_name()
    try:

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="portal2gunIV!",
            database='price_tracker_stats'
        )
        mycursor = db.cursor()

        
        query = f"""
            SELECT id, title, lowest_price, current_tme FROM {username} ORDER BY id, current_tme ASC
        """
        
        mycursor.execute(query)

        # Fetch all rows
        rows = mycursor.fetchall()
        # Separate old and new prices, IDs, and titles
        ids = [row[0] for row in rows]
        titles = [row[1] for row in rows]
        lowest_prices = [row[2] for row in rows]
        current_time = [row[3] for row in rows]

        return ids, titles, lowest_prices, current_time

    except mysql.connector.Error as err:
        print("Error:", err)


ids, artists, prices, current_time = get_data()

# creates a dictionary with the relevant details
# Keys: concert/event ids
# Values: artist name, timestamps, and prices of tickets
def plot_stats(list_of_ids, list_of_artists, list_of_prices, list_of_current_time):
    def convert_timestamp(timestamp):
        return timestamp.replace('T', ' ')

    converted_timestamps = [convert_timestamp(timestamp) for timestamp in list_of_current_time]

    artist_data = {}
    for i, _id in enumerate(list_of_ids):
        if _id not in artist_data:
            artist_data[_id] = {'artist': list_of_artists[i], 'timestamps': [], 'prices': []}
        artist_data[_id]['timestamps'].append(converted_timestamps[i])
        artist_data[_id]['prices'].append(list_of_prices[i])

    plt.figure(figsize=(10, 6))

    for _id, data in artist_data.items():
        label = f'{data["artist"]} (ID: {_id})'  # Include ID in the legend label
        plt.plot(data['timestamps'], data['prices'], marker='o', label=label)

    plt.xlabel('Date and Time')
    plt.ylabel('Price')
    plt.title('Lowest Prices over Time by Artist')
    plt.xticks(rotation=45)

    # Configures Legend
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = list(set(labels))
    unique_handles = [handles[labels.index(label)] for label in unique_labels]
    plt.legend(unique_handles, unique_labels, loc='upper left')

    plt.grid(True)
    plt.tight_layout()
    plt.show()


plot_stats(ids, artists, prices, current_time)

# ----------------PREDICTIVE MODELING---------------- #

concert_data = pd.read_csv('stats.csv')

# Convert timestamp columns to numeric values
timestamp_cols = ['announced', 'event_timestamp', 'current_tme']
for col in timestamp_cols:
    concert_data[col] = pd.to_datetime(concert_data[col]).astype('int64') // 10**9

# Drop non-numeric or non-relevant columns
concert_data = concert_data.drop(columns=['id', 'title'])

# Preprocess the data
X = concert_data.drop(columns=['average_price'])  # Features
y = concert_data['average_price']  # Target variable
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Choose a Linear Regression Model
model = LinearRegression()
model.fit(X_train, y_train)

# Generate the Predictive Model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print('Mean Squared Error:', mse)

# Plot

plt.scatter(y_test, y_pred)
plt.xlabel('Actual Prices')
plt.ylabel('Predicted Prices')
plt.title('Actual vs. Predicted Prices')
plt.show()
