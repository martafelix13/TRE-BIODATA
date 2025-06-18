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

  // Download a file by its filename and project ID
  downloadTemplateFile(filename: string, projectId: string): Observable<Blob> {
    const url = `${this.backendUrl}/files/download/template/${projectId}/${filename}`;
    return this.http.get(url, { responseType: 'blob' });
  }

  // Get a signed URL for downloading a file
  getSignedDownloadUrl(filename: string, projectId: string): Observable<Blob> {
    const url = `${this.backendUrl}/files/download/signed/${projectId}/${filename}`;
    return this.http.get(url, { responseType: 'blob' });
  }

  // Upload a file to the server
  uploadFile(file: File, projectId: string): Observable<any> {
    const url = `${this.backendUrl}/files/upload-signed/${projectId}`;
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(url, formData);
  }

}
