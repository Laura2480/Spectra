import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GET_ALL_REG_API, GET_FEATURES_BY_FILENAME, GET_FEATURES_CHART_API } from '../../../core/constants/api';
import { LocalStorageService } from '../../../core/services/local-storage.service';

@Injectable({
  providedIn: 'root'
})
export class FeaturesService {
  private BASE_URL = null;
  constructor(private http: HttpClient, private localStorageService: LocalStorageService) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL');
  }

  getFeaturesChardData(): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${GET_FEATURES_CHART_API}`, {});
  }

  getAllReg(): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${GET_ALL_REG_API}`, {});
  }

  getFeaturesByFilename(fileName:String): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${GET_FEATURES_BY_FILENAME}/${fileName}`, {});
  }

  
}
