"""Main file to get text from any pdf document"""
# python imports
import json
import logging
from flask import Flask, request, jsonify, make_response

# local imports
import text_analysis

# by default disable_existing_loggers=True
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger_access = logging.getLogger("gunicorn.access")
logger_error = logging.getLogger("gunicorn.error")

app = Flask(__name__)


@app.route("/parse", methods=["POST"])
def analysis_run():
    """Run analysis on a document"""

    data = request.get_json()
    logger_access.info("Input bucket name and doc name: %s", data)

    doc_analysis = text_analysis.DocumentAnalysis(data["bucket_name"], data["document_name"])
    job_id = doc_analysis.start_job()
    logger_access.info("Started job with id: %s",job_id)
    # response = None
    if doc_analysis.is_job_complete(job_id):
        response = doc_analysis.get_job_results(job_id)

    key_map, value_map, block_map, text = doc_analysis.get_kv_map(response)
    logger_access.debug("key_map: %s , value_map: %s", key_map, value_map)
    logger_access.debug("block_map: %s text: %s ", block_map, text)
    # Get raw text
    file = open("raw_info.txt", "w+")
    file.write(text)
    file.close()
    # Get Key Value relationship
    kvs = doc_analysis.get_kv_relationship(key_map, value_map, block_map)
    with open("forms.json", "w") as outfile:
        json.dump(kvs, outfile, indent=2)

    api_response = {
        "patient-name": "xyz",
        "file-number": "123",
        "date-of-injury": "01-15-2021",
        "dob": "03-09-1993",
        "employer":" abc",
        "ssn": "123456789",
        "provider": "xxyy",
        "icd-10-codes":{"B97.35": 10,
                        "A02.21": 15
                        }
        }
    response_dict = {"message": api_response, "error": ""}
    response = make_response(jsonify(response_dict), 200, )
    response.headers["Content-Type"] = "application/json"
    return response
