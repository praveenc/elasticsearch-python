# Parsing docs using Apache Tika and Python3

## Prerequisites

- Python3.7 or greater
- Docker
- elasticsearch
- kibana

## Installation, Configuration

---

Note: ![Alert Icon](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon28.png "Alert") Instructions are for macos variants

1. Install pre-requisites using [brew](https://brew.sh/) on MacOS

   ```(shell)
   brew install python3 docker elasticsearch kibana
   ```

2. Start `elasticsearch` using `brew services start elasticsearch`
   1. If you'd wish to change elasticsearch config then it's available here `/usr/local/etc/elasticsearch/elasticsearch.yml`
3. Pull [tika-docker](https://github.com/apache/tika-docker) image 

   ```(shell)
   docker pull docker pull apache/tika:<tag>
   ```

4. Run docker image `docker run -d -p 9998:9998 apache/tika`
   1. Test if tika server is up `curl http://localhost:9998/tika`
5. Install and acitivate python3 virutal environment

   ```(shell)
   python3 -m venv venv
   source venv/bin/activate
   ```

6. Install pre-requisites to run [es-indexdocs-tika.py](es-indexdocs-tika.py) `pip install -r requirements.txt`
7. run the script [es-indexdocs-tika.py](es-indexdocs-tika.py) `venv> python es-indexdocs-tika.py`

---

### References

- [Tika Server Documentation](https://cwiki.apache.org/confluence/display/TIKA/TikaServer)
- [tika-python Documentation](https://github.com/chrismattmann/tika-python)
- [Sample document metadata extracted using ApacheTika](data-samples/metadata-tika-sample.json)
- [Elasticsearch REST calls](rest-calls/elasticsearch-rest.http)
