import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class FileService {
  private backendUrl = environment.serverUrl;
  
  constructor(private http: HttpClient) {}

  getFiles() {
    return this.http.get(`${this.backendUrl}/files`);
  }

  downloadFile(filename: string) {
    return this.http.get(`${this.backendUrl}/files/download/${filename}`);
  }

  uploadSignedFile(formData: FormData): Observable<any> {
    console.log('Uploading file: ', formData);
    return this.http.post(`${this.backendUrl}/files/upload`, formData, {withCredentials: true});
  }

  getFilesByProject(project_id: string) {
    return this.http.get(`${this.backendUrl}/files/`+ project_id);
  }
}
