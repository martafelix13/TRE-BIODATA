import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ProjectsService {

  projects = [
    {
      id: '1',
      title: 'Project 1',
      description: 'Description of Project 1',
      last_update: '2025-01-01',
      organization: 'Organization 1',
      status: 'P-E',
      owner: 'marta.felix@lifescience-ri.eu',
      internal_storage: true
    },
    {
      id: '2',
      title: 'Project 2',
      description: 'Description of Project 2',
      last_update: '2025-02-05',
      organization: 'Organization 1',
      status: 'P-E',
      owner: 'marta.felix@lifescience-ri.eu',
      internal_storage: false
    },
    {
      id: '3',
      title: 'Project 3',
      description: 'Description of Project 3',
      last_update: '2024-12-20',
      organization: 'Organization 1',
      status: 'P-E',
      owner: 'marta.felix@lifescience-ri.eu',
      internal_storage: true
    }
  ];

  user_id = '';
  private backendUrl = 'http://localhost:8080';

  
  constructor(private authService : AuthService, private http: HttpClient) { 
    this.authService.user$.subscribe(user => {
      if (user) {
        this.projects = this.projects.filter((project: { owner: string; }) => project.owner === user.sub);
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
      project.id = this.projects.length + 1;
    }

    return this.http.post(this.backendUrl + '/submit-project', project)
  }

  deleteProject(id: string) {
    return this.http.delete(this.backendUrl + '/projects/' + id);
  }

    
  

}
