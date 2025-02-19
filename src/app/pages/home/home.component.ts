import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {

  userData: any = {};

  constructor( private route: ActivatedRoute,private router: Router, private authService: AuthService) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const { name, email} = params;

      if (name || email) {
        this.userData = { name, email };
        this.authService.setUserData(this.userData);  
        this.router.navigate(['/'], { replaceUrl: true });
      }
    });

    this.userData = this.authService.getUserData();
    console.log('User Data:', this.userData);
  }

  goToPage(pageRef : string){
    console.log("Go to page: " + pageRef);
    this.router.navigate([pageRef]);
  }
  
}
