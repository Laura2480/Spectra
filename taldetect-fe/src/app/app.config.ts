import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideClientHydration } from '@angular/platform-browser';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { HttpClient, HttpClientModule, provideHttpClient, withInterceptors } from '@angular/common/http';
import { TranslateLoader, TranslateModule, TranslateService } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { CustomPaginatorIntl } from './core/utils/paginator-intl';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { loaderInterceptor } from './core/interceptors/loader.interceptor';
import { provideToastr } from 'ngx-toastr';

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}
export function getPaginatorIntl(translate: TranslateService) {
  return new CustomPaginatorIntl(translate);
}

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), provideClientHydration(), provideAnimationsAsync(), provideHttpClient(), importProvidersFrom(
    HttpClientModule,
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      },
      useDefaultLang: true,
      defaultLanguage: 'it'
    }),
  ),
  provideHttpClient(withInterceptors([loaderInterceptor])),
  provideToastr(),
  importProvidersFrom(MatProgressSpinnerModule),
  { provide: MatPaginatorIntl, useFactory: getPaginatorIntl, deps: [TranslateService] }

  ]
};
