import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { CodeDisplayComponent } from '../../components/code-display/code-display.component';
import { MatDividerModule } from '@angular/material/divider';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RemsService } from '../../services/rems.service';

@Component({
  selector: 'app-data-upload',
  imports: [MatCardModule, MatIconModule, CodeDisplayComponent, MatDividerModule, CommonModule, MatFormFieldModule, ReactiveFormsModule, FormsModule],
  templateUrl: './data-upload.component.html',
  styleUrl: './data-upload.component.scss'
})
export class DataUploadComponent {
  @Input() withREMS: boolean = false;

  resource_id : string = '';
  validation_message : string = '';

  constructor(private remsService : RemsService) { }

  ngOnInit() {
    console.log('Data Upload Component initialized.');
    console.log('Embedded: ', this.withREMS);
  }


  createResource(){
    if (!this.resource_id) {
      this.validation_message = "Resource Name is required.";
    } else {
      if (!this.validation_message) {
        this.remsService.createResource(this.resource_id).subscribe((res) => {
          console.log('Resource created: ', res);
        });
      }
    }
  }

  validateResourceName() {

    console.log('Validating resource name...', this.resource_id);
    const validPattern = /^[a-zA-Z0-9_]+$/;

    if (!this.resource_id) {
      this.validation_message = "Resource Name is required.";
    } else if (!validPattern.test(this.resource_id)) {
      this.validation_message =
        "Invalid format. Only letters, numbers, and underscores (_) are allowed.";
    } else {
      this.validation_message = "";
    }
  }

  


}
