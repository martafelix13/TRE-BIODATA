from backend import utils
from flask import Blueprint,request, jsonify
import requests
import settings

from utils import convert_json_to_dcat, convert_json_to_catalog_dcat

fdp_bp = Blueprint('fdp', __name__)

@fdp_bp.route("/upload-dataset", methods=["POST"])
def uploadDataset():
    """
    Upload a file to the FDP.
    """
    print("DEBUG: Received request to upload dataset")

    form_data = request.json
    print(f"DEBUG: Form data received: {form_data}")
    
    g = convert_json_to_dcat(form_data)
    print("DEBUG: Converted form data to DCAT graph")
    print(g.serialize(format="turtle"))

    token = utils.get_fdp_token()
    if not token:
        print("ERROR: Unable to retrieve token")
        return jsonify({"error": "Unable to retrieve token"}), 401

    print(f"DEBUG: Retrieved token: {token}")

    # Create headers for the request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/turtle"
    }
    print(f"DEBUG: Headers created: {headers}")
    
    # Turn g into file
    file = g.serialize(format="turtle").encode("utf-8")
    print("DEBUG: Serialized graph to Turtle format")

    # Send the JSON-LD data to the FDP
    response = requests.post(f"{settings.FDP_URL}/dataset", headers=headers, data=file)
    print(f"DEBUG: Response from FDP: {response.status_code}, {response.text}")
    
    if response.status_code == 200:
        print("DEBUG: File uploaded successfully")
        return jsonify({"message": "File uploaded successfully"}), 200
    else:
        print(f"ERROR: Failed to upload file, status code: {response.status_code}")
        return jsonify({"error": "Failed to upload file"}), response.status_code   
     

    
@fdp_bp.route("/upload-catalog", methods=["POST"])
def uploadCatalog():
    """
    Upload a file to the FDP.
    """
    print("DEBUG: Received request to upload catalog")

    form_data = request.json
    print(f"DEBUG: Form data received: {form_data}")
    
    g = convert_json_to_catalog_dcat(form_data)
    print("DEBUG: Converted form data to DCAT graph")
    print(g.serialize(format="turtle"))

    token = utils.get_fdp_token()
    if not token:
        print("ERROR: Unable to retrieve token")
        return jsonify({"error": "Unable to retrieve token"}), 401

    print(f"DEBUG: Retrieved token: {token}")

    # Create headers for the request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/turtle"
    }
    print(f"DEBUG: Headers created: {headers}")
    
    # Turn g into file
    file = g.serialize(format="turtle").encode("utf-8")
    print("DEBUG: Serialized graph to Turtle format")

    # Send the JSON-LD data to the FDP
    response = requests.post(f"{settings.FDP_URL}/catalog", headers=headers, data=file)
    print(f"DEBUG: Response from FDP: {response.status_code}, {response.text}")
    
    if response.status_code == 400:
        #TODO: Create metadata
        print("DEBUG: Service metadata created successfully")
        response = requests.post(f"{settings.FDP_URL}/catalog", headers=headers, data=file)
        print(f"DEBUG: Response from FDP after creating metadata: {response.status_code}, {response.text}")
        

        if response.status_code == 200:
            print("DEBUG: Catalog created successfully")
            return jsonify({"message": "Catalog created successfully"}), 200
        else:
            print(f"ERROR: Failed to create the catalog, status code: {response.status_code}")
            return jsonify({"error": "Failed to create catalog"}), response.status_code

    elif response.status_code == 200:
        print("DEBUG: Catalog created successfully")
        return jsonify({"message": "Catalog created successfully"}), 200
    else:
        print(f"ERROR: Failed to create the catalog, status code: {response.status_code}")
        return jsonify({"error": "Failed to create catalog"}), response.status_code   

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