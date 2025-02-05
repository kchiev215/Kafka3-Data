from kafka import KafkaConsumer, TopicPartition
from json import loads
import mysql.connector


class XactionConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer('bank-customer-events',
            bootstrap_servers=['localhost:9092'],
            # auto_offset_reset='earliest',
            value_deserializer=lambda m: loads(m.decode('ascii')))
        ## These are two python dictionarys
        # Ledger is the one where all the transaction get posted
        self.ledger = {}
        # custBalances is the one where the current blance of each customer
        # account is kept.
        self.custBalances = {}
        # THE PROBLEM is every time we re-run the Consumer, ALL our customer
        # data gets lost!
        # add a way to connect to your database here.

        #Go back to the readme.

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="kafka"
    )

    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS transaction (custid INT PRIMARY KEY NOT NULL, \
                      type VARCHAR(255) NOT NULL, date INT, amt INT)")

    def handleMessages(self):
        for message in self.consumer:
            message = message.value
            print('{} received'.format(message))
            self.ledger[message['custid']] = message
            # add message to the transaction table in your SQL usinf SQLalchemy
            if message['custid'] not in self.custBalances:
                self.custBalances[message['custid']] = 0
            if message['type'] == 'dep':
                self.custBalances[message['custid']] += message['amt']
            else:
                self.custBalances[message['custid']] -= message['amt']
            print(self.custBalances)

            messages = (message['custid'], message['type'], message['date'], message['amt'])
            insert_data = 'INSERT INTO Transaction (custid, type, date, amt) VALUES (?, ?, ?, ?)'
            self.cursor.execute(insert_data, messages)
            self.conn.commit()

if __name__ == "__main__":
    c = XactionConsumer()
    c.handleMessages()