import base64
import time
import sys
from multiprocessing.context import Process

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
cassandra_ip = "20.76.16.81"
keyspace_name = "test"
test_file_location = 'test.dat'

# cluster = Cluster([cassandra_ip], auth_provider=ap)
cluster = Cluster()


def add_file(file_name,file,session):
    strCQL = "INSERT INTO file (file_name,file) VALUES (?,?)"
    pStatement = session.prepare(strCQL)
    session.execute(pStatement, [file_name, file])


def check_file_saved_correctly(file_name, file,session):
    strCQL ="SELECT file FROM file WHERE file_name=?;"
    pStatement = session.prepare(strCQL)
    retrieved_file = session.execute(pStatement, [file_name]).one()
    return retrieved_file[0] == file;


def run_test(file_name):
    file = get_test_file()
    session = cluster.connect(keyspace_name)
    start = time.perf_counter()
    add_file(file_name,file,session);
    if(check_file_saved_correctly(file_name,file,session)):
        stop = time.perf_counter()
        time_taken = stop - start
        print(f"Process {file_name} succesful taken : {time_taken:0.4f} seconds")
    else:
        print("TEST failed")

def get_test_file():
    file = open(test_file_location, 'rb')  # open binary file in read mode
    file_read = file.read()
    file_64_encode = base64.encodebytes(file_read)
    return file_64_encode


def setup():
    session = cluster.connect()
    session.execute("DROP KEYSPACE IF EXISTS %s;" % keyspace_name)
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
        """ % keyspace_name)
    session.execute("USE %s" % keyspace_name)
    session.execute("""CREATE TABLE file(
                       file_name text PRIMARY KEY,
                       file blob)""")
    print("setup completed you can now test by running: python3.8 CassandraTester.py test (amount_of_processes)")


def run_test_session(amount_of_processes):
    for i in range(amount_of_processes):
        Process(target=run_test, args=(str(i),)).start()


def main():
    print("Welcome to the DPS assignment 2 application")
    command = sys.argv[1]
    if command == "setup":
        setup()
    elif command == "test":
        run_test_session(int(sys.argv[2]))
    else:
        print("Wrong input")


if __name__ == '__main__':
    main()
