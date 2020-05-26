# Parsing docs using Apache Tika and Python3

## Prerequisites

- Python3.7 or greater
- Docker
- elasticsearch
- kibana

## Installation, Configuration

---
Note: ![Alert Icon](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon28.png "Alert") Instructions are for macos variants

1. Install pre-requisites using [brew](https://brew.sh/) on MacOS `brew install python3 docker elasticsearch kibana`
2. Pull [tika-docker](https://github.com/apache/tika-docker) image `docker pull docker pull apache/tika:<tag>`
3. Run docker image `docker run -d -p 9998:9998 apache/tika`
4. Install tika-python using pip `pip install tika`

---

### References

- [Tika Server Documentation](https://cwiki.apache.org/confluence/display/TIKA/TikaServer)
- [tika-python Documentation](https://github.com/chrismattmann/tika-python)
- [Sample document metadata extracted using ApacheTika](data-samples/metadata-tika-sample.json)
- [Elasticsearch REST calls](rest-calls/elasticsearch-rest.http)
