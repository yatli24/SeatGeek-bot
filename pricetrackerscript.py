import datetime
import requests
import csv
import pandas as pd
import mysql.connector
from matplotlib import pyplot as plt
import numpy as np

# TODO #
# plotting works if data is incomplete, i.e if a user tracks 4 events ,then decides to track 2 events, the graph works
# clear data automatically that is less than 24 hours apart
# implement adding data and tables to database directly, instead of reading a csv, because that happens locally
# implement an update function, updates existing user's events
# implement remove events
# figure out how to hold a unique table for each user in sql database
# figure out how to hold multiple user data on a discord bot
# if possible, move all of this to the cloud and automate updating (SQL server, discord bot)
# perhaps other data in the scrape could be useful, such as number of listings, date of event
# maybe make something useful to the user? (reminders of when events are, alerts that price went down)


### NOTES ###
# remember to use two \ in the directory definitions for it to work
# The SeatGeek API is running on Michigan time
# plotting works when there are multiple of the same timestamp
# test event IDs:
# 6480339 Shakira concert
# 6471282 Bruno Mars Concert
# 6441103 Hans Zimmer Concert
# 6453740 21 Pilots Concert

# SeatGeek API details, where client_id is the username and client_secret is the password
client_id = 'NDExNTIwNzN8MTcxMzkzMDcyMS43MTgwMzM'
client_secret = '08e38998e8b5d0e37a5bd65d06615965ab87170481d6b1bba957e0f06614fe94'
data_dir = "C:\\Users\\ivani\\OneDrive\\Desktop\\pricetracker\\"

# params variable to use for permissions
params = (('client_id', 'client_secret'),)

sample_ids = [6480339, 6471282, 6441103, 6453740]


# a function that calls the get_event_ids and get_event_jsons functions at the same time
# returns list of raw event jsons for multiple events (up to 4)
def get_event_list_jsons():
    # prompts the user to input event IDs, up to 4, then returns a list of event IDs
    # change this to a command on discord, !track id id id id
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

    # a function that grabs event ID list, and puts the raw json data into a list
    def get_event_jsons(event_id_list):
        response_list = []
        for id in event_id_list:
            response_list.append(requests.get(
                f'https://api.seatgeek.com/2/events/{id}?client_id={client_id}&client_secret={client_secret}').json())
        return response_list

    # this try and except statement runs the get event ids function and prompts the user to type the events
    try:
        event_ids = get_event_ids()
        print("Event IDs:", event_ids)  # Print event IDs just for confirmation
        return get_event_jsons(event_ids)
    except ValueError as ve:
        print("Error:", ve)
        return []


# stores the list of raw jsons (multiple dictionaries) into a variable by calling the get_event_list_jsons function
jsons = get_event_list_jsons()


# takes json data (one dictionary), and returns a dictionary with the relevant stats
def get_stats(json_data):
    """
    takes json_data and extracts the relevant statistics from the data; returns a dictionary containing these stats
    the response argument is the raw json text that was scraped from the api. This is the dictionary.
    define a new dictionary, stats, whose keys are relevant keys from the response json, and values are the index of
    those relevant keys in the response json
    """
    stats = {'id': json_data['id'], 'title': json_data['title'], 'listing_count': json_data['stats']['listing_count'],
             'lowest_price': json_data['stats']['lowest_price'], 'median_price': json_data['stats']['median_price'],
             'average_price': json_data['stats']['average_price'], 'highest_price': json_data['stats']['highest_price'],
             'announced': json_data['announce_date'], 'event_timestamp': json_data['datetime_local'],
             'current_tme': datetime.datetime.utcnow().isoformat()[:-4]}
    return stats


# returns a list of dictionaries with the relevant stats extracted from the multiple raw jsons by the get_stats function
def get_stats_dict_list(jsons_list):
    dict_list = []
    for i in range(len(jsons_list)):
        dict_list.append(get_stats(jsons_list[i]))
    return dict_list


# creates a variable which is a list of dictionaries of inputted event ids (up to 4) with their relevant stats

stats_dict_list = get_stats_dict_list(jsons)
print(stats_dict_list)


# converts list of dictionaries with the relevant json stats extracted, into one csv file
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


# call the function and create the csv
convert_dicts_to_csv(stats_dict_list)

# creates variable data which is a data frame of the stats csv (easier to generate graphs and whatnot with dataframe)
# stats_dataframe = pd.read_csv("stats.csv")
# print(stats_dataframe)

# ----------------DATABASE SECTION ---------------- #

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="portal2gunIV!",
    database='price_tracker_stats'
)

mycursor = db.cursor()


# # deletes oldest 4 entries from the stats table
# mycursor.execute("DELETE FROM stats ORDER BY current_tme ASC LIMIT 4;")
# db.commit()

# # drops table stats
# mycursor.execute("DROP TABLE stats")

# #creates a table stats with columns named after the stats dictionary
def create_user_table():
    # defines a function get_name, gets the name of the discord user and creates a sql table with their data.
    def get_name():
        name = input("Enter name: ")
        return name

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="portal2gunIV!",
        database='price_tracker_stats'
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


# make this into a discord command !register
# create_user_table()

# this reads the csv, and imports the data of the csv into the stats table on the database
# try to make it so that it just reads the dictionaries into the sql database
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


# reads a sql table from my database and makes it into a pandas dataframe
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


old_time_stats_df = create_df('old_time_stats')


# print(old_time_stats_df)


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


# clear_table('stats')
# clear_table('old_time_stats')


# ----------------TEST PLOTTING---------------- #
# old_time_stats has all the data. Sort by time extract and plot the similar ids
# test event IDs:
# 6480339 Shakira concert
# 6471282 Bruno Mars Concert
# 6441103 Hans Zimmer Concert
# 6453740 21 Pilots Concert

# gets the data from the database given a user's id
def get_data():
    def get_name():
        name = input("Enter name for data retrieval and plotting: ")
        return name

    username = get_name()
    try:
        # Connect to MySQL
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="portal2gunIV!",
            database='price_tracker_stats'
        )
        mycursor = db.cursor()

        # Construct SQL query to select old data and new data
        query = f"""
            SELECT id, title, lowest_price, current_tme FROM {username} ORDER BY id, current_tme ASC
        """
        # Execute SQL query
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

print(ids)
print(artists)
print(prices)
print(current_time)


# creates a dictionary with of the relevant details
# the keys are the unique concert/event ids
# the values are the artist name, timestamps, and prices of tickets
# plots the data with the ids, artists, prices, current_time
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

    # configures plot size on display, figure out how to turn this into an image and display on dc
    plt.figure(figsize=(10, 6))
    # configures the legend to display the artist name as well as their unique id
    # perhaps to make it user-friendly, I can replace id with location of event, as that may be unique as well.
    for _id, data in artist_data.items():
        label = f'{data["artist"]} (ID: {_id})'  # Include ID in the legend label
        plt.plot(data['timestamps'], data['prices'], marker='o', label=label)

    plt.xlabel('Date and Time')
    plt.ylabel('Price')
    plt.title('Lowest Prices over Time by Artist')
    plt.xticks(rotation=45)

    # Customizing legend
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = list(set(labels))
    unique_handles = [handles[labels.index(label)] for label in unique_labels]
    plt.legend(unique_handles, unique_labels, loc='upper left')

    plt.grid(True)
    plt.tight_layout()
    plt.show()


plot_stats(ids, artists, prices, current_time)
