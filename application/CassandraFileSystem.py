import sys
import time
import uuid
from multiprocessing.context import Process

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
cassandra_ip = "a58cb486432d64a9abd619859b3b430c-1134284996.us-east-1.elb.amazonaws.com"
keyspace_name = "test"
chunk_size = 1000000
# cluster for remote host
cluster = Cluster([cassandra_ip], auth_provider=ap)

# cluster for localhost
#cluster = Cluster()


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
    strCQL = "SELECT * FROM file WHERE file_name=?;"
    pStatement = session.prepare(strCQL)
    rows = session.execute(pStatement, [file_name])
    chunks = []
    for row in rows:
        chunks.append(row[2])
    file = b''.join(chunks)
    return file


def run_test(chunks, process_name):
    session = cluster.connect(keyspace_name)
    session.default_timeout = None

    start = time.perf_counter()
    insert_file(process_name, chunks, session)
    output = get_file(process_name,session)
    stop = time.perf_counter()
    input = b''.join(chunks)
    if(input == output):
        time_taken = stop - start
        # print(f"Process {process_name} succesful taken : {time_taken:0.4f} seconds")
        print(time_taken)
    else:
        print("TEST failed")


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
                       PRIMARY KEY(file_name, id))""")

def run_test_session(file_location, amount_of_processes):
    setup()
    print('setup done')
    chunks = separate_file_into_chunks(file_location, chunk_size)
    print(f"file is split into {len(chunks)} chunks")
    print(f"Starting {amount_of_processes} processes")
    for i in range(amount_of_processes):
        Process(target=run_test, args=(chunks, str(i))).start()


def list_files():
    session = cluster.connect(keyspace_name)
    rows = session.execute("SELECT DISTINCT file_name FROM file")
    print("Files available for download:")
    for row in rows:
        print(row[0])


def save_file(file_name, location_to_be_saved):
    session = cluster.connect(keyspace_name)
    file = get_file(file_name, session)
    f = open(location_to_be_saved, "wb")
    f.write(file)
    print("Written file at: " + location_to_be_saved)


def print_help():
    file = open("help.txt")
    lines = file.readlines()
    for line in lines:
        print(line)

def separate_file_into_chunks(file_location,chunk_size):
    chunks = []
    with open(file_location, 'rb') as infile:
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break

            chunks.append(chunk)
    return chunks


def delete_file(file_name):
    session = cluster.connect(keyspace_name)
    strCQL = "DELETE FROM file WHERE file_name=?;"
    pStatement = session.prepare(strCQL)
    session.execute(pStatement, [file_name])


def main():
    command = sys.argv[1]
    if command == "setup":
        setup()
        print("Setup completed")
    elif command == "test":
        run_test_session(sys.argv[2], int(sys.argv[3]))
    elif command == "add_file":
        add_file(sys.argv[2], sys.argv[3])
        print(f"File {sys.argv[2]} added")
    elif command == "list_files":
        list_files()
    elif command == "get_file":
        save_file(sys.argv[2], sys.argv[3])
    elif command == "delete_file":
        delete_file(sys.argv[2])
        print(f"File {sys.argv[2]} deleted")
    elif command == "help":
        print_help()
    else:
        print("Wrong input")
        print("For help execute:")
        print("python3.8 CassandraFileSystem.py help")


if __name__ == '__main__':
    main()
