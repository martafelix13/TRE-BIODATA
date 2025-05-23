import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RemsService {

  //private remsUrl = 'http://localhost:3000'; // must have a ssh connection active to the server
  private backendUrl = environment.serverUrl;


  constructor(private http: HttpClient) {}

  redirectToRemsCatalog(): void {
    //window.location.href = `${this.remsUrl}/catalogue`;
  }

  redirectToRemsAdmin(): void {
    //window.location.href = `${this.remsUrl}/administration/catalogue-items`;
  }

  createResource(name: string) {
    //return this.http.post(`${this.backendUrl}/rems/create_resource`,{filename: name});
  }
}
