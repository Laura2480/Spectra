import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ASSIGN_ROLES_API, DIARIZE_AUDIO_API, DIARIZE_AUDIO_GET_PROGRESS_API, GET_SPEAKER_EXCERPT_API, GET_SPEAKERS_API,  } from '../../../core/constants/api';
import { LocalStorageService } from '../../../core/services/local-storage.service';

@Injectable({
  providedIn: 'root'
})
export class DiarizationService {
  private BASE_URL = null;
  constructor(private http: HttpClient, private localStorageService: LocalStorageService) {
    this.BASE_URL = this.localStorageService.getItem('BASE_URL');
  }

  startDiarization(uploadId: string): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${DIARIZE_AUDIO_API}/${uploadId}`, {});
  }

  getDiarizationProgress(uploadId: string): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${DIARIZE_AUDIO_GET_PROGRESS_API}/${uploadId}`, {});
  }

  getDiarizationSpeakers(uploadId: string): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${GET_SPEAKERS_API}/${uploadId}`, {});
  }

  getSpeakerExcerpt(uploadId: string, speaker: string): Observable<Blob> {
    return this.http.post(`${this.BASE_URL}/${GET_SPEAKER_EXCERPT_API}/${uploadId}`, { speaker }, { responseType: 'blob' });
  }

  assignRoles(uploadId: string, roles: Record<string, string>): Observable<any> {
    return this.http.post(`${this.BASE_URL}/${ASSIGN_ROLES_API}/${uploadId}`, roles);
  }
  
}
