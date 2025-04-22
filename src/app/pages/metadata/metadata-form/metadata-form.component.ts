import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import * as uuid from 'uuid';
import { MetadataUploadService } from '../../../services/metadata-upload.service';
import { AuthService } from '../../../services/auth.service';
import { ProjectsService } from '../../../services/projects.service';

const DATASET = 'dataset';
const DISTRIBUTION = 'distribution';


@Component({
  selector: 'app-metadata-form',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './metadata-form.component.html',
  styleUrl: './metadata-form.component.scss'
})
export class MetadataFormComponent {
  @Input() project: any;
  
  //savedCatalogs: any[] = [];
  savedDatasets: any[] = [];
  savedDistributions: any[] = [];

  //catalogForm: FormGroup;
  datasetForm: FormGroup;
  distributionForm: FormGroup;

  selectItem: any;

  user_id = '';

  selectedType = DATASET;

  formOptions = [
    { label: 'Dataset', value: DATASET },
    { label: 'Distribution', value: DISTRIBUTION }
  ]

    constructor(private fb: FormBuilder, private metadataUploadService: MetadataUploadService, private authService: AuthService, private projectService: ProjectsService) {
      
/*       this.catalogForm = this.fb.group({
        id: [''],
        title: ['', Validators.required],
        version: ['', Validators.required],
        publisher: ['', Validators.required],
        publisher_email: ['',  Validators.required],
        homePage: [''],
        rights: [''],
        license: [''],
        language: [''],
        description: [''],
        themeTaxonomy: [''],
        isPartOf: [''],
        user_id: [''],
        project_id: ['']
      });
 */
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
        user_id: [authService.getIdToken()]
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
        user_id: [authService.getIdToken()]
      });

  }
  
  ngOnInit(): void {
     // this.getCatalogs();
      this.getDatasets();
      this.getDistributions();

      this.user_id =  this.authService.getIdToken();
  }

  saveDataset(){
    this.datasetForm.patchValue({id: uuid.v4()});
      this.datasetForm.patchValue({user_id: this.user_id});
      this.datasetForm.patchValue({project_id: this.project.id});
      console.log(this.datasetForm.value)
      this.metadataUploadService.submitDataset(this.datasetForm.value).subscribe(
        (data) => {
          this.getDatasets();
        },
        (error) => {
          console.error('Error saving form:', error);
        }
      )
  }

  /* saveCatalog(){
    this.catalogForm.patchValue({id: uuid.v4()});
    this.catalogForm.patchValue({user_id: this.user_id});
    this.catalogForm.patchValue({project_id: this.project.id});

    const catalog_json = {
      id: `http://localhost/${this.catalogForm.value.id}`,
      title: this.catalogForm.value.title,
      issued: new Date().toISOString(),
      modified: new Date().toISOString(),
      homepage: this.catalogForm.value.homePage || '',
      themeTaxonomy: this.catalogForm.value.themeTaxonomy || 'http://example.org/theme',
      isPartOf: "http://localhost/",
      publisher: {
          name: this.catalogForm.value.publisher,
          mbox: `mailto:${this.catalogForm.value.publisher_email}`
      },
      rights: this.catalogForm.value.rights || 'http://creativecommons.org/licenses/by/4.0/',
      license: this.catalogForm.value.license || 'http://example.org/license',
      language: 'http://id.loc.gov/vocabulary/iso639-1/en',
      version: this.catalogForm.value.version
    };

    console.log(catalog_json);
    this.metadataUploadService.submitCatalog(catalog_json).subscribe(
      (data) => {
        this.getCatalogs();
      },
      (error) => {
        console.error('Error saving form:', error);
      }
    )
  } */
  

 /*  saveForm(type:string) {
    if (type === 'dataset') {
      this.datasetForm.patchValue({id: uuid.v4()});
      this.datasetForm.patchValue({user_id: this.user_id});
      this.datasetForm.patchValue({project_id: this.project.id});
      console.log(this.datasetForm.value)
      this.metadataUploadService.submitForm(this.datasetForm.value, 'dataset').subscribe(
        (data) => {
          this.getDatasets();
        },
        (error) => {
          console.error('Error saving form:', error);
        }
      )
    } else if (type === 'distribution') {
      this.distributionForm.patchValue({id: uuid.v4()});
      this.distributionForm.patchValue({user_id: this.user_id});
      this.distributionForm.patchValue({project_id: this.project.id});
      console.log(this.distributionForm.value)
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
      this.savedCatalogs = JSON.parse(data)
      console.log(this.savedCatalogs)
    });
  }
 */
  getDatasets() {
    this.metadataUploadService.getDatasets().subscribe((data: any) => {
      console.log("loaded datasets:") 
      console.log(data)
      this.savedDatasets = JSON.parse(data)
    });
  }

  getDistributions() {
    this.metadataUploadService.getDistributions().subscribe((data: any) => {
      console.log("loaded distributions:") 
      console.log(data)
      this.savedDistributions  = JSON.parse(data)
    });
  }


  resetForm(){
    //this.catalogForm.reset();
    this.datasetForm.reset();
    this.distributionForm.reset();
  }


  goToNextPage(){
    this.projectService.updateProjectStatus(this.project.id, 'D-E').subscribe({
      next: () => { console.log('updated'); }
    });
  }

  isInvalid(controlName: string) {
    if(this.selectedType === DATASET) {
      const control = this.datasetForm.get(controlName);
      return control ? control.invalid && (control.dirty || control.touched) : false;

    }
    else if(this.selectedType === DISTRIBUTION) {
      const control = this.distributionForm.get(controlName);
      return control ? control.invalid && (control.dirty || control.touched) : false;
    }
    return false;
  }
}
  
