import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class FileService {
  private baseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) {}

  getFiles() {
    return this.http.get(`${this.baseUrl}/files`);
  }

  downloadFile(filename: string) {
    return this.http.get(`${this.baseUrl}/download/${filename}`);
  }

  uploadSignedFile(formData: FormData): Observable<any> {
    console.log('Uploading file: ', formData);
    return this.http.post(`${this.baseUrl}/upload`, formData, {withCredentials: true});
  }

  getFilesByProject(project_id: string) {
    return this.http.get(`${this.baseUrl}/file/`+ project_id);
  }
}
