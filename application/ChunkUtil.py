def separate_file_into_chunks(file_location,chunk_size):
    chunks = []
    with open(file_location, 'rb') as infile:
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break

            chunks.append(chunk)
    return chunks