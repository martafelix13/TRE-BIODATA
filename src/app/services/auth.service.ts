import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {


  user: any = null;

  private backendUrl = 'http://localhost:8080';
  private userSubject = new BehaviorSubject<any>(null);
  public user$ = this.userSubject.asObservable(); 

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
    this.http.get(`${this.backendUrl}/oidc-callback?code=${code}`, { withCredentials: true })
      .subscribe({
        //next: () => this.loadUserData(),
        error: (error) => console.error('Error exchanging code:', error)
      });
  }

  loadUserData(): void {
    this.http.get(`${this.backendUrl}/api/user`, { withCredentials: true })
      .subscribe({
        next: (user) => {
          console.log( user);

          this.userSubject.next(user); // Store user data
          this.router.navigate(['/']); // Redirect to home
        },
        error: (error) => {
          console.error('Error getting user data:', error);
          this.userSubject.next(null);
        }
      });
  }

  setUserData(userData: any): void {
    this.user =  userData;
  }

  getUserData() {
    return this.user;
  }

  isLogged(): boolean {
    return this.user !== null;
  }

  logout(): void {
    //this.userSubject.next(null);
    this.user = null;
    this.router.navigate(['/']);
  }
}
