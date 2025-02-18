import { CommonModule } from '@angular/common';
import { Component, HostListener } from '@angular/core';
import {Router, RouterModule, RouterOutlet} from '@angular/router';
import {MatSidenavModule} from '@angular/material/sidenav';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterModule, MatSidenavModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'Trusted Research Environment';
  isMenuOpen = false;

  constructor(private router: Router, private authService: AuthService) {
    this.router.events.subscribe(() => {
      this.isMenuOpen = false;
    });
  }

  menuLinks = [
    { label: 'Home', path: '/' },
    { label: 'Metadata Information', path: '/metadata-details' },
  ];

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  closeMenu() {
    this.isMenuOpen = false;
  }

  @HostListener('document:click', ['$event'])
  handleClickOutside(event: Event) {
    const menuElement = document.querySelector('.menu-container');
    if (menuElement && !menuElement.contains(event.target as Node)) {
      this.isMenuOpen = false;
    }
  }

  login(){
    this.authService.login();
  }
}


