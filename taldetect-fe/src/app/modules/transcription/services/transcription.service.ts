import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, interval, BehaviorSubject, map } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import {
  DOWNLOAD_TRANSCRIPTION_API,
  DOWNLOAD_TRANSCRIPTION_PDF_API,
  DOWNLOAD_TRANSCRIPTION_TEXT_API,
  DOWNLOAD_VERBOSE_TRANSCRIPTION_API,
  GET_PAGINATED_TRANSCRIPTIONS,
  GET_TRANSCRIBE_PROGRESS_API,
  GET_TRANSCRIBE_RESULT_API,
  GET_TRANSCRIPTION_DETAIL,
  SAVE_TRANSCRIPTION_API,
  TRANSCRIBE_API,
  UPDATE_TRANSCRIPTION,
} from '../../../core/constants/api';
import { TRANSCRIPTION_PROGRESS_INTERVAL_MS } from '../../../core/constants/interval';
import { LocalStorageService } from '../../../core/services/local-storage.service';
import { TranscriptionUpdatePayload } from '../../../core/utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class TranscriptionService {
  private transcriptionProgress = new BehaviorSubject<number>(0);
  private BASE_URL = null;

  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL') || '';
  }

  transcribeAudio(uploadId: string): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${TRANSCRIBE_API}/${uploadId}`, {});
  }

  getTranscriptionProgress(uploadId: string): Observable<number> {
    return interval(TRANSCRIPTION_PROGRESS_INTERVAL_MS).pipe(
      switchMap(() =>
        this.http.post<{ progress: number }>(
          `${this.BASE_URL}/${GET_TRANSCRIBE_PROGRESS_API}/${uploadId}`,
          {}
        )
      ),
      map((response) => response.progress),
      takeWhile((progress) => progress < 100, true)
    );
  }

  getSingleTranscriptionProgress(uploadId: string): Observable<number> {
    return this.http
      .post<{ progress: number }>(
        `${this.BASE_URL}/${GET_TRANSCRIBE_PROGRESS_API}/${uploadId}`,
        {}
      )
      .pipe(map((response) => response.progress));
  }

  getTranscriptionProgressObservable(): Observable<number> {
    return this.transcriptionProgress.asObservable();
  }

  getTranscriptionResult(uploadId: string): Observable<{ transcription: any }> {
    return this.http.post<{ transcription: any }>(
      `${this.BASE_URL}/${GET_TRANSCRIBE_RESULT_API}/${uploadId}`,
      {}
    );
  }

  saveCorrectedTranscription(
    uploadId: string,
    correctedTranscription: string
  ): Observable<{ message: string; upload_id: string }> {
    return this.http.post<{ message: string; upload_id: string }>(
      `${this.BASE_URL}/${SAVE_TRANSCRIPTION_API}/${uploadId}`,
      { transcription: correctedTranscription }
    );
  }

  getTranscriptions(page: number, perPage: number): Observable<any> {
    if (this.BASE_URL != '' && !this.BASE_URL.includes('lsNotAvailable')) {
      return this.http.post<any>(
        `${this.BASE_URL}/${GET_PAGINATED_TRANSCRIPTIONS}?page=${page}&per_page=${perPage}`,
        {}
      );
    }
    return null;
  }

  getTranscriptionDetail(uploadId: string): Observable<any> {
    return this.http.post<any>(
      `${this.BASE_URL}/${GET_TRANSCRIPTION_DETAIL}/${uploadId}`,
      {}
    );
  }

  updateTranscription(
    uploadId: string,
    payload: TranscriptionUpdatePayload
  ): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const url = `${this.BASE_URL}/${UPDATE_TRANSCRIPTION}/${uploadId}`;
    return this.http.put(url, { transcription: payload }, { headers });
  }

  downloadVerboseTranscription(uploadId: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    return this.http.post(
      `${this.BASE_URL}/${GET_PAGINATED_TRANSCRIPTIONS}/${uploadId}/${DOWNLOAD_VERBOSE_TRANSCRIPTION_API}`,
      {},
      { headers, responseType: 'blob' }
    );
  }

  downloadTranscriptionJson(uploadId: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    return this.http.post(
      `${this.BASE_URL}/${GET_PAGINATED_TRANSCRIPTIONS}/${uploadId}/${DOWNLOAD_TRANSCRIPTION_API}`,
      {},
      { headers, responseType: 'blob' }
    );
  }

  downloadTranscriptionTxt(uploadId: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    return this.http.post(
      `${this.BASE_URL}/${GET_PAGINATED_TRANSCRIPTIONS}/${uploadId}/${DOWNLOAD_TRANSCRIPTION_TEXT_API}`,
      {},
      { headers, responseType: 'blob' }
    );
  }
  downloadTranscriptionPdf(uploadId: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    return this.http.post(
      `${this.BASE_URL}/${GET_PAGINATED_TRANSCRIPTIONS}/${uploadId}/${DOWNLOAD_TRANSCRIPTION_PDF_API}`,
      {},
      { headers, responseType: 'blob' }
    );
  }
}
