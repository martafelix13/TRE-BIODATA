import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient } from '@angular/common/http';
import { UUID } from 'mongodb';

@Injectable({
  providedIn: 'root'
})
export class ProjectsService {

  user_id = '';
  private backendUrl = 'http://localhost:8080';

  
  constructor(private authService : AuthService, private http: HttpClient) { 
    this.authService.user$.subscribe(user => {
      if (user) {
        this.user_id = user.sub;     
      } else {
        console.error('No user logged in');
        return;
      }
    });
  }

  getProjects() {
    return this.http.get(this.backendUrl + '/projects', { withCredentials: true });
  }

  getProject(id: string) {
    return this.http.get(this.backendUrl + '/projects/' + id, { withCredentials: true });
  }

  saveProject(project: any) {
    project.last_update = new Date().toISOString().split('T')[0];
    project.id = Math.random().toString(36).substring(2, 8);
    project.owner = this.user_id;
    project.responsable='';
    project.status = 'P-AR';
    console.log('Project to save: ', project);
    return this.http.post(this.backendUrl + '/submit-project', project)
  }

  updateProjectStatus(id: string, newStatus: string) {
    const updateData = { status: newStatus };
    return this.http.patch(this.backendUrl + '/projects/' + id, updateData, { withCredentials: true });
  }
}
