import base64
import time
import uuid
from multiprocessing.context import Process

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

from application.ChunkUtil import separate_file_into_chunks

ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
cassandra_ip = "20.76.16.81"
keyspace_name = "test"
chunk_size = 10
# cluster for remote host
#cluster = Cluster([cassandra_ip], auth_provider=ap)

# cluster for localhost
cluster = Cluster()


def insert_file(file_name, chunks, session):
    for i in range(len(chunks)):
        strCQL = "INSERT INTO file (id, file_name, chunk, chunk_number ) VALUES (?,?,?,?)"
        pStatement = session.prepare(strCQL)
        session.execute(pStatement, [uuid.uuid1(),file_name, chunks[i], i])


def add_file(file_name, file_location):
    chunks = separate_file_into_chunks(file_location, chunk_size)
    session = cluster.connect(keyspace_name)
    insert_file(file_name, chunks, session)


def check_file_saved_correctly(file_name, file,session):
    retrieved_file = get_file(file_name, session)
    return retrieved_file == file


def get_file(file_name, session):
    strCQL = "SELECT file FROM file WHERE file_name=?;"
    pStatement = session.prepare(strCQL)
    rows = session.execute(pStatement, [file_name])
    for row in rows:
        print(row)
    return rows[0]


def run_test(file_name,process_name):
    file = open_file(file_name)
    session = cluster.connect(keyspace_name)
    session.default_timeout = None
    # session.default_timeout = 80
    # session.default_timeout
    start = time.perf_counter()
    insert_file(process_name, file, session)
    if(check_file_saved_correctly(process_name, file, session)):
        stop = time.perf_counter()
        time_taken = stop - start
        # print(f"Process {process_name} succesful taken : {time_taken:0.4f} seconds")
        print(time_taken)
    else:
        print("TEST failed")

def open_file(file_location):
    file = open(file_location, 'rb')
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
                       id uuid,
                       file_name text,
                       chunk blob,
                       chunk_number int,
                       PRIMARY KEY(id))""")

def run_test_session(file_name, amount_of_processes):
    for i in range(amount_of_processes):
        Process(target=run_test, args=(file_name, str(i))).start()


def list_files():
    session = cluster.connect(keyspace_name)
    rows = session.execute("SELECT file_name FROM file")
    print("Files available for download:")
    for row in rows:
        print(row[0])


def save_file(file_name, location_to_be_saved):
    session = cluster.connect(keyspace_name)
    file = get_file(file_name, session)
    decoded_file = base64.decodebytes(file)
    f = open(location_to_be_saved, "wb")
    f.write(decoded_file)
    print("Written file at: " + location_to_be_saved)


def print_help():
    file = open("help.txt")
    lines = file.readlines()
    for line in lines:
        print(line)


def main():
    print("Welcome to the DPS assignment 2 application")
    save_file("test","help.txt")
    # chunks = separate_file_into_chunks("help.txt",chunk_size)

    # command = sys.argv[1]
    # if command == "setup":
    #     setup()
    # elif command == "test":
    #     run_test_session(sys.argv[2], int(sys.argv[3]))
    # elif command == "add_file":
    #     add_file(sys.argv[2], sys.argv[3])
    # elif command == "list_files":
    #     list_files()
    # elif command == "get_file":
    #     save_file(sys.argv[2], sys.argv[3])
    # elif command == "help":
    #     print_help()
    # else:
    #     print("Wrong input")
    #     print("For help execute:")
    #     print("python3.8 CassandraFileSystem.py help")


if __name__ == '__main__':
    main()
