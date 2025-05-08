import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { LocalStorageService } from './local-storage.service';

@Injectable({
  providedIn: 'root',
})
export class EndpointService {
  private readonly storageKey = 'BASE_URL';
  private readonly endpointUrl = 'https://get-endpoint-fsiqd7bf7a-uc.a.run.app/?type=data_preprocessing';

  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {}

  fetchAndStoreBaseUrl(): Observable<{ endpoint_url: string }> {
    return this.http.get<{ endpoint_url: string }>(this.endpointUrl).pipe(
      tap(response => {
        const baseUrl = response.endpoint_url;
        this.localStorageService.setItem(this.storageKey, baseUrl);
      })
    );
  }

  getBaseUrl(): string | null {
    return this.localStorageService.getItem(this.storageKey);
  }
}
