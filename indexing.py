from elasticsearch import Elasticsearch
import logging
import requests
from os import walk
from os.path import join
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


INDEX_NAME="sooperindex"
DOC_PATH='/Users/pchamart/Praveen/guides-whitepaper-presentations/guides'

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Connected...')
    else:
        print('Aww it could not connect')
    return _es

def create_index(es_object, index_name=INDEX_NAME):
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
                    "title": {
                        "type": "text"
                    },
                    "keywords": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "creator": {
                        "type": "text"
                    },
                    "producer": {
                        "type": "text"
                    },
                    "creation_date": {
                        "type": "date"
                    },
                    "doc_content": {
                        "type": "text"
                    }
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(INDEX_NAME):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=INDEX_NAME, ignore=400, body=settings)
            print('Created Index')
            created = True
        else:
            print(f"Index: {INDEX_NAME} already exists")
    except Exception as ex:
        print(str(ex))
    finally:
        return created

def add_record_to_index(elastic_connection, index_name, record):
    is_stored = True
    try:
        outcome = elastic_connection.index(index=index_name, doc_type='knowledge_docs', body=record)
        print(outcome)
    except Exception as ex:
        print('Error indexing data')
        print(str(ex))
        is_stored = False
    return is_stored

def get_documents(path_to_scan):
    for (dirpath, _, filenames) in walk(DOC_PATH):
        full_names = [join(dirpath, fn) for fn in filenames if fn.endswith('pdf')]
        break
    return full_names


# TODO: Implement reading PDF metadata and posting to Elasticsearch Index
# TODO: 


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    print(f"Connecting to ES ...")
    es_conn = connect_elasticsearch()
    print(f"Creating index {INDEX_NAME} ...")
    create_index(es_conn)
    # record = {
    #     "title": "Primal Carvings",
    #     "description": "your favorite foods made paleo",
    #     "author": "Megan McCullough Keatley and Brandon Keatley",
    #     "published_date": "2013-05-01"
    # }
    # if add_record_to_index(es_conn, INDEX_NAME, record):
    #     print("record indexed successfully")