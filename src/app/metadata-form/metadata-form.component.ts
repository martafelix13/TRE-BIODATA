import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import * as uuid from 'uuid';


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

  type: string = 'catalog';
  type_options = ['catalog', 'dataset', 'distribution'];

    constructor(private fb: FormBuilder) {
      
      this.catalogForm = this.fb.group({
        id: [uuid.v4()],
        title: ['', Validators.required],
        version: ['', Validators.required],
        publisher: ['', Validators.required],
        homePage: [''],
        rights: [''],
        license: [''],
        language: [''],
        description: [''],
      });

      this.datasetForm = this.fb.group({
        id: [uuid.v4()],
        title: ['', Validators.required],
        version: ['', Validators.required],
        publisher: ['', Validators.required],
        theme: ['', Validators.required, Validators.pattern('http://+.*')],
        modified: ['', Validators.pattern('%d%d%d%d-%d%d-%d%d')],
        issued: ['', Validators.pattern('%d%d%d%d-%d%d-%d%d')],
        license: [''],
        description: [''],
        isPartOf: ['', Validators.required],
      });

      this.distributionForm = this.fb.group({
        id: [uuid.v4()],
        isPartOf: ['', Validators.required],
        title: ['', Validators.required],
        description: [''],
        license: [''],
        mediaType: ['', Validators.required],
        version: ['', Validators.required],
        format: [''],
        publisher: ['', Validators.required],

      });

  }
  
  ngOnInit(): void {}

  

  saveForm(type:string) {
    if (type === 'catalog') {
      this.savedCatalogs.push(this.catalogForm.value);
    } else if (type === 'dataset') {
      this.savedDatasets.push(this.datasetForm.value);
    } else if (type === 'distribution') {
      this.savedDistributions.push(this.distributionForm.value);
    }
    this.resetForm();
  }


  resetForm(){
    this.catalogForm.reset();
    this.datasetForm.reset();
    this.distributionForm.reset();
  }



}
