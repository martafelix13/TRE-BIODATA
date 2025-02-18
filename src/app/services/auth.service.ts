import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {


  private backendUrl = 'http://localhost:8080'; 

  constructor(private router: Router, private http: HttpClient) {}
    
  
  
  login(): void {
      window.location.href=`${this.backendUrl}/login`;
  }

  handleCallback(): void {
    console.log('Handling callback')
    const urlParams = new URLSearchParams(window.location.search);

    const code = urlParams.get('code');  // Extract the "code" from the URL query parameters

    if (code) {
      this.exchangeCodeForToken(code);  // Send the code to the backend for token exchange
    } else {
      console.error('No authorization code returned');
    }
  }

  exchangeCodeForToken(code: string): void {
    this.http.get(`${this.backendUrl}/oidc-callback?code=${code}`).subscribe(
      (response: any) => {
        console.log('Access Token:', response.access_token);
        console.log('ID Token:', response.id_token);
        
        this.router.navigate(['/']);
      },
      (error) => {
        console.error('Error exchanging authorization code for token:', error);
      }
    );
  }

}
