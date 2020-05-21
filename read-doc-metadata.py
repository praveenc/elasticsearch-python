import requests
import logging
from os import listdir, walk    
from os.path import isfile, join, splitext
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


## https://cwiki.apache.org/confluence/display/TIKA/TikaServer#TikaServer-UsingprebuiltDockerimage

DOC_PATH='/Users/pchamart/Praveen/guides-whitepaper-presentations/guides'
TIKA_SERVER_URL="http://localhost:9998"
# onlyfiles = [f for f in listdir(DOC_PATH) if isfile(join(DOC_PATH, f))]

for (dirpath, dirnames, filenames) in walk(DOC_PATH):
    full_names = [join(dirpath, fn) for fn in filenames if fn.endswith('pdf')]
    print(full_names)
    break

# headers = {
#     'Content-type': 'application/pdf',
# }

# Loop through each file and then CURL this to tika
for kdoc in full_names:
    print(f"Reading doc: {kdoc}")
    data = open(kdoc, 'rb')
    parser = PDFParser(data)
    doc = PDFDocument(parser)
    # data = open(kdoc, 'rb').read()
    # response = requests.put(TIKA_SERVER_URL+"/tika", headers=headers, data=data)
    # response = requests.put(TIKA_SERVER_URL+"/unpack", data=data)
    # response = requests.get(TIKA_SERVER_URL+"/unpack")
    # print(response.text)
    metadata = doc.info[0]
    print(metadata)
    # break
