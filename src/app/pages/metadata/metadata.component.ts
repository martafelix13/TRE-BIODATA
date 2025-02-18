import { Component } from '@angular/core';
import { MetadataFormComponent } from '../../metadata-form/metadata-form.component';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-metadata',
  imports: [MetadataFormComponent, CommonModule],
  templateUrl: './metadata.component.html',
  styleUrl: './metadata.component.scss'
})
export class MetadataComponent {

  isAuthenticated = false;

  constructor(private router : Router) {}

  ngOnInit() {
    this.isAuthenticated = false;
  }

  onToggleFakeLogin() {
    console.log("isAuthenticated: " + this.isAuthenticated);
    this.isAuthenticated = !this.isAuthenticated;
  }

}
