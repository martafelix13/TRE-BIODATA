import io
import logging
from bson import ObjectId
from flask import Flask, json, request, redirect, jsonify, make_response, send_file
import gridfs
import requests
import jwt
from flask_cors import CORS
from pymongo import MongoClient
import os
from settings import *
from pathlib import Path
import json
from rdflib import Graph

from routes.fdp_routes import fdp_bp
from routes.si_routes import si_bp
import xml.etree.ElementTree as ET

import utils

# =========================
# Logging Configuration
# =========================
AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), 'audit.log')
audit_logger = logging.getLogger("TRE-BIODATA-AUDIT")
audit_logger.setLevel(logging.INFO)
audit_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding='utf-8')
audit_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
audit_logger.addHandler(audit_handler)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

client = MongoClient(MONGO_URI)
dbMetadata = client["metadata"]
catalogDB = dbMetadata["catalog"]
datasetDB = dbMetadata["dataset"]
distributionDB = dbMetadata["distribution"]

dbProject = client["project"]
projectDB = dbProject["project_details"]

templateDB = dbProject["templates"]

dbFiles = client["files_system"]
fs = gridfs.GridFS(dbFiles)

dbUser = client["users"]
userDB = dbUser["users_info"]

dbPipeline = client["pipeline"]
pipelineDB = dbPipeline["pipeline_details"] #Pipeline_id | PayloadJson
id_token = None
access_token = None
token_type = None
user = None

app.register_blueprint(fdp_bp, url_prefix='/fdp')  # Optional prefix
app.register_blueprint(si_bp, url_prefix='/si')  

## Authentication and Authorization ##
@app.route('/login')
def login():
    """Redirect user to the OAuth login page"""
    login_url = f"{LOGIN_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20profile%20email%20ga4gh_passport_v1"
    audit_logger.info(f"LOGIN | IP={request.remote_addr}")
    return redirect(login_url)

@app.route('/oidc-callback')
def oidc_callback():
    global id_token, access_token, token_type

    code = request.args.get('code')
    audit_logger.info(f"OIDC_CALLBACK | IP={request.remote_addr} | code={code}")
    if not code:
        audit_logger.warning(f"OIDC_CALLBACK | MISSING_CODE | IP={request.remote_addr}")
        return jsonify({"error": "Authorization code missing"}), 400

    token_request_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid profile email ga4gh_passport_v1",
        "redirect_uri": REDIRECT_URI,
        "requested_token_type": "urn:ietf:params:oauth:token-type:refresh_token",
        "grant_type": "authorization_code"
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(AUTHORIZATION_URL, data=token_request_data, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch tokens"}), response.status_code

    token_data = response.json()
    print("Token Response:", token_data)

    id_token = token_data.get("id_token")
    token_type = token_data.get("token_type")
    access_token = token_data.get("access_token")

    # Store token in cookies
    resp = make_response(redirect(FRONTEND_URL))
    resp.set_cookie('id_token', id_token, httponly=False, secure=True, samesite='None')
    resp.set_cookie('access_token', access_token, httponly=False, secure=True, samesite='None')
    resp.set_cookie('token_type', token_type, httponly=False, secure=True, samesite='None')

    print("Redirecting user to frontend")
    print("Cookies:", resp.headers)
    print (resp)

    audit_logger.info(f"OIDC_CALLBACK | SUCCESS | IP={request.remote_addr}")
    return resp


@app.route('/api/user')
def get_user():
    """Return user data separately"""
    access_token = request.cookies.get('access_token')
    token_type = request.cookies.get('token_type')
    user_id = None

    if not access_token or not token_type:
        audit_logger.warning(f"API_USER | UNAUTHORIZED | IP={request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch user info
    response = requests.post(USER_INFO_URL, headers={'Authorization': f"{token_type} {access_token}"})

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info"}), response.status_code
    
    print(response.json())
    
    # save user data in the database as user.sub -> user.info
    user = {
        "id": response.json().get("sub"),
        "user_info": response.json()
    }

    if not userDB.find_one({"id": user.get("id")}):
        userDB.insert_one(user)

    user_json = response.json()
    user_id = user_json.get("sub", "unknown")
    audit_logger.info(f"API_USER | user_id={user_id} | IP={request.remote_addr}")

    return user_json


## Metadata API ##
@app.route('/submit-form', methods=['POST'])
def submit_form():
    """Submit form data to the server"""
    form_data = request.json
    user_id = utils.get_user_id(request.cookies.get('id_token'))
    audit_logger.info(f"SUBMIT_FORM | user_id={user_id} | IP={request.remote_addr} | data={json.dumps(form_data)[:200]}")
    # Save the RDF graph to a file
    with open("output.ttl", "w", encoding='utf-8') as f:
        f.write(g.serialize(format="turtle"))
    

    if (not form_data):
        return jsonify({"error": "Form data missing"}), 400

    datasetDB.insert_one(form_data)
    distributionDB.insert_one(form_data)

    return jsonify({"message": "Form data submitted successfully"})

@app.route('/catalogs', methods=['GET'])
def get_catalogs():
    # TODO: Add user authentication
    """Return all catalogs"""
    data = list(catalogDB.find({}, {"_id": 0}))  # Fetch data from MongoDB
    json_data = json.dumps(data, default=str)
    print('Catalogs:', json_data)
    return jsonify(json_data), 200

@app.route('/catalog/<string:catalog_id>/datasets', methods=['GET'])
def get_datasets_by_catalog(catalog_id):
    datasets = list(datasetDB.find({"isPartOf": catalog_id}, {"_id": 0}))
    json_data = json.dumps(datasets, default=str)
    print('Datasets from catalog ', catalog_id, ' :', json_data)
    return jsonify(json_data), 200

@app.route('/datasets', methods=['GET'])
def get_datasets():
    #TODO: Add user authentication
    """Return all datasets"""
    datasets = list(datasetDB.find({}, {"_id": 0}))
    json_data = json.dumps(datasets, default=str)
    print('Datasets:', json_data)
    return jsonify(json_data), 200

@app.route('/dataset/<string:dataset_id>/distributions', methods=['GET'])
def get_distributions_by_dataset(dataset_id):
    distributions = list(distributionDB.find({"isPartOf": dataset_id}, {"_id": 0}))
    json_data = json.dumps(distributions, default=str)
    print('Distributions from Dataset ', dataset_id, ' :', json_data)
    return jsonify(json_data), 200


@app.route('/distributions', methods=['GET'])
def get_distributions():
    #TODO: Add user authentication
    """Return all distributions"""
    distributions = list(distributionDB.find({}, {"_id": 0}))
    json_data = json.dumps(distributions, default=str)
    print('Distributions:', json_data)
    return jsonify(json_data), 200



@app.route('/catalog/<string:catalog_id>', methods=['GET'])
def get_catalog(catalog_id):
    #TODO: Add user authentication
    """Return a specific catalog"""
    catalog = catalogDB.find_one({"_id": catalog_id})
    return jsonify(catalog), 200

@app.route('/dataset/<string:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    #TODO: Add user authentication
    """Return a specific dataset"""
    dataset = datasetDB.find_one({"_id": dataset_id})
    return jsonify(dataset), 200



## Project API ##
@app.route('/projects', methods=['GET'])
def get_projects():
    """Return all user's projects"""

    id_token = request.cookies.get('id_token')
    user_id = utils.get_user_id(id_token)
    audit_logger.info(f"GET_PROJECTS | user_id={user_id} | IP={request.remote_addr}")
    if not user_id:
        audit_logger.warning(f"GET_PROJECTS | UNAUTHORIZED | IP={request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 401
    
    projects = list(projectDB.find({'owner': user_id}))  
    
    # Convert ObjectId to string
    for i in range(len(projects)):
        projects[i] = utils.serialize_doc(projects[i])

    json_data = json.dumps(projects, default=str)
    return jsonify(json_data), 200


@app.route('/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    #TODO: Add user authentication
    """Return a specific project"""

    id_token = request.cookies.get('id_token')
    user_id = utils.get_user_id(id_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    project = projectDB.find_one({'owner': user_id, "_id": ObjectId(project_id)})

    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # Convert ObjectId to string
    project = utils.serialize_doc(project)

    return jsonify(project), 200

@app.route('/submit-project', methods=['POST'])
def submit_project():
    """Submit project data to the server"""
    print("Request:", request)
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400 
    
    project_id = project_data['id']
    del project_data['id']
    
    if not project_id:
        return jsonify({"error": "Project ID missing"}), 400
    
    if project_id == 'new':
        projectDB.insert_one(project_data)
        return jsonify({"message": "Project data submitted successfully"})
    
    else:
        projectDB.update_one({"_id": ObjectId(project_id)}, {"$set": project_data})
        return jsonify({"message": "Project data updated successfully"})
    


@app.route('/projects/<string:project_id>', methods=['PATCH'])
def update_project(project_id):
    """Update project data"""
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400
    
    id_token = request.cookies.get('id_token')
    user_id = utils.get_user_id(id_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    ALLOWED_FIELDS = {"status", "last_update", "dataset_uri", "distributions_uri"} 

    # Filter out any fields that are not allowed
    project_data = {k: v for k, v in project_data.items() if k in ALLOWED_FIELDS}

    projectDB.update_one({"_id": ObjectId(project_id), "owner": user_id}, {"$set": project_data})
    return jsonify({"message": "Project updated successfully"})




## File Handling ##
@app.route('/files', methods=['GET'])
def get_files():
    """Return all files"""
    files = list(templateDB.find({}, {"_id": 0}))
    return jsonify(files), 200


@app.route('/files/<string:project_id>', methods=['GET'])
def get_files_by_project(project_id):
    """Return all files for a specific project"""
    files = fs.find({"project_id": project_id})
    file_list = []
    for file in files:
        existing_file = next((f for f in file_list if f["filename"] == file.type), None)
        if existing_file:
            if file.uploadDate > existing_file["upload_date"]:
                file_list.remove(existing_file)
                file_list.append({
                    "filename": file.type,
                    "download_url": f"download/{file._id}",
                    "upload_date": file.uploadDate,
                })
        else:
            file_list.append({
                "filename": file.type,
                "download_url": f"download/{file._id}",
                "upload_date": file.uploadDate,
            })

    for item in file_list:
        item['download_url'] = request.host_url + item['download_url']
    print('Files from project ', project_id)
    print(file_list)
    return jsonify(file_list), 200

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a specific file."""

    file_obj_id = ObjectId(file_id)

    user_id = utils.get_user_id(request.cookies.get('id_token'))
    audit_logger.info(f"DOWNLOAD_FILE | user_id={user_id} | file_id={file_id} | IP={request.remote_addr}")

    try:
        file_data = fs.get(file_obj_id)
        if not file_data:
            return "File not found", 404

        return send_file(
            io.BytesIO(file_data.read()),
            as_attachment=True,
            download_name=file_data.type,
            mimetype="application/pdf"
        )
    except Exception as e:
        return str(e), 500


@app.route('/upload', methods=['POST'])
def upload_signed_file():
    """Receive signed files from users"""

    if 'file' not in request.files:  # Check if 'file' key exists
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    
    if 'project_id' not in request.form:
        return jsonify({"error": "Project ID missing"}), 400
    
    if 'file_type' not in request.form:
        return jsonify({"error": "Document type missing"}), 400

    project_id = request.form.get('project_id')
    file_type = request.form.get('file_type')

    id_token = request.cookies.get('id_token')
    user_id = utils.get_user_id(id_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file.filename = file_type
    fs.put(file , owner=user_id, project_id=project_id, type=file_type)

    user_id = utils.get_user_id(request.cookies.get('id_token'))
    project_id = request.form.get('project_id')
    file_type = request.form.get('file_type')
    filename = request.files['file'].filename if 'file' in request.files else None
    audit_logger.info(f"UPLOAD_FILE | user_id={user_id} | project_id={project_id} | file_type={file_type} | filename={filename} | IP={request.remote_addr}")

    return jsonify({"message": "File uploaded successfully!" })


@app.route('/redirect-rems', methods=['GET'])
def redirect_rems():
    # open new window with rems
    return open('http://localhost:3000')


@app.route('/rems/create_resource', methods=['POST'])
def create_resource():
    # TODO: Adapt to other organizations and add process to add user to the organization
    organization_id = "organization_example"
    resource_id = "pt:biodata.pt:tre:website_resource" 

    # Add user to the organization

    # Create resource

    rems_api_url = "http://localhost:3000/api/resources/create"
    api_key = "bgs6o1u81gasz6x5812bvtg"
    user_id = "robot-org-owner"

    #"content-type: application/json" \
    #-H "x-rems-api-key: $API_KEY" \
    #-H "x-rems-user-id: $USER_ID" \

    headers = {
        "content-type": "application/json",
        "x-rems-api-key": api_key,
        "x-rems-user-id": user_id
    }

    response =  requests.post(rems_api_url, headers=headers, json={
            "resid": resource_id,
            "organization": {
                "organization/id": organization_id # example organization
            },
            "licenses": [1] # license id = 1 => Data processing agreement
        })
    
    print(response.json())
            

    return jsonify(response.json())


@app.route('/pipelines', methods=['GET'])
def get_pipelines():

    raw_pipelines = list(pipelineDB.find({}, {"_id": 0}) )
    print('Pipelines:', raw_pipelines)

    pipelines = []
    for pipeline in raw_pipelines:
        print('Pipeline:', pipeline)
        payload = json.loads(pipeline.get('payload', '{}'))
        pipelines.append({
            "id": pipeline.get('id'),
            "name": payload.get('name'),
            "description": payload.get('description'),
        })

    print('Pipelines:', pipelines)

    return jsonify({"pipelines": pipelines}), 200

@app.route("/run-task", methods=['POST'])
def runTask():
    print (request.json)
    file_id = request.json['file_id']
    pipeline_id = request.json['pipeline_id']

    print (file_id)
    print (pipeline_id)

    #get payload associated to the pipeline
    resp = pipelineDB.find_one({"id": pipeline_id}, {"_id": 0})
    if not resp:
        return jsonify({"error": "Pipeline not found"}), 404

    #get cookies to get the access token
    access_token = request.cookies.get('access_token')
    
    template = resp['payload']
    payload_str = json.dumps(template)

    values = {
    "$FILE_ID": file_id,
    "$TOKEN": access_token
    }

    for key, value in values.items():
        payload_str = payload_str.replace(key, value)

    payload = json.loads(payload_str)

    print (payload)

    response = requests.post(TES_URL, headers={"Accept": "application/json", "Content-Type": "application/json"}, data=payload)
    
    return jsonify(response.json())

@app.route("/run-task/<string:taskId>", methods=['GET'])
def getTask(taskId):
    print ("Task_id: " + taskId)

    response = requests.get(f"{TES_URL}/{taskId}?view=FULL", headers={"Accept": "application/json", "Content-Type": ""}).json()
    print(response)
    if response["state"] == 'COMPLETE':
        output = response['logs'][0]['logs'][0]['stdout']
        print (output)

        return jsonify({"message": "Task completed successfully", "output": output, "state":"COMPLETE"}), 200
    

        # Download the file
        """ download_url = response['outputs'][0]['stdout']
        file_response = requests.get(download_url, stream=True)

        if file_response.status_code == 200:
            # Save the file locally
            with open('output_file', 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return jsonify({"message": "File downloaded successfully"}), 200
        else:
            return jsonify({"error": "Failed to download file"}), file_response.status_code """
    return jsonify(response), 200
    

@app.route("/skos/label", methods=['GET'])
def get_skos_labels():
    uri = request.args.get('uri')
    if not uri:
        return jsonify(error="Missing 'uri' parameter"), 400

    try:
        response = requests.get(uri, headers={"Accept": "application/rdf+xml"})
        if response.status_code != 200:
            return jsonify(error="Failed to fetch RDF data"), 502

        xml = response.text
        root = ET.fromstring(xml)

        ns = {
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'xml': 'http://www.w3.org/XML/1998/namespace'
        }

        labels = {}
        for label in root.findall('.//skos:prefLabel', ns):
            lang = label.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang and label.text:
                labels[lang] = label.text

        return jsonify({
            "uri": uri,
            "prefLabel": labels
        })

    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/contact-info')
def get_contact_info():
    uri = request.args.get('uri')
    print("[DEBUG] Received URI:", uri)
    if not uri:
        print("[DEBUG] No URI provided in request")
        return jsonify({"error": "Missing uri"}), 400

    try:
        if "orcid.org" in uri:
            print("[DEBUG] Detected ORCID URI")
            orcid_id = uri.split("/")[-1]
            print("[DEBUG] ORCID ID:", orcid_id)

            headers = {"Accept": "application/json"}
            resp = requests.get(f"https://pub.orcid.org/v3.0/{orcid_id}", headers=headers)
            print("[DEBUG] ORCID API response status:", resp.status_code)
            data = resp.json()
            print("[DEBUG] ORCID API response data:", data.get('person', {}))

            name = f"{data['person']['name']['given-names']['value']} {data['person']['name']['family-name']['value']}"
            print("[DEBUG] Extracted name:", name)

            return jsonify({"name": name})

        elif "ror.org" in uri:
            print("[DEBUG] Detected ROR URI")
            ror_id = uri.split("/")[-1]
            print("[DEBUG] ROR ID:", ror_id)
            resp = requests.get(f"https://api.ror.org/v2/organizations/{ror_id}")
            print("[DEBUG] ROR API response status:", resp.status_code)
            if resp.status_code != 200:
                print("[DEBUG] Failed to fetch ROR data")
                return jsonify({"error": "Failed to fetch ROR data"}), 502
            data = resp.json()
            print("[DEBUG] ROR API response data:", data)
            names = data.get('names', 'Unknown')
            print("[DEBUG] Extracted names:", names)

            for entrie in names:
                print("[DEBUG] Checking entry:", entrie)
                if 'label' in entrie.get('types', []):
                    name = entrie.get('value')
                    print("[DEBUG] Found English name:", name)
                    return jsonify({"name": name})

            print("[DEBUG] No English name found, using first entry")
            return jsonify({"name": names[0].get('value'), "email": None})

        else:
            print("[DEBUG] Unsupported UID format")
            return jsonify({"error": "Unsupported UID format"}), 400

    except Exception as e:
        print("[DEBUG] Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    audit_logger.info("SERVER_START")
    app.run(port=API_PORT, debug=True)
