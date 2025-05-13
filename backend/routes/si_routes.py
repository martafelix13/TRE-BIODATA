import utils
from flask import Blueprint,request, jsonify
import requests
import settings
import fdp_utils
from pymongo import MongoClient
import jwt 

si_bp = Blueprint('si', __name__)


@si_bp.route('/files', methods=['GET'])
def get_files():
    """
    Get a list of files from the FDP.
    """
    request_data = request.args.get('id')
    if not request_data:
        return jsonify({"error": "No request data provided"}), 400

    try:
        passport = jwt.decode(request_data, options={"verify_signature": False})
    except Exception as e:
        return jsonify({"error": f"Invalid JWT: {str(e)}"}), 401

    visa = passport.get('ga4gh_visa_v1')
    if not visa or visa.get('type') != 'ControlledAccessGrants':
        return jsonify({"dataset": None, "files": []}), 200

    dataset_id = visa.get('value')
    if not dataset_id:
        return jsonify({"error": "Missing dataset value in visa"}), 400

    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"error": "Missing access token in cookies"}), 401

    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            f"{settings.DOWNLOAD_S3}/metadata/datasets/{dataset_id}/files",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch files: {str(e)}"}), 502

    try:
        response_data = response.json()
    except ValueError:
        return jsonify({"error": "Invalid JSON response from file server"}), 502

    files = []
    for file in response_data:
        if all(k in file for k in ('fileId', 'displayFileName', 'fileStatus')):
            files.append({
                'id': file['fileId'],
                'status': file['fileStatus']
            })

    return jsonify({"dataset": dataset_id, "files": files}), 200
