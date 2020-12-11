from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
cassandra_ip = "20.73.39.50"
keyspace_name = "test";


cluster = Cluster([cassandra_ip], auth_provider=ap)

def add_user():
    session = cluster.connect(keyspace_name)
    user_name = input("Please input user name ")
    session.execute("""
           INSERT INTO user (user_name)
           VALUES ('%s')
           """ % user_name)

def get_users():
    session = cluster.connect(keyspace_name)
    rows = session.execute("SELECT * FROM user");
    for user_row in rows:
        print(user_row.user_name)


def main_cycle():
    choice = input("Give input ")
    if choice == "setup":
        setup()
    elif choice == "add user":
        add_user()
    elif choice == "get users":
        get_users()
    else:
        print("invalid command")
    main_cycle()


def setup():
    session = cluster.connect()
    session.execute("DROP KEYSPACE IF EXISTS %s;" % keyspace_name)
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
        """ % keyspace_name)
    session.execute("USE %s" % keyspace_name)
    session.execute("""CREATE TABLE user(
                    user_name text PRIMARY KEY)""")
    



def main():
    print("Welcome to the DPS assignment 2 application")
    main_cycle()


if __name__ == '__main__':
    main()
