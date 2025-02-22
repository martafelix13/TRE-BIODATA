import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-header',
  imports: [CommonModule, RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {

  title = 'Trusted Research Environment';
  userData: any;

  constructor( private authService: AuthService ) {
    this.authService.user$.subscribe(user => {
      this.userData = user;
    });
  }

  login(){
    this.authService.login();
  }

  logout(){
    this.authService.logout();
  }

  isLogged(): boolean {
    return this.authService.isLogged();
  }


}
