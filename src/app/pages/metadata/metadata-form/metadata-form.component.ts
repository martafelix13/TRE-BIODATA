import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import * as uuid from 'uuid';
import { MetadataUploadService } from '../../../services/metadata-upload.service';
import { AuthService } from '../../../services/auth.service';
import { ProjectsService } from '../../../services/projects.service';
import { ThemeDirective } from '@coreui/angular';


@Component({
  selector: 'app-metadata-form',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './metadata-form.component.html',
  styleUrls: ['./metadata-form.component.scss']
})
export class MetadataFormComponent implements OnInit {
  @Input() project: any;

  datasetForm: FormGroup;
  distributionForm: FormGroup;

  distributionsForms: FormGroup[] = [];

  datasetData: any = {};
  distributionsData: any[] = [];

  user_id = '';

  selectedType = 'dataset';
  formOptions = [
    { label: 'Dataset', value: 'dataset' },
    { label: 'Distribution', value: 'distribution' }
  ];

  constructor(
    private fb: FormBuilder,
    private metadataUploadService: MetadataUploadService,
    private authService: AuthService,
    private projectService: ProjectsService
  ) {
// Initialize dataset form with sample values
this.datasetForm = this.fb.group({
  title: ['STROKE Patient Dataset', Validators.required],
  theme: ['http://example.org/themes/neurology', Validators.required],
  publisher: ['National Health Data Platform (NHDP)', Validators.required],
  version: ['1.0', Validators.required],
  release_date: ['2024-01-01', Validators.required],
  update_date: ['2025-01-01', Validators.required],
  license: ['https://creativecommons.org/licenses/by/4.0/', Validators.required],
  description: [
    'A curated dataset containing anonymized stroke patient data, including clinical, imaging, and outcome variables. Designed for predictive modeling and public health research.',
    Validators.required
  ],
  no_unique_individuals: [1200, Validators.required],
  no_records: [1500, Validators.required],
  population_coverage: ['90%', Validators.required],
  min_typical_age: [45, Validators.required],
  max_typical_age: [85, Validators.required],
  keyword: ['stroke, neurology, dataset', Validators.required],
  contact_point: ['https://contact@nhdp.org', Validators.required] // TODO: add validator in form
});

// Initialize distribution form with sample values
this.distributionForm = this.fb.group({
  title: ['STROKE Data (CSV)', Validators.required],
  publisher: ['National Health Data Platform (NHDP)', Validators.required],
  media_type: ['cvs/text', Validators.required],
  has_version: ['1.0', Validators.required],
  access_url: ['https://data.nhdp.org/stroke/1.0/data.csv', Validators.required],
  description: [
    'Downloadable CSV file containing structured STROKE patient data, including diagnosis, treatment, and outcomes.',
    Validators.required
  ]
});
  }

  ngOnInit(): void {
    this.user_id = this.authService.getIdToken();
  }
  

  // Save dataset data
  saveDataset(): void {
    this.datasetData = {
      contact_point: [this.datasetForm.value.contact_point],
      creator: [{ name: ['BioData.pt'], identifier: 'https://ror.org/02q7abn51' }],
      description: [{ value: this.datasetForm.value.description }],
      distribution: ['http://localhost:8667/tre/distribution'],
      release_date: this.datasetForm.value.release_date,
      keyword: [{ value: this.datasetForm.value.keyword }],
      identifier: [uuid.v4()],
      update_date: this.datasetForm.value.update_date,
      publisher: [{ name: [this.datasetForm.value.publisher], identifier: 'https://ror.org/02q7abn51' }],
      theme: [this.datasetForm.value.theme],
      title: [{ value: this.datasetForm.value.title }],
      license: this.datasetForm.value.license,
      no_unique_individuals: this.datasetForm.value.no_unique_individuals,
      no_records: this.datasetForm.value.no_records,
      population_coverage: [this.datasetForm.value.population_coverage],
      min_typical_age: this.datasetForm.value.min_typical_age,
      max_typical_age: this.datasetForm.value.max_typical_age,
      has_version: this.datasetForm.value.version, 
    };
    console.log('Dataset Data:', this.datasetData);
  }

  transformDistributionData(distribution: any): any {
    const distributionsData = {
      title: [distribution.title],
      publisher: [{ name: [distribution.publisher], identifier: 'https://ror.org/02q7abn51' }],
      description: [{ value: distribution.description }],
      access_url: [distribution.access_url],
      media_type: distribution.media_type,
      has_version: distribution.version,
      // "identifier": ["GDIF-12345678-90ab-defg"]
    };

  return distributionsData;
}

  addDistribution(): void {
    const form = this.fb.group(this.distributionForm.value); 
    form.addControl('collapsed', this.fb.control(false));
    this.distributionsForms.push(form);
  }
  
  saveDistribution(index: number): void {
    const dist = this.distributionsForms[index];
    if (dist.valid) {
      dist.get('collapsed')?.setValue(true);
    } else {
      dist.markAllAsTouched();  // Show validation errors
    }
  }
  
  editDistribution(index: number): void {
    this.distributionsForms[index].get('collapsed')?.setValue(false);
  }
  
  submitMetadata(): void{

    this.saveDataset();

    console.log('Submitting metadata...');
    // remove collapsed property from each distribution
    this.distributionsForms.forEach((dist) => {
      dist.removeControl('collapsed');
      this.distributionsData.push(this.transformDistributionData(dist.value));
    });
    console.log('Dataset Data:', this.datasetData);
    console.log('Distributions Data:', this.distributionsData);
    this.metadataUploadService.uploadMetadata(this.datasetData, this.distributionsData).subscribe(
      (response) => {
        console.log('Metadata submitted successfully:', response);
      },
      (error) => {
        console.error('Error submitting metadata:', error);
      }
    );
  }

  removeDistribution(index: number): void {
    this.distributionsData.splice(index, 1);
  }


  resetForm(): void {
    this.datasetForm.reset();
    this.distributionForm.reset();
    this.distributionsData = [];
    this.datasetData = {};
  }

  goToNextPage(){
    this.projectService.updateProjectStatus(this.project.id, 'D-E').subscribe({
      next: () => { console.log('updated'); }
    });
  }

  isInvalid(form: FormGroup, controlName: string) {
      const control = form.get(controlName);
      return control ? control.invalid && (control.dirty || control.touched) : false;
  }
}

