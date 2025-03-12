import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient } from '@angular/common/http';

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
    return this.http.get(this.backendUrl + '/project/' + id, { withCredentials: true });
  }

  saveProject(project: any) {
    console.log('Project to save: ', project);

    project.last_update = new Date().toISOString().split('T')[0];
    project.owner = this.user_id;
    project.status = 'P-AR';

    if (project.id === 'new') {
      //project.id = this.projects.length + 1;
    }

    return this.http.post(this.backendUrl + '/submit-project', project)
  }

  deleteProject(id: string) {
    return this.http.delete(this.backendUrl + '/projects/' + id);
  }


}
