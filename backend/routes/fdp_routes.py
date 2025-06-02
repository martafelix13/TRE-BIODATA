import utils
from flask import Blueprint, request, jsonify
import requests
import settings
import fdp_utils
from pymongo import MongoClient
import logging
import os

fdp_bp = Blueprint('fdp', __name__)
BASE_URL = "http://localhost:8667"

client = MongoClient(settings.MONGO_URI)
dbMetadata = client["metadata"]
datasetDB = dbMetadata["dataset"]
distributionDB = dbMetadata["distribution"]

# === Audit Logger Setup (reuse the same file as server.py) ===
AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'audit.log')
audit_logger = logging.getLogger("TRE-BIODATA-AUDIT")
if not audit_logger.hasHandlers():
    audit_logger.setLevel(logging.INFO)
    audit_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding='utf-8')
    audit_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    audit_logger.addHandler(audit_handler)

@fdp_bp.route("/upload", methods=["POST"])
def uploadMetadata():
    """
    Upload a file to the FDP.
    """
    print("DEBUG: Received request to upload metadata")

    form_data = request.json

    print(f"DEBUG: Form data received: {form_data}")
    datasetDB.insert_one(form_data["dataset"])
    for distribution in form_data["distributions"]:
        distributionDB.insert_one(distribution)

    response = fdp_utils.create_and_publish_metadata(form_data["dataset"], form_data["distributions"])

    user_ip = request.remote_addr
    user_id = utils.get_user_id(request.cookies.get('id_token')) if hasattr(utils, "get_user_id") else "unknown"

    audit_logger.info(f"FDP_UPLOAD | user_id={user_id} | IP={user_ip} | data_keys={list(form_data.keys())}")

    if isinstance(response, dict) and "error" in response:
        print(f"ERROR: Failed to upload metadata: {response['error']}")
        audit_logger.error(f"FDP_UPLOAD_FAIL | user_id={user_id} | IP={user_ip} | error={response['error']}")
        return jsonify(response), 500
    else:
        formatted_response = {
            "dataset_uri": str(response["dataset_uri"]),
            "distributions_uri": [str(uri) for uri in response["distribution_uri"]]
        }
        print("DEBUG: Metadata uploaded successfully")
        audit_logger.info(f"FDP_UPLOAD_COMPLETE | user_id={user_id} | IP={user_ip} | dataset_id={formatted_response.get('dataset_uri', 'unknown')}")
        return jsonify(formatted_response), 200


@fdp_bp.route("/datasets", methods=["GET"])
def getDataset():
    """
    Get a datasets from the FDP.
    """
    print("DEBUG: Received request to get dataset")
    
    user_ip = request.remote_addr
    user_id = utils.get_user_id(request.cookies.get('id_token')) if hasattr(utils, "get_user_id") else "unknown"
    audit_logger.info(f"FDP_GET_DATASETS | user_id={user_id} | IP={user_ip}")

    # Send the JSON-LD data to the FDP
    response = requests.get(f"{settings.FDP_TRE_CATALOG_URL}", headers={"Accept": "text/turtle"})
    audit_logger.info(f"FDP_GET_DATASETS_RESPONSE | user_id={user_id} | IP={user_ip} | status={response.status_code}")
    
    if response.status_code == 200:
        print("DEBUG: Dataset retrieved successfully")
        audit_logger.info(f"FDP_GET_DATASETS_SUCCESS | user_id={user_id} | IP={user_ip}")
        return jsonify(response), 200
    else:
        print(f"ERROR: Failed to retrieve dataset, status code: {response.status_code}")
        audit_logger.error(f"FDP_GET_DATASETS_FAIL | user_id={user_id} | IP={user_ip} | status={response.status_code}")
        return jsonify({"error": "Failed to retrieve dataset"}), response.status_code