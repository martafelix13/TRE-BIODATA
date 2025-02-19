const express = require('express');
const axios = require('axios');
const cors = require('cors'); 
const jwt = require('jsonwebtoken');
const app = express();
const port = 8080;  

const CLIENT_ID = 'metadados-tre';
const CLIENT_SECRET = 'esparguete';
const REDIRECT_URI = 'http://localhost:8080/oidc-callback'; 
const LOGIN_URL = 'https://kc.portal.gdi.biodata.pt/oidc/auth/authorize'; 
const AUTHORIZATION_URL = 'https://kc.portal.gdi.biodata.pt/oidc/token';  
const USER_INFO_URL = 'https://kc.portal.gdi.biodata.pt/oidc/userinfo';  

const FRONTEND_URL = 'http://localhost:4200';

app.use(cors({ origin: 'http://localhost:4200', credentials: true }));
app.use(express.json());

app.get('/login', (req, res) => {
  const lsLoginUrl = `${LOGIN_URL}?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&scope=openid%20profile%20email`;
  console.log("Redirecting user to:", lsLoginUrl);
  res.redirect(lsLoginUrl);
});


app.get('/oidc-callback', async (req, res) => {

  console.log("Received /callback request:", req.query);
  const { code } = req.query;

  if (!code) return res.status(400).json({ error: "Authorization code missing" });
  console.log("Received authorization code:", code);
  
  try {
    
    const requestConfig = {
    url: AUTHORIZATION_URL,
    method: 'POST',
    headers: {'content-type': 'application/x-www-form-urlencoded'},
    data: {
        code: code,
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        scope: 'openid profile email',
        redirect_uri: REDIRECT_URI,
        requested_token_type: 'urn:ietf:params:oauth:token-type:refresh_token',
        grant_type: 'authorization_code'
      }
    };


    axios.request(requestConfig).then(function (response) {
      console.log(response.data);

      const id_token = response.data.id_token;
      const token_type = response.data.token_type;
      const access_token = response.data.access_token;  

      axios.request({
          url: USER_INFO_URL,
          method: 'POST',
          headers: {'Authorization': `${token_type} ${access_token}`}
        }).then(response => {
          console.log(response.data);
          const userData = response.data;
          res.redirect(`${FRONTEND_URL}/?name=${userData.name}&email=${userData.email}`);
      });
      
    });

  } catch (error) {
    console.error("Error during authentication:", error);
    res.redirect('http://localhost:4200/error'); 
  }
});


app.get('/api/user', (req, res) => {
  console.log("Received /api/user request");

  const token = req.cookies.authToken
  if (!token) return res.status(401).json({ message: "Unauthorized" });

  try {
      const userData = jwt.verify(token, CLIENT_SECRET);
      console.log("User data:", userData);
      res.json(userData);
  } catch (error) {
      res.status(403).json({ message: "Invalid token" });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Backend server running at http://localhost:${port}`);
});


