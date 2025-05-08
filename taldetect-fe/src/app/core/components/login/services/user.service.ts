import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';
import { catchError, map, Observable, tap, throwError } from 'rxjs';
import {
  LOGIN_API,
  RESET_USER_API,
  UPDATE_PSW_USER_API,
  REGISTER_USER_API,
  USER_INFO_API,
} from '../../../constants/api';
import { LocalStorageService } from '../../../services/local-storage.service';
import { AuthSupport } from '../../../utils/AuthSupport';
import { HttpSupport } from '../../../utils/HttpSupport';
import { Token, User } from '../../../utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private BASE_URL;

  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private authSupport: AuthSupport,
    private httpSupport: HttpSupport
  ) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  login(email: string, password: string): Observable<Token> {
    return this.http
      .post<Token>(
        `${this.BASE_URL}/${LOGIN_API}`,
        { email, password },
        { headers: { 'Content-Type': 'application/json' } }
      )
      .pipe(
        map((response: any) => {
          const token: Token = {
            jwt: response.access_token,
            auth: response.token_type,
          };
          return token;
        }),
        catchError(this.handleError)
      );
  }

  userInfo(): Observable<User> {
    let token = this.authSupport.getToken();
    let headers = this.httpSupport.buildHeaders(token);

    return this.http
      .post<User>(`${this.BASE_URL}/${USER_INFO_API}`, {}, { headers })
      .pipe(
        tap((response) => console.log('Risposta ricevuta:', response)),
        map((response) => {
          if (typeof response !== 'object') {
            throw new Error('Risposta non valida, forse HTML?');
          }
          return {
            email: response.email,
            name: response.name,
            surname: response.surname,
            role: response.role,
          };
        }),
        catchError((error) => {
          console.error('Errore API:', error);
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('token');
  }

  saveUser(user: any): void {
    sessionStorage.setItem('user', JSON.stringify(user));
  }

  resetUserPassword(email: string) {
    return this.http
      .get(`${this.BASE_URL}/${RESET_USER_API}/${email}`, {
        headers: { 'Content-Type': 'application/json' },
      })
      .pipe(
        map((response) => {
          return 'Password reset email sent successfully!';
        }),
        catchError((error) => {
          return throwError(
            () => new Error('Failed to reset password. Please try again.')
          );
        })
      );
  }

  updateUserPassword(email: string, newPassword: string) {
    return this.http
      .put<{ message: string }>(
        `${this.BASE_URL}/${UPDATE_PSW_USER_API}/${email}`,
        { newPassword },
        {
          headers: { 'Content-Type': 'application/json' },
        }
      )
      .pipe(
        map(() => 'Password Updated!'),
        catchError(() =>
          throwError(() => new Error('Failed to update password'))
        )
      );
  }

  registerUser(userData: any): Observable<any> {
    return this.http
      .post<any>(`${this.BASE_URL}/UPDATE_PSW_USER_API`, userData)
      .pipe(
        catchError((error) => {
          console.error('Errore durante la registrazione:', error);
          return throwError(
            () => new Error('Errore nella registrazione dell’utente')
          );
        })
      );
  }

  getUser(): User | null {
    if (typeof window !== 'undefined' && sessionStorage) {
      const user = sessionStorage.getItem('user');
      return user ? (JSON.parse(user) as User) : null;
    }
    return null;
  }

  isLoggedIn(): boolean {
    return sessionStorage.getItem('user') !== null;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Errore sconosciuto!';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Errore client: ${error.error.message}`;
    } else {
      errorMessage = `Errore server (${error.status}): ${
        error.error.message || error.message
      }`;
    }
    return throwError(() => new Error(errorMessage));
  }
}
