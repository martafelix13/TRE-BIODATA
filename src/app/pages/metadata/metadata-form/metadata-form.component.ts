import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import * as uuid from 'uuid';
import { MetadataUploadService } from '../../../services/metadata-upload.service';
import { AuthService } from '../../../services/auth.service';


@Component({
  selector: 'app-metadata-form',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './metadata-form.component.html',
  styleUrl: './metadata-form.component.scss'
})
export class MetadataFormComponent {
  
  savedCatalogs: any[] = [];
  savedDatasets: any[] = [];
  savedDistributions: any[] = [];

  catalogForm: FormGroup;
  datasetForm: FormGroup;
  distributionForm: FormGroup;

  type = 'catalog';
  type_options = ['catalog', 'dataset', 'distribution'];

    constructor(private fb: FormBuilder, private metadataUploadService: MetadataUploadService, private authService: AuthService) {
      
      this.catalogForm = this.fb.group({
        title: ['', Validators.required],
        version: ['', Validators.required],
        publisher: ['', Validators.required],
        homePage: [''],
        rights: [''],
        license: [''],
        language: [''],
        description: [''],
        user_id: [authService.getIdToken()]
      });

      this.datasetForm = this.fb.group({
        title: ['', Validators.required],
        version: ['', Validators.required],
        publisher: ['', Validators.required],
        theme: ['', Validators.required, Validators.pattern('http://+.*')],
        modified: ['', Validators.pattern('%d%d%d%d-%d%d-%d%d')],
        issued: ['', Validators.pattern('%d%d%d%d-%d%d-%d%d')],
        license: [''],
        description: [''],
        isPartOf: ['', Validators.required],
        user_id: [authService.getIdToken()]
      });

      this.distributionForm = this.fb.group({
        isPartOf: ['', Validators.required],
        title: ['', Validators.required],
        description: [''],
        license: [''],
        mediaType: ['', Validators.required],
        version: ['', Validators.required],
        format: [''],
        publisher: ['', Validators.required],
        user_id: [authService.getIdToken()]
      });

  }
  
  ngOnInit(): void {
      this.getCatalogs();
      this.getDatasets();
      this.getDistributions();
  }

  

  saveForm(type:string) {

    if (type === 'catalog') {
      this.metadataUploadService.submitForm(this.catalogForm.value, 'catalog').subscribe(
        (data) => {
          this.getCatalogs();
        },
        (error) => {
          console.error('Error saving form:', error);
        }
      )
    } else if (type === 'dataset') {
      this.metadataUploadService.submitForm(this.datasetForm.value, 'dataset').subscribe(
        (data) => {
          this.getDatasets();
        },
        (error) => {
          console.error('Error saving form:', error);
        }
      )
    } else if (type === 'distribution') {
      this.metadataUploadService.submitForm(this.distributionForm.value, 'distribution').subscribe(
        (data) => {
          this.getDistributions();
        },
        (error) => {
          console.error('Error saving form:', error);
        }
      )
      
    }    
    this.resetForm();
  }

  getCatalogs() {
    this.metadataUploadService.getCatalogs().subscribe((data: any) => {
      console.log("loaded catalogs:") 
      console.log(data)
      this.savedCatalogs = data;
    });
  }

  getDatasets() {
    this.metadataUploadService.getDatasets().subscribe((data: any) => {
      console.log("loaded datasets:") 
      console.log(data)
      this.savedDatasets = data;
    });
  }

  getDistributions() {
    this.metadataUploadService.getDistributions().subscribe((data: any) => {
      console.log("loaded dsitributions:") 
      console.log(data)
      this.savedDistributions = data;
    });
  }


  resetForm(){
    this.catalogForm.reset();
    this.datasetForm.reset();
    this.distributionForm.reset();
  }

  isInvalid(field: string) {
    if (this.type === 'catalog') {
      if (this.catalogForm.get(field)){
        return this.catalogForm.get(field)?.invalid && this.catalogForm.get(field)?.touched;
      }
    }

    if (this.type === 'dataset') {
      if (this.datasetForm.get(field)){
        return this.datasetForm.get(field)?.invalid && this.datasetForm.get(field)?.touched;
      }
    }

    if (this.type === 'distribution') {
      if (this.distributionForm.get(field)){
        return this.distributionForm.get(field)?.invalid && this.distributionForm.get(field)?.touched;
      }
    }

    return false;
  }

}
