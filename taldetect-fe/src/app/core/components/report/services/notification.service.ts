import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GET_NOTIFICATION_API } from '../../../constants/api';
import { Observable } from 'rxjs/internal/Observable';
import { catchError, map, throwError } from 'rxjs';
import { LocalStorageService } from '../../../services/local-storage.service';
import { ReportUser } from '../../../utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class NotificationService {
  BASE_URL: any;
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  notification(): Observable<ReportUser[]> {
    return this.http
      .post<ReportUser | ReportUser[]>(
        `${this.BASE_URL}/${GET_NOTIFICATION_API}`,
        {},
        { headers: { 'Content-Type': 'application/json' } }
      )
      .pipe(
        map((response: ReportUser | ReportUser[]) => {
          if (!response) {
            throw new Error('Response is null or undefined');
          }

          const reports = Array.isArray(response) ? response : [response];

          return reports.map((report) => ({
            id: report.id,
            upload_id: report.upload_id,
            filename: report.filename,
            report: report.report.map((item) => ({
              tipologia: item.tipologia,
              punteggio: item.punteggio,
              giustificazione: item.giustificazione || '',
              pattern_rilevati: item.pattern_rilevati || [],
            })),
            status: report.status,
            score: report.score
          }));
        }),
        catchError(this.handleError)
      );
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