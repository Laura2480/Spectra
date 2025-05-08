import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { Patient } from '../../../utils/BeanSupport';
import { LocalStorageService } from '../../../services/local-storage.service';
import { GET_PATIENTS, PATCH_PATIENT, PUT_PATIENT } from '../../../constants/api';

@Injectable({
  providedIn: 'root',
})
export class PatientService {
  BASE_URL: any;
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  getAllPatients(): Observable<Patient[]> {
    return this.http
      .post<Patient[]>(`${this.BASE_URL}/${GET_PATIENTS}`, {})
      .pipe(catchError(this.handleError));
  }

  savePatient(patient: Patient): Observable<any> {
    return this.http
      .put(`${this.BASE_URL}/${PUT_PATIENT}`, patient)
      .pipe(catchError(this.handleError));
  }

  updatePatient(patient: Patient): Observable<any> {
    return this.http
      .put(`${this.BASE_URL}/${PATCH_PATIENT}`, patient)
      .pipe(catchError(this.handleError));
  }

  deletePatient(id: string): Observable<any> {
    return this.http
      .delete(`${this.BASE_URL}/patient/${id}`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Errore sconosciuto!';
    if (error.error && error.error.message) {
      errorMessage = `Errore: ${error.error.message}`;
    } else if (error.message) {
      errorMessage = `Errore: ${error.message}`;
    } else {
      errorMessage = `Errore status ${error.status}: ${error.statusText}`;
    }
    return throwError(() => new Error(errorMessage));
  }
  
}
