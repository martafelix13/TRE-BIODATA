import io
from bson import ObjectId
from flask import Flask, json, request, redirect, jsonify, make_response, send_file
import gridfs
import requests
import jwt
from flask_cors import CORS
from pymongo import MongoClient
import os
from settings import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


client = MongoClient(MONGO_URI)  
dbMetadada = client["metadata"]
catalogDB = dbMetadada["catalog"]
datasetDB = dbMetadada["dataset"]
distributionDB = dbMetadada["distribution"]

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
    
    # save user data in the database as user.sub -> user.info
    user = {
        "id": response.json().get("sub"),
        "user_info": response.json()
    }

    if not userDB.find_one({"id": user.get("id")}):
        userDB.insert_one(user)

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
    return jsonify(json_data), 200


@app.route('/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    #TODO: Add user authentication
    """Return a specific project"""

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    project = projectDB.find_one({'owner': user_id, "id": project_id},  {"_id": 0})
    return jsonify(project), 200

@app.route('/submit-project', methods=['POST'])
def submit_project():
    """Submit project data to the server"""
    print("Request:", request)
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400 
    
    project_id = project_data['id']
    
    if not project_id:
        return jsonify({"error": "Project ID missing"}), 400
    
    existing_id = projectDB.find_one({"id": project_id})

    if existing_id:
        projectDB.update_one({"id": project_id}, {"$set": project_data})
        return jsonify({"message": "Project data updated successfully"})
    
    else:
        projectDB.insert_one(project_data)
        return jsonify({"message": "Project data submitted successfully"})



@app.route('/projects/<string:project_id>', methods=['PATCH'])
def update_project(project_id):
    """Update project data"""
    project_data = request.json

    if (not project_data):
        return jsonify({"error": "Project data missing"}), 400
    
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    projectDB.update_one({"id": project_id, "owner": user_id}, {"$set": project_data})
    return jsonify({"message": "Project updated successfully"})


## File Handling ##
@app.route('/files', methods=['GET'])
def get_files():
    """Return all files"""
    files = list(templateDB.find({}, {"_id": 0}))
    return jsonify(files), 200


@app.route('/file/<string:project_id>', methods=['GET'])
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

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file.filename = file_type
    fs.put(file , owner=user_id, project_id=project_id, type=file_type)
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
                "organization/id": organization_id
            },
            "licenses": [1]
        })
    
    print(response.json())
            

    return jsonify(response.json())


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

    response = requests.get(f"{TES_URL}/{taskId}?view=FULL", headers={"Accept": "application/json", "Content-Type": ""})
    return jsonify(response.json())
    
if __name__ == '__main__':
    app.run(port=8080, debug=True)
