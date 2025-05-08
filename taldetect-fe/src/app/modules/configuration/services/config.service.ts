import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ADD_CONFIGURATION_API } from '../../../core/constants/api';
import { LocalStorageService } from '../../../core/services/local-storage.service';
import { ConfigPayload } from '../../../core/utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class ConfigService {
  private backendUrl = ADD_CONFIGURATION_API;

  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {
    this.backendUrl = `${this.localStorageService.getItem(
      'BASE_URL'
    )}/${ADD_CONFIGURATION_API}`;
  }

  configure(payload: ConfigPayload): Observable<any> {
    return this.http.post<any>(this.backendUrl, payload);
  }
}
