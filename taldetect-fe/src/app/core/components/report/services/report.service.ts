import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  GET_PATIENT_API,
  GET_REPORT_API,
  GET_REPORTS_API,
  GET_REPORTS_DETECTED_COUNT_API,
  UPDATE_REPORT_API,
  GET_DOWNLOAD_SCORE_REPORT_PATIENT,
  GET_DOWNLOAD_COMPLETED_REPORT_PATIENT,
} from '../../../constants/api';
import { Observable } from 'rxjs/internal/Observable';
import { catchError, map, throwError } from 'rxjs';
import { LocalStorageService } from '../../../services/local-storage.service';
import { Patient, ReportItem, ReportUser } from '../../../utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class ReportService {
  BASE_URL: any;
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  reportById(upload_id: string): Observable<ReportUser> {
    return this.http
      .post<ReportUser>(
        `${this.BASE_URL}/${GET_REPORT_API}/${upload_id}`,
        {},
        { headers: { 'Content-Type': 'application/json' } }
      )
      .pipe(
        map((response: any) => {
          if (!response) {
            throw new Error('Response is null or undefined');
          }

          let reportItems: ReportItem[] = [];
          try {
            reportItems =
              typeof response.report === 'string'
                ? JSON.parse(response.report)
                : response.report;
            console.log('report from db', reportItems);
          } catch (error) {
            throw new Error('Error parsing report data');
          }

          const parsedReportItems: ReportItem[] = reportItems.map(
            (item: any) => {
              return {
                tipologia: item.tipologia,
                punteggio: item.punteggio,
                giustificazione: item.giustificazione || '',
                pattern_rilevati: item.pattern_rilevati || [],
              };
            }
          );

          const reportUser: ReportUser = {
            id: response.id,
            upload_id: response.upload_id,
            filename: response.filename,
            report: parsedReportItems,
            status: response.status,
            score: response.score,
          };

          return reportUser;
        }),
        catchError(this.handleError)
      );
  }

  updateReport(currentReport: ReportUser) {
    return this.http
      .put<any>(
        `${this.BASE_URL}/${UPDATE_REPORT_API}`,
        {
          id: currentReport.id,
          upload_id: currentReport.upload_id,
          report: currentReport.report,
          filename: currentReport.filename,
          status: currentReport.status,
          score: currentReport.score,
        },
        { headers: { 'Content-Type': 'application/json' } }
      )
      .pipe(
        map((response) => {
          if (!response) {
            throw new Error('La risposta del server è nulla o non definita.');
          }
          return response;
        }),
        catchError((error) => {
          console.error('Errore durante l’aggiornamento del report:', error);
          return throwError(
            () => new Error('Errore durante l’aggiornamento del report.')
          );
        })
      );
  }

  patientById(upload_id: string): Observable<Patient> {
    return this.http
      .post<Patient>(
        `${this.BASE_URL}/${GET_PATIENT_API}/${upload_id}`,
        {},
        { headers: { 'Content-Type': 'application/json' } }
      )
      .pipe(
        map((response: any) => {
          if (!response) {
            throw new Error('Response is null or undefined');
          }
          console.log('risposta paziente', response);
          const patient: Patient = {
            id: response.id,
            name: response.name,
            surname: response.surname,
            email: response.email,
            age: response.age,
          };

          return patient;
        }),
        catchError(this.handleError)
      );
  }

  getReportDetectedCount(): Observable<any> {
    return this.http
      .post<any>(`${this.BASE_URL}${GET_REPORTS_DETECTED_COUNT_API}`, {})
      .pipe(
        map((response) => {
          if (!response) {
            throw new Error('Response is null or undefined');
          }
          return response;
        }),
        catchError(this.handleError)
      );
  }

  getLatestsReports(): Observable<ReportUser[]> {
    return this.http
      .post<ReportUser | ReportUser[]>(
        `${this.BASE_URL}/${GET_REPORTS_API}`,
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
            score: report.score,
          }));
        }),
        catchError(this.handleError)
      );
  }

  getReportScorePatient(upload_id: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post(
      `${this.BASE_URL}/${GET_DOWNLOAD_SCORE_REPORT_PATIENT}/${upload_id}`,
      {},
      {
        headers,
        responseType: 'blob',
      }
    );
  }
  getReportCompletedPatient(upload_id: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post(
      `${this.BASE_URL}/${GET_DOWNLOAD_COMPLETED_REPORT_PATIENT}/${upload_id}`,
      {},
      {
        headers,
        responseType: 'blob',
      }
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
