import datetime
import io
from flask import Flask, json, request, redirect, jsonify, make_response, send_file, send_from_directory
import gridfs
import requests
import jwt
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

CLIENT_ID = 'metadados-tre'
CLIENT_SECRET = 'esparguete'
REDIRECT_URI = 'http://localhost:8080/oidc-callback'
LOGIN_URL = 'https://kc.portal.gdi.biodata.pt/oidc/auth/authorize'
AUTHORIZATION_URL = 'https://kc.portal.gdi.biodata.pt/oidc/token'
USER_INFO_URL = 'https://kc.portal.gdi.biodata.pt/oidc/userinfo'
FRONTEND_URL = 'http://localhost:4200'

TEMPLATES_FOLDER = "templates"
SIGNED_FOLDER = "signed_files"
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

client = MongoClient("mongodb://localhost:27017/")  # Change to your MongoDB connection URI
dbMetadada = client["metadata"]
catalogDB = dbMetadada["catalog"]
datasetDB = dbMetadada["dataset"]
distributionDB = dbMetadada["distribution"]

dbProject = client["project"]
projectDB = dbProject["project_details"]

templateDB = dbProject["templates"]

dbFiles = client["files_system"]
fs = gridfs.GridFS(dbFiles)


#fs = gridfs.GridFS(signedDocumentsDB)


id_token = None
access_token = None
token_type = None
user = None

def get_user_id(): 
    id_token = request.cookies.get('id_token')
    print ('id_token: ' + id_token)
    if not id_token:
        print ('id_token not found')
        return None
    
    try:
        user = jwt.decode(id_token, CLIENT_SECRET, options={"verify_signature": False, "verify": False}).get("sub")  # Use the correct signing algorithm
        print(user)
        return user

    except jwt.ExpiredSignatureError:
        print ('ExpiredSignatureError')
        return None
    
    except jwt.InvalidTokenError:
        print('InvalidTokenError')
        return None



## Authentication and Authorization ##
@app.route('/login')
def login():
    """Redirect user to the OAuth login page"""
    login_url = f"{LOGIN_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20profile%20email"
    print(f"Redirecting user to: {login_url}")
    return redirect(login_url)

@app.route('/oidc-callback')
def oidc_callback():
    global id_token, access_token, token_type

    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code missing"}), 400

    token_request_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid profile email",
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

    return resp


@app.route('/api/user')
def get_user():
    """Return user data separately"""
    access_token = request.cookies.get('access_token')
    token_type = request.cookies.get('token_type')

    if not access_token or not token_type:
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch user info
    response = requests.post(USER_INFO_URL, headers={'Authorization': f"{token_type} {access_token}"})

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info"}), response.status_code
    
    print(response.json())

    return response.json()


## Metadata API ##
@app.route('/submit-form', methods=['POST'])
def submit_form():
    """Submit form data to the server"""
    form_data = request.json

    if (not form_data):
        return jsonify({"error": "Form data missing"}), 400
    
    if (form_data.get("type") == "catalog"):
        print("Form Data:", form_data)
        catalogDB.insert_one(form_data)
    
    elif (form_data.get("type") == "dataset"):
        print("Form Data:", form_data)
        datasetDB.insert_one(form_data)

    elif (form_data.get("type") == "distribution"):
        print("Form Data:", form_data)
        distributionDB.insert_one(form_data)

    else:
        return jsonify({"error": "Invalid form type"}), 400
    
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

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    projects = list(projectDB.find({'owner': user_id}, {"_id": 0}))  
    json_data = json.dumps(projects, default=str)
    print('Projects:', json_data)
    return jsonify(json_data), 200


@app.route('/project/<string:project_id>', methods=['GET'])
def get_project(project_id):
    #TODO: Add user authentication
    """Return a specific project"""

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    print('User ID:', user_id)
    print('Project ID:', project_id)
    project = projectDB.find_one({'owner': user_id, "id": project_id},  {"_id": 0})
    return jsonify(project), 200

@app.route('/submit-project', methods=['POST'])
def submit_project():
    """Submit project data to the server"""
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400 
    
    print("Project Data:", project_data)
    projectDB.insert_one(project_data)
    
    return jsonify({"message": "Project data submitted successfully"})

@app.route('/update-project/<string:project_id>', methods=['PUT'])

def update_project(project_id):
    """Update project data"""
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400

    projectDB.update_one({"id": project_id}, {"$set": project_data})
    return jsonify({"message": "Project data updated successfully"})

@app.route('/delete-project/<string:project_id>', methods=['DELETE'])

def delete_project(project_id):
    """Delete a project"""
    
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    projectDB.delete_one({'owner': user, "id": project_id})
    return jsonify({"message": "Project deleted successfully"})

@app.route('/project/update-status/<string:project_id>', methods=['PUT'])
def update_project_status(project_id):
    """Update project status"""
    project_status = request.json
    projectDB.update_one({"id": project_id}, {"$set": {"status": project_status}})
    return jsonify({"message": "Project status updated successfully"})


## File Handling ##
@app.route('/files', methods=['GET'])
def get_files():
    """Return all files"""
    files = list(templateDB.find({}, {"_id": 0}))
    return jsonify(files), 200


@app.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    print("Downloading file:", filename)
    response = templateDB.find_one({"filename": filename}, {"_id": 0})
    if not response:
        return jsonify({"error": "File not found"}), 404
    
    print(response)

    return jsonify(response), 200

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

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file.filename = file_type
    fs.put(file , owner=user_id, project_id=project_id, type=file_type)
    return jsonify({"message": "File uploaded successfully!" })




if __name__ == '__main__':
    app.run(port=8080, debug=True)
