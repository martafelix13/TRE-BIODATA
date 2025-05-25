import utils
from flask import Blueprint, request, jsonify
import requests
import settings
import fdp_utils
from pymongo import MongoClient
import jwt
import logging
import os

si_bp = Blueprint('si', __name__)

# === Audit Logger Setup (reuse the same file as server.py) ===
AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'audit.log')
audit_logger = logging.getLogger("TRE-BIODATA-AUDIT")
if not audit_logger.hasHandlers():
    audit_logger.setLevel(logging.INFO)
    audit_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding='utf-8')
    audit_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    audit_logger.addHandler(audit_handler)

@si_bp.route('/files', methods=['GET'])
def get_files():
    """
    Get a list of files from the FDP.
    """
    user_ip = request.remote_addr
    request_data = request.args.get('id')
    user_id = "unknown"
    audit_logger.info(f"SI_GET_FILES | IP={user_ip} | request_data_present={bool(request_data)}")

    if not request_data:
        audit_logger.warning(f"SI_GET_FILES | MISSING_REQUEST_DATA | IP={user_ip}")
        return jsonify({"error": "No request data provided"}), 400

    try:
        passport = jwt.decode(request_data, options={"verify_signature": False})
        user_id = passport.get('sub', 'unknown')
        audit_logger.info(f"SI_GET_FILES | JWT_DECODED | user_id={user_id} | IP={user_ip}")
    except Exception as e:
        audit_logger.error(f"SI_GET_FILES | INVALID_JWT | IP={user_ip} | error={str(e)}")
        return jsonify({"error": f"Invalid JWT: {str(e)}"}), 401

    visa = passport.get('ga4gh_visa_v1')
    if not visa or visa.get('type') != 'ControlledAccessGrants':
        audit_logger.info(f"SI_GET_FILES | NO_CONTROLLED_ACCESS | user_id={user_id} | IP={user_ip}")
        return jsonify({"dataset": None, "files": []}), 200

    dataset_id = visa.get('value')
    if not dataset_id:
        audit_logger.warning(f"SI_GET_FILES | MISSING_DATASET_ID | user_id={user_id} | IP={user_ip}")
        return jsonify({"error": "Missing dataset value in visa"}), 400

    access_token = request.cookies.get('access_token')
    if not access_token:
        audit_logger.warning(f"SI_GET_FILES | MISSING_ACCESS_TOKEN | user_id={user_id} | IP={user_ip}")
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
        audit_logger.info(f"SI_GET_FILES | FILES_FETCHED | user_id={user_id} | dataset_id={dataset_id} | IP={user_ip} | status={response.status_code}")
    except requests.RequestException as e:
        audit_logger.error(f"SI_GET_FILES | FILES_FETCH_FAIL | user_id={user_id} | dataset_id={dataset_id} | IP={user_ip} | error={str(e)}")
        return jsonify({"error": f"Failed to fetch files: {str(e)}"}), 502

    try:
        response_data = response.json()
    except ValueError:
        audit_logger.error(f"SI_GET_FILES | INVALID_JSON_RESPONSE | user_id={user_id} | dataset_id={dataset_id} | IP={user_ip}")
        return jsonify({"error": "Invalid JSON response from file server"}), 502

    files = []
    for file in response_data:
        if all(k in file for k in ('fileId', 'displayFileName', 'fileStatus')):
            files.append({
                'id': file['fileId'],
                'status': file['fileStatus']
            })

    audit_logger.info(f"SI_GET_FILES | SUCCESS | user_id={user_id} | dataset_id={dataset_id} | IP={user_ip} | files_count={len(files)}")
    return jsonify({"dataset": dataset_id, "files": files}), 200
