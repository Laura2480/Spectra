import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/internal/Observable';
import { LocalStorageService } from '../../../core/services/local-storage.service';
import { GENERATE_REPORT_API } from '../../../core/constants/api';

@Injectable({
    providedIn: 'root',
})
export class StepperReportService {
    BASE_URL: any;
    constructor(
        private http: HttpClient,
        private localStorageService: LocalStorageService
    ) {
        this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
    }

    startGenerateReport(upload_id: string): Observable<any> {
        return this.http.post<any>(`${this.BASE_URL}/${GENERATE_REPORT_API}/${upload_id}`, {});
    }
}
