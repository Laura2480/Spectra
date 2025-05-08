import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GET_PAGINATED_JOBS, START_JOB_API } from '../../../core/constants/api';
import { LocalStorageService } from '../../../core/services/local-storage.service';
import { ConfigPayload } from '../../../core/utils/BeanSupport';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private BASE_URL:String = null;

  constructor(private http: HttpClient, private localStorageService: LocalStorageService) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  startJob(upload_id: string, payload: ConfigPayload): Observable<any> {
    return this.http.post<any>(`${this.BASE_URL}/${START_JOB_API}/${upload_id}`, payload);
  }

  getJobs(page: number, perPage: number): Observable<any> {
    if (this.BASE_URL != '' && !this.BASE_URL.includes('lsNotAvailable')) {
      return this.http.post<any>(`${this.BASE_URL}/${GET_PAGINATED_JOBS}?page=${page}&per_page=${perPage}`, {});
    }
    return null;
  }

  getJobDetail(upload_id: string): Observable<any> {
    if (this.BASE_URL != '' && !this.BASE_URL.includes('lsNotAvailable')) {
      return this.http.post<any>(`${this.BASE_URL}/${GET_PAGINATED_JOBS}/${upload_id}`, {});
    }
    return null;
  }
}
