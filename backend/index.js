const express = require('express');
const axios = require('axios');
const cors = require('cors'); 
const app = express();
const port = 8080;  

const CLIENT_ID = 'metadados-tre';
const CLIENT_SECRET = 'esparguete';
const REDIRECT_URI = 'http://localhost:8080/oidc-callback'; 
const LOGIN_URL = 'https://kc.portal.gdi.biodata.pt/oidc/login'; 
const AUTHORIZATION_URL = 'https://kc.portal.gdi.biodata.pt/oidc/authorize';  

// Enable CORS so your Angular frontend can make requests to the backend
app.use(cors());

// Endpoint to initiate the OAuth login flow
app.get('/login', (req, res) => {
  const lsLoginUrl = `${LOGIN_URL}?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scopes=openid%20profile%20email%5Ccountry%20ga4gh_passport_v1`;

  console.log("Redirecting user to:", lsLoginUrl);
  res.redirect(lsLoginUrl); // Redirect the user to the LS Login page


});

// Endpoint to handle OAuth callback and exchange authorization code for access token
app.get('/oidc-callback', async (req, res) => {

  console.log("Received /callback request:", req.query);

  const { code, state } = req.query;
  if (!code) {
      console.error("Authorization code is missing.");
      return res.status(400).send("Authorization code is required.");
  }

  console.log("Received authorization code:", code);
  console.log("Received state:", state);


  try {
    // Exchange the code for an access token
    const tokenResponse = await axios.post(AUTHORIZATION_URL, {
      code: code,
      state: state,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
    });

    res.json({
      access_token: tokenResponse.data.access_token,
      refresh_token: tokenResponse.data.refresh_token,
      expires_in: tokenResponse.data.expires_in,
    });


  } catch (error) {
    console.error('Error exchanging authorization code for token:', error);
    res.status(500).send('Error exchanging authorization code');
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Backend server running at http://localhost:${port}`);
});


