#!/usr/bin/env python
import logging
import tika
import os
import logging
import concurrent.futures
from tika import parser, unpack
from elasticsearch import Elasticsearch
"""
Author: Praveen Chamarthi
"""
INDEX_NAME="apachelogs"
LOGS_PATH='/path/to/apache/logs/'

def connect_elasticsearch(host="localhost", port="9200"):
    """ Function that returns a connection object. 
    
    Arguments:
        host {str} -- Hostname (default is localhost)
        port {str} -- Portnumber (default is 9200)
    """
    _es = None
    _es = Elasticsearch([{'host': host, 'port': port}])
    if _es.ping():
        logging.info('Connected...')
    else:
        logging.error(f"Error connecting to ES Cluster: {host}:{port}")
    return _es

def create_index(es_object, index_name=INDEX_NAME):
    """
    Create a strict index based on document metadata returned by tika.
    Refer to metadata-tika-sample.json for sample metadata fields returned

    Arguments:
        es_object {Object} -- Instance of elasticsearch connection object
        index_name {str}  -- Name of elasticsearch index to create
    """
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "knowledge_docs": {
                "dynamic": "strict",
                "properties": {
                    "title": {"type": "text" },
                    "description": {"type": "text" },
                    "author": {"type": "text" },
                    "creation_date": {"type": "date" },
                    "content_type": {"type": "text" },
                    "keywords": {"type": "text" },
                    "num_pages": {"type": "integer" },
                    "filename":  {"type": "text" },
                    "content":  {"type": "text" }
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(INDEX_NAME):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=INDEX_NAME, ignore=400, body=settings)
            logging.info('Created Index')
        created = True
    except Exception as ex:
        logging.error("Error creating Index: %s" %(ex))
    finally:
        return created

def prepare_index_record(document_path, tika_url=TIKA_URL):
    """
    Prepares the record object (dict) after querying tika using the unpack.
    Unpack returns metadata and content in the response dict.

    Arguments:
        document_path {str}  -- Full Path to the document to be sent to tika
        tika_url {str}  -- (optional) full url to tika server
    """
    parsed = unpack.from_file(document_path, tika_url)
    metadata = parsed["metadata"]
    content = parsed["content"]
    title = "NoTitle"
    if title == "NoTitle":
        title = metadata.get("title", "NoTitle")
    elif title == "NoTitle":
        title = metadata.get("dc:title", "NoTitle")
    else:
        title = metadata.get("pdf.docinfo:title", "NoTitle")
    author = "NoAuthor"
    if author == "NoAuthor":
        author = metadata.get("Author", "NoAuthor")
    elif author == "NoAuthor":
        author = metadata.get("meta:author", "NoAuthor")
    
    subject = metadata.get("subject", "NoSubject")
    keywords = "NoKeywords"
    if keywords == "NoKeywords":
        keywords = metadata.get("Keywords", "NoKeywords")
    elif keywords == "NoKeywords":
        keywords = metadata.get("meta:keyword", "NoKeywords")
    elif keywords == "NoKeywords":
        keywords = metadata.get("pdf.docinfo:keywords", "NoKeywords")
    resourcename = metadata.get("resourceName", "NoResourceName")
    record = {
        "title": title,
        "description": subject,
        "author": author,
        "creation_date": metadata["Creation-Date"],
        "content_type": metadata["Content-Type"],
        "keywords": keywords,
        "num_pages": metadata["xmpTPg:NPages"],
        "filename": resourcename,
        "content": content
    }
    return record

def add_record_to_index(elastic_connection, document_path, tika_url=TIKA_URL, index_name=INDEX_NAME):
    """
    Sends document(record) to elasticsearch for index.

    Arguments:
        elastic_connection {object}  -- instance of connection object to elasticsearch
        document_path {str}  -- Full Path to the document to be sent to tika
        tika_url {str}  -- URI to tika server e.g. http://localhost:9998/tika
        index_name {str}  -- name of the elasticsearch index
    """
    record = prepare_index_record(document_path, tika_url)
    try:
        index_confirmation=elastic_connection.index(index=index_name, doc_type='knowledge_docs', body=record)
    except Exception as exc:
        logging.error('%r Error indexing data %s' %(document_path, exc))
    return index_confirmation

def get_documents(path_to_scan):
    """
    returns a list of paths (FQDN) of all documents under the top level directory.

    Arguments:
        path_to_scan {str}  -- Full Path to the top level directory where the documents reside
    """
    for (dirpath, _, filenames) in os.walk(path_to_scan):
        full_names = [os.path.join(dirpath, fn) for fn in filenames if fn.endswith('pdf')]
        break
    return full_names

def create_logger():
    """ Basic logger to write to console and to a file for debug info. """
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='DEBUG.log',
                    filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

if __name__ == "__main__":
    create_logger()
    logging.info(f"Connecting to ES ...")
    es_conn = connect_elasticsearch()
    if not es_conn.indices.exists(INDEX_NAME):
        logging.info(f"Creating index {INDEX_NAME} ...")
        create_index(es_conn)
    else:
        logging.info(f"Index {INDEX_NAME} exists")
    logging.info(f"Scanning DIR: {LOGS_PATH} ...")
    full_names = get_documents(LOGS_PATH)

    # Use ThreadPoolExecutor to index documents in parallel with 5 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_kdoc = {executor.submit(add_record_to_index, es_conn, kdoc, TIKA_URL): kdoc for kdoc in full_names}
        # print(future_to_kdoc)
        for future in concurrent.futures.as_completed(future_to_kdoc):
            kdoc = future_to_kdoc[future]
            logging.info(f"Indexing: {kdoc}...")
            try:
                data = future.result()
            except Exception as exc:
                logging.error("Indexing %r generated an exception: %s" % (kdoc, exc))
            else:
                logging.info("document %s indexed successfully" % (kdoc))