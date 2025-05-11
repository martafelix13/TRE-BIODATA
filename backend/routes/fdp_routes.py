import utils
from flask import Blueprint,request, jsonify
import requests
import settings
import fdp_utils
from pymongo import MongoClient

fdp_bp = Blueprint('fdp', __name__)
BASE_URL = "http://localhost:8667"

client = MongoClient(settings.MONGO_URI)
dbMetadata = client["metadata"]
datasetDB = dbMetadata["dataset"]
distributionDB = dbMetadata["distribution"]

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

    fdp_utils.create_and_publish_metadata(form_data["dataset"], form_data["distributions"])

    return jsonify({"message": "Metadata uploaded successfully"}), 201


@fdp_bp.route("/datasets", methods=["GET"])
def getDataset():
    """
    Get a datasets from the FDP.
    """
    print("DEBUG: Received request to get dataset")
    
    # Send the JSON-LD data to the FDP
    response = requests.get(f"{settings.FDP_TRE_CATALOG_URL}", headers={"Accept": "text/turtle"})
    print(f"DEBUG: Response from FDP: {response.status_code}, {response.text}")
    
    if response.status_code == 200:
        print("DEBUG: Dataset retrieved successfully")
        return jsonify(response.json()), 200
    else:
        print(f"ERROR: Failed to retrieve dataset, status code: {response.status_code}")
        return jsonify({"error": "Failed to retrieve dataset"}), response.status_code