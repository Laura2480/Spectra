import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { LocalStorageService } from '../../../core/services/local-storage.service';

@Injectable({
    providedIn: 'root'
})
export class FileService {
    private uploadUrl: string;

    constructor(private http: HttpClient, private localStorageService: LocalStorageService) {
        const baseUrl = this.localStorageService.getItem("BASE_URL");
        this.uploadUrl = `${baseUrl}/upload`;
    }

    uploadFile(file: File, clinicianId: string, patientId: string): Observable<number | any> {
        const formData: FormData = new FormData();
        formData.append("file", file);
        formData.append("clinician_id", clinicianId);
        formData.append("patient_id", patientId);

        return this.http.post(this.uploadUrl, formData, {
            reportProgress: true,
            observe: 'events'
        }).pipe(
            map((event: HttpEvent<any>) => {
                if (event.type === HttpEventType.UploadProgress) {
                    return Math.round(100 * event.loaded / (event.total || 1));
                }
                if (event.type === HttpEventType.Response) {
                    return event.body;
                }
                return null;
            }),
            catchError((error: HttpErrorResponse) => {
                console.error("Errore durante l'upload:", error);
                return throwError(error);
            })
        );
    }
}
