import { Component, Input, OnInit } from '@angular/core';
import { FileService } from '../../services/file.service';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ActivatedRoute } from '@angular/router';
import {MatIconModule} from '@angular/material/icon';
import { GSSAPICanonicalizationValue, StrictMatchKeysAndValues } from 'mongodb';
import { ProjectsService } from '../../services/projects.service';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-file-management',
  imports: [CommonModule, MatIconModule, MatCardModule],
  templateUrl: './file-management.component.html',
  styleUrls: ['./file-management.component.css'],
})
export class FileManagementComponent implements OnInit {
  @Input() project_id = '';
  @Input() status = '';


  files: any;
  selectedFile: File | null = null;
  user_id: string = '';
  //project_id: string = '';

  selectedFiles: Map<string, File> = new Map();

  fileList = [];

  constructor(
    private fileService: FileService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private projectService: ProjectsService
  ) {
    // check if the user is logged in
    authService.user$.subscribe((user) => {
      this.user_id = user?.sub;
      if (!user) {
        authService.login();
      }
    });
  }

  ngOnInit() {
    console.log('Project ID: ', this.project_id);
    console.log("Status: " + this.status)

    if (this.status == 'A-E') {
         this.fileService.getFiles().subscribe((data) => {
      this.files = data;
      console.log('Files: ', this.files);
      });
    } else if (this.status == 'A-AR') {
      this.getFilesByProjectId();
    }
  }

  download(filename: string) {
    this.fileService.downloadFile(filename).subscribe((data: any) => {
      const url = data.path
      window.open(url);
    });
  }

  

  onFileSelected(event: any, file: any) {
    this.selectedFile = event.target.files[0];
    console.log('Selected file: ', this.selectedFile);
    console.log(file);
    if (this.selectedFile) {
      this.selectedFiles.set(file.filename, this.selectedFile!);
    }
  }

  upload() {

    if (this.selectedFiles.size != this.files.length) {
      alert('Please sign all files before uploading');
      return
    }

    this.selectedFiles.forEach((file, key) => {
      console.log('Uploading file: ', key);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', this.project_id);
      formData.append('file_type', key);
      this.fileService.uploadSignedFile(formData).subscribe({
        next: (res) => { 
          console.log('Response: ', res); 
            this.projectService.updateProjectStatus(this.project_id, "A-AR").subscribe({
              next: (res) => {alert('File uploaded successfully!');},
              error:(err) => {console.error("Error: ", err);}
            })
        },
        error: (err) => { console.error('Error: ', err);
          alert('Upload Failed.');
         }
      });
    }); 
  }


  getFilesByProjectId() {
    console.log("Inside getFilesByProjectId")
    this.fileService.getFilesByProject(this.project_id).subscribe({
      next: (res: any) => {
        console.log("Get Files by project Id: ")
        console.log(res)
        this.fileList = res;
      },
      error: (err) => { console.error("Error: " + err) }
    })
  }

  downloadFile(url: string) {
    window.open(url, '_blank'); 
  }


}
