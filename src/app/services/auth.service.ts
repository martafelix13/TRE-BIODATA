import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { CookieService } from 'ngx-cookie-service';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private backendUrl = 'http://localhost:8080';
  private userSubject = new BehaviorSubject<any>(null);
  public user$ = this.userSubject.asObservable();

  constructor(
    private router: Router, 
    private http: HttpClient, 
    private cookieService: CookieService
  ) {
    this.loadUserData();
  }

  /** Redirect user to login page */
  login(): void {  
    window.location.href = `${this.backendUrl}/login`;
  }  

  handleCallback(): void {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');  // Extract "code" from URL
  
    if (code) {
      this.exchangeCodeForToken(code);  
    } else {
      console.error('No authorization code found in callback URL');
    }
  }
  

  exchangeCodeForToken(code: string): void {
    this.http.get(`${this.backendUrl}/oidc-callback?code=${code}`, { withCredentials: true })
      .subscribe({
        next: () => {
          console.log('Tokens set in cookies, redirecting...');
          this.loadUserData();  
        },
        error: (error) => console.error('Error exchanging code:', error)
      });
  }

  loadUserData(): void {
    this.http.get(`${this.backendUrl}/api/user`, { withCredentials: true })
      .subscribe({
        next: (user) => {
          console.log('User data received:', user);
          this.userSubject.next(user); 
          this.router.navigate(['/']); 
        },
        error: (error) => {
          console.error('Error getting user data:', error);
          this.userSubject.next(null);
        }
      });
  }

  isLogged(): boolean {
    return this.userSubject.value !== null;
  }

  /** Logs out the user */
  logout(): void {
    this.cookieService.delete('id_token', '/');
    this.cookieService.delete('access_token', '/');
    this.cookieService.delete('token_type', '/');
    this.cookieService.delete('user', '/');
    this.userSubject.next(null);
    this.router.navigate(['/']); 
  }

  getIdToken(): string {
    return this.userSubject.value.sub;
  }

  redirectIfNotLoggedIn(): void {
    if (!this.isLogged()) {
      this.login();
    }
  }
  
}
