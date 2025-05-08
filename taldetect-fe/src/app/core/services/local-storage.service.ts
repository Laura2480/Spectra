import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class LocalStorageService {
  private isBrowser: boolean;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  setItem(key: string, value: string): void {
    if (this.isBrowser && localStorage) {
      localStorage.setItem(key, value);
    } 
  }

  getItem(key: string): string | null {
    if (this.isBrowser && localStorage) {
      return localStorage.getItem(key);
    } else {
      return "lsNotAvailable";
    }
  }

  removeItem(key: string): void {
    if (this.isBrowser && localStorage) {
      localStorage.removeItem(key);
    }
  }
}
