from flask import Flask, json, request, redirect, jsonify, make_response
import requests
import jwt
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app, supports_credentials=True)

CLIENT_ID = 'metadados-tre'
CLIENT_SECRET = 'esparguete'
REDIRECT_URI = 'http://localhost:8080/oidc-callback'
LOGIN_URL = 'https://kc.portal.gdi.biodata.pt/oidc/auth/authorize'
AUTHORIZATION_URL = 'https://kc.portal.gdi.biodata.pt/oidc/token'
USER_INFO_URL = 'https://kc.portal.gdi.biodata.pt/oidc/userinfo'
FRONTEND_URL = 'http://localhost:4200'


client = MongoClient("mongodb://localhost:27017/")  # Change to your MongoDB connection URI
db = client["metadata"]
catalogDB = db["catalog"]
datasetDB = db["dataset"]
distributionDB = db["distribution"]


id_token = None
access_token = None
token_type = None
user = None

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
    """Return all catalogs"""
    data = list(catalogDB.find({}, {"_id": 0}))  # Fetch data from MongoDB
    json_data = json.dumps(data, default=str)
    print('Catalogs:', json_data)
    return jsonify(json_data), 200

@app.route('/datasets', methods=['GET'])
def get_datasets():
    """Return all datasets"""
    datasets = list(datasetDB.find({}, {"_id": 0}))
    json_data = json.dumps(datasets, default=str)
    print('Datasets:', json_data)
    return jsonify(json_data), 200

@app.route('/distributions', methods=['GET'])
def get_distributions():
    """Return all distributions"""
    distributions = list(distributionDB.find({}, {"_id": 0}))
    json_data = json.dumps(distributions, default=str)
    print('Distributions:', json_data)
    return jsonify(json_data), 200

@app.route('/catalog/<string:catalog_id>', methods=['GET'])
def get_catalog(catalog_id):
    """Return a specific catalog"""
    catalog = catalogDB.find_one({"_id": catalog_id})
    return jsonify(catalog), 200

@app.route('/dataset/<string:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Return a specific dataset"""
    dataset = datasetDB.find_one({"_id": dataset_id})
    return jsonify(dataset), 200


if __name__ == '__main__':
    app.run(port=8080, debug=True)
