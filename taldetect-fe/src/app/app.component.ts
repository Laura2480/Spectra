import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from "./core/components/navbar/navbar.component";
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { FooterComponent } from './core/components/footer/footer.component';
import { EndpointService } from './core/services/endpoint.service';
import { LoaderComponent } from "./core/components/loader/loader.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, HttpClientModule, TranslateModule, FooterComponent, LoaderComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'asdetect-fe';

  constructor(
    private translate: TranslateService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private endpointService: EndpointService,
    private http: HttpClient
  ) {
    translate.addLangs(['en', 'it']);
    if (isPlatformBrowser(this.platformId)) {
      const savedLang = localStorage.getItem('lang');
      translate.setDefaultLang(savedLang ? savedLang : 'en');
    } else {
      translate.setDefaultLang('en');
    }
  }

  ngOnInit(): void {
    const testBaseUrl = this.endpointService.getBaseUrl();
    if (testBaseUrl != null && !testBaseUrl.includes('lsNotAvailable')) {
      this.http.head(testBaseUrl + "/docs", { observe: 'response' }).subscribe({
        next: (response) => {
          console.log(
            response.status >= 200 && response.status < 400
              ? 'BASE_URL raggiungibile:' + testBaseUrl
              : 'BASE_URL non raggiungibile, recupero nuovo BASE_URL...'
          );

          if (response.status < 200 || response.status >= 400) {
            this.fetchAndStoreBaseUrl();
          }
        },
        error: () => this.fetchAndStoreBaseUrl()
      });
    } 
    if(testBaseUrl == null){
      this.fetchAndStoreBaseUrl();
    }
  }

  fetchAndStoreBaseUrl() {
    this.endpointService.fetchAndStoreBaseUrl().subscribe({
      next: () => {
        console.log('BASE_URL recuperato e memorizzato con successo.');
      },
      error: (error) => {
        console.error('Errore nel recupero del BASE_URL:', error);
      }
    });
  }

  switchLanguage(event: any) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('lang', event);
    }
    this.translate.use(event);
  }
}
