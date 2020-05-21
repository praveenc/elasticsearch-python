import logging
from elasticsearch import Elasticsearch

INDEX_NAME="sooperindex"

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
                    "description": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "published_date": {
                        "type": "date"
                    },
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
    except Exception as ex:
        print(str(ex))
    finally:
        return created

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    print(f"Connecting to ES ...")
    es_conn = connect_elasticsearch()
    print(f"Creating index {INDEX_NAME} ...")
    create_index(es_conn)