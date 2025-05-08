import { Component, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { NavigationEnd, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { UserService } from '../login/services/user.service';
import { filter, Subscription } from 'rxjs';
import { MatMenuModule } from '@angular/material/menu';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    RouterModule,
    TranslateModule,
    MatMenuModule
  ],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit, OnDestroy {
  userSession: any = null;
  private routerSubscription: Subscription | null = null;


  constructor(public userService: UserService, public router: Router) {}

  @Output() switchLanguage: EventEmitter<string> = new EventEmitter<string>();

  sendSwitchLanguage(lang: string) {
    this.switchLanguage.emit(lang);
  }

  ngOnInit() {
    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.userSession = this.userService.getUser();
      });
  }

  ngOnDestroy() {
    this.routerSubscription?.unsubscribe();
  }

  logout() {
    this.userService.logout();
    this.userSession = null;
    this.router.navigate(['/login']);
  }
  
  redirectToLogin(){
    this.router.navigate(['/login'])
  }
}
