import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';
import { DropdownComponent, 
  DropdownItemDirective, 
  DropdownMenuDirective, 
  DropdownToggleDirective
} from '@coreui/angular'

@Component({
  selector: 'app-header',
  imports: [CommonModule, RouterLink, DropdownComponent, DropdownItemDirective, DropdownMenuDirective, DropdownToggleDirective],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})

export class HeaderComponent {

  title = 'Trusted Research Environment';
  userData: any;

  constructor( private authService: AuthService) {
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
