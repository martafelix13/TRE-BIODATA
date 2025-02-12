import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';
import { Router } from '@angular/router';

@Component({
  selector: 'app-side-menu',
  templateUrl: './side-menu.component.html',
  imports: [CommonModule, MatSidenavModule],
  styleUrls: ['./side-menu.component.css']
})
export class SideMenuComponent {
  constructor(private router: Router) {}

  menuLinks = [
    { label: 'Home', path: '/' },
    { label: 'Metadata Information', path: '/metadata-details' },
  ];

  navigateTo(path: string) {
    this.router.navigate([path]);
  }
}
