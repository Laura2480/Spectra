import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthSupport {
  getToken(): string {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token non valido o assente.');
      throw new Error('Token non valido');
    }
    return token;
  }
}
