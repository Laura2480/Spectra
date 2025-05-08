import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  Validators,
  ReactiveFormsModule,
} from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { UserService } from './services/user.service';
import { Router, RouterModule } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';
import { switchMap } from 'rxjs/internal/operators/switchMap';
import { Token, User } from '../../utils/BeanSupport';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    TranslateModule,
    ReactiveFormsModule,
    RouterModule,
    TranslateModule,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  emailRegex: string = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$';
  email: string = '';
  password: string = '';
  loginForm: FormGroup;
  labelMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private router: Router,
    private toastr: ToastrService,
    private translate: TranslateService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
    });

    this.translate.get(['login.message']).subscribe((translations) => {
      this.labelMessage = translations['login.message'];
    });
  }

  onLogin() {
    if (this.loginForm.invalid) {
      this.toastr.warning('Compila correttamente il form.');
      return;
    }

    const { email, password } = this.loginForm.value;

    this.userService
      .login(email, password)
      .pipe(
        switchMap((token: Token) => {
          console.log('Token:', token);
          if (token?.jwt) {
            localStorage.setItem('token', token.jwt);
          } else {
            throw new Error('Token not valid');
          }
          return this.userService.userInfo();
        })
      )
      .subscribe({
        next: (user: User) => {
          console.log('Utente autenticato:', user);
          this.userService.saveUser(user);
          this.toastr.success(`${this.labelMessage}, ${user.name}!`);
          this.router.navigate(['/']);
        },
        error: (error: HttpErrorResponse) => {
          console.error('Errore HTTP:', error);
          localStorage.removeItem('token');
          this.verifyLoginError(error);
        },
      });
  }

  onReset() {
    if (this.loginForm.get('email')?.valid) {
      const email = this.loginForm.get('email');
      this.userService.resetUserPassword(email.value).subscribe({
        next: (message: string) => {
          this.toastr.info(message);
        },
        error: (err: Error) => {
          this.toastr.error(err.message);
        },
      });
    } else {
      console.log('Email non inserita');
      this.toastr.error('Email non inserita');
    }
  }

  onRegister() {
    this.router.navigate(['/create-user']);
  }

  private verifyLoginError(error: HttpErrorResponse) {
    if (error.status === 401) {
      this.toastr.error('Credenziali non valide.');
    } else if (error.status === 404) {
      this.toastr.error('Utente non registrato.');
    } else if (error.status === 500) {
      this.toastr.error('Errore del server. Riprova più tardi.');
    } else {
      this.toastr.error('Errore sconosciuto. Controlla la console.');
    }
  }
}
