import multiprocessing
import statistics
import sys
import time
import uuid
from multiprocessing.context import Process

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
# Place ip of cluster here
cassandra_ip = ""
keyspace_name = "test"
chunk_size = 1000000

# cluster for remote host
cluster = Cluster([cassandra_ip], auth_provider=ap)


def insert_file(file_name, chunks, session):
    for i in range(len(chunks)):
        strCQL = "INSERT INTO file (id, file_name, chunk, chunk_number ) VALUES (?,?,?,?)"
        pStatement = session.prepare(strCQL)
        session.execute(pStatement, [uuid.uuid1(), file_name, chunks[i], i])


def add_file(file_name, file_location):
    chunks = separate_file_into_chunks(file_location, chunk_size)
    session = cluster.connect(keyspace_name)
    insert_file(file_name, chunks, session)


def check_file_saved_correctly(file_name, file, session):
    retrieved_file = get_file(file_name, session)
    return retrieved_file == file


def get_chunk_numbers(file_name, session):
    strCQL = "SELECT chunk_number FROM file WHERE file_name=?;"
    pStatement = session.prepare(strCQL)
    rows = session.execute(pStatement, [file_name])
    chunk_numbers = []
    for row in rows:
        chunk_numbers.append(row[0])
    chunk_numbers.sort()
    return chunk_numbers


def get_chunks(file_name, chunk_numbers, session):
    chunks = []
    for chunk_number in chunk_numbers:
        strCQL = "SELECT chunk FROM file WHERE file_name=? AND chunk_number=?;"
        pStatement = session.prepare(strCQL)
        row = session.execute(pStatement, [file_name, chunk_number]).one()
        chunks.append(row[0])
    return chunks


def get_file(file_name, session):
    chunk_numbers = get_chunk_numbers(file_name, session)
    chunks = get_chunks(file_name, chunk_numbers, session)
    file = b''.join(chunks)
    return file


def run_test(chunks, process_name, return_dict):
    session = cluster.connect(keyspace_name)
    session.default_timeout = None

    start = time.perf_counter()
    insert_file(process_name, chunks, session)
    output = get_file(process_name, session)
    stop = time.perf_counter()
    input = b''.join(chunks)
    if input == output:
        time_taken = stop - start
        return_dict[process_name] = time_taken
    else:
        print("TEST failed")


def setup():
    session = cluster.connect()
    session.execute("DROP KEYSPACE IF EXISTS %s;" % keyspace_name)
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
        """ % keyspace_name)
    session.execute("USE %s" % keyspace_name)
    session.execute("""CREATE TABLE file(
                       id uuid,
                       file_name text,
                       chunk blob,
                       chunk_number int,
                       PRIMARY KEY(file_name, chunk_number, id)
                       )""")


def run_test_session(file_location, amount_of_processes):
    setup()
    print('setup done')
    chunks = separate_file_into_chunks(file_location, chunk_size)
    print(f"file is split into {len(chunks)} chunks")
    print(f"Starting {amount_of_processes} processes")
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    all_processes = []
    for i in range(amount_of_processes):
        all_processes.append(Process(target=run_test, args=(chunks, str(i), return_dict)))
    for p in all_processes:
        p.start()

    for p in all_processes:
        p.join()
    print("Processes done")
    median_session = statistics.median(list(return_dict.values()))
    print(median_session)
    return median_session


def run_test_cycle(file_location, amount_of_processes, cycles):
    results = []
    for i in range(cycles):
        print(f"RUNNING cycle: {i}")
        results.append(run_test_session(file_location, amount_of_processes))

    print("RESULTS")
    for result in results:
        print(result)
    median = statistics.median(results)

    print(f"Median of {cycles} cycles is {median}")


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


def separate_file_into_chunks(file_location, chunk_size):
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
        run_test_cycle(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
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
