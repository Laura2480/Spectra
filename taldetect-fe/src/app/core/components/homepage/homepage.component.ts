import { CommonModule, isPlatformBrowser } from '@angular/common';
import {
  Component,
  OnInit,
  AfterViewInit,
  ViewChild,
  ChangeDetectorRef,
  Inject,
  PLATFORM_ID,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { GoogleChartsModule } from 'angular-google-charts';
import { ChartType } from 'angular-google-charts';
import { MatGridListModule } from '@angular/material/grid-list';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { TranscriptionService } from '../../../modules/transcription/services/transcription.service';
import { Router } from '@angular/router';
import { JobService } from '../../../modules/job/services/job.service';
import { NotificationService } from '../report/services/notification.service';
import { MatIcon } from '@angular/material/icon';
import { FeaturesService } from '../../../modules/features/services/features.service';
import { Observable, tap } from 'rxjs';
import {
  ChartsData,
  DataItem,
  Features,
  Job,
  ReportUser,
  Transcription,
} from '../../utils/BeanSupport';
import { ReportService } from '../report/services/report.service';

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    GoogleChartsModule,
    MatGridListModule,
    TranslateModule,
    MatIcon,
  ],
  styleUrls: ['./homepage.component.scss'],
})
export class HomepageComponent implements OnInit, AfterViewInit {
  isBrowser = false;
  displayedColumns: string[] = ['registrationName', 'actions'];
  displayedColumnsTranscriptions: string[] = ['filename', 'actions'];
  displayedColumnsJobs: string[] = ['filename', 'status', 'actions'];
  reports: any[] = [];
  reportsUser: any[] = [];
  transcriptions: Transcription[] = [];
  jobs: any[] = [];
  dataSource = new MatTableDataSource<Report>(this.reports);
  dataSourceReport = new MatTableDataSource<ReportUser>(this.reportsUser);
  transcriptionDataSource = new MatTableDataSource<Transcription>(
    this.transcriptions
  );
  jobDataSource = new MatTableDataSource<Transcription>(this.jobs);
  @ViewChild('reportPaginator') reportPaginator!: MatPaginator;
  @ViewChild('transactionPaginator') transactionPaginator!: MatPaginator;
  @ViewChild('jobPaginator') jobPaginator!: MatPaginator;
  type = ChartType;
  riscontriChart: any = {};
  featureChart: any = {};
  transcriptionPage: number = 1;
  transcriptionPerPage: number = 5;
  totalCount: number = 0;
  jobPage: number = 1;
  jobPerPage: number = 5;
  jobTotalCount: number = 0;
  chartsData: ChartsData = null;
  reportsDetectedCounts: any = null;
  featureScale: { [feature: string]: { min: number; max: number } } = {
    MFCC: { min: -15, max: 15 },
    Spectral_Centroid: { min: 800, max: 3000 },
    Spectral_Bandwidth: { min: 1000, max: 4000 },
    Spectral_Contrast: { min: 0, max: 40 },
    Spectral_Flatness: { min: 0, max: 1 },
    Spectral_Rolloff: { min: 1500, max: 3500 },
    Zero_Crossing_Rate: { min: 0, max: 0.2 },
    Chroma_STFT: { min: 0, max: 1 },
    RMS_Energy: { min: 0, max: 1 },
    Tempo: { min: 60, max: 180 },
    Speech_Rate: { min: 0, max: 1 },
    Pause_Duration: { min: 0.5, max: 3 },
    Turn_Taking_Coordination: { min: 0, max: 1 },
    HNR: { min: -80, max: 0 },
    Prosody_Variation: { min: 0, max: 200 },
    Speech_Intonation: { min: 0, max: 150 },
    Stress_Voice: { min: 0, max: 150 },
    Energy_Modulation: { min: 0, max: 0.01 },
    Latency_Intra_Turn: { min: -0.01, max: 0.01 },
    Turn_Response_Time: { min: 1, max: 3 },
    Fluency_Disfluency: { min: 0, max: 1 },
    Sentence_Length_Avg: { min: 0, max: 10 },
    Syntactic_Complexity: { min: 0, max: 6000 },
    Predictability_Entropy: { min: 0, max: 3000 },
    Functional_Word_Frequency: { min: 0, max: 1 },
    Total_Speech_Duration: { min: 0, max: 180 },
  };

  constructor(
    private cdr: ChangeDetectorRef,
    @Inject(PLATFORM_ID) private platformId: any,
    private translate: TranslateService,
    private transcriptionService: TranscriptionService,
    private jobService: JobService,
    private notificationService: NotificationService,
    private featuresService: FeaturesService,
    private reportService: ReportService,
    private router: Router
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
    translate.onLangChange.subscribe(() => {
      this.loadCharts();
    });
  }

  ngOnInit(): void {
    this.loadReports();
    this.fetchTranscriptions();
    this.fetchJobs();
    this.loadNotification();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.reportPaginator;
    this.transcriptionDataSource.paginator = this.transactionPaginator;
    this.jobDataSource.paginator = this.jobPaginator;
    if (this.isBrowser) {
      this.fetchChartsData().subscribe(() => {
        this.fetchReportsDetectedCount().subscribe(() => {
          this.loadCharts();
        });
      });
    }
    this.cdr.detectChanges();
  }

  normalizeFeature(value: number, min: number, max: number): number {
    if (value <= min) return 0;
    if (value >= max) return 100;
    return Math.round(((value - min) / (max - min)) * 100);
  }

  normalizeFeatures(features: { [key: string]: number }): {
    [key: string]: number;
  } {
    const normalized: { [key: string]: number } = {};
    for (const key in features) {
      if (this.featureScale[key]) {
        normalized[key] = this.normalizeFeature(
          features[key],
          this.featureScale[key].min,
          this.featureScale[key].max
        );
      } else {
        normalized[key] = 0;
      }
    }
    return normalized;
  }

  calcolaMedie(gruppo: DataItem[]): Features {
    const somma: Features = {};
    const conteggio = gruppo.length;

    gruppo.forEach((elemento) => {
      const normalized = this.normalizeFeatures(elemento.features);
      Object.keys(normalized).forEach((chiave) => {
        if (!somma[chiave]) {
          somma[chiave] = 0;
        }
        somma[chiave] += normalized[chiave];
      });
    });

    const medie: Features = {};
    Object.keys(somma).forEach((chiave) => {
      medie[chiave] = somma[chiave] / conteggio;
    });

    return medie;
  }

  async loadCharts(): Promise<void> {
    const medieHealthy = this.calcolaMedie(this.chartsData.healthy_control);
    const medieDisorder = this.calcolaMedie(this.chartsData.detected_disorder);
    const datiGrafico: any[] = Object.keys(medieHealthy).map(
      (caratteristica) => [
        caratteristica,
        medieDisorder[caratteristica] || 0,
        medieHealthy[caratteristica] || 0,
      ]
    );
    console.log(this.reportsDetectedCounts);
    this.translate
      .get([
        'homepage.sections.analysis-result.unhealthy',
        'homepage.sections.analysis-result.healthy',
      ])
      .subscribe((translations) => {
        this.riscontriChart = {
          chartType: 'BarChart',
          data: [
            [
              translations['homepage.sections.analysis-result.unhealthy'],
              this.reportsDetectedCounts
                ? this.reportsDetectedCounts.detected_disorder
                : 0,
            ],
            [
              translations['homepage.sections.analysis-result.healthy'],
              this.reportsDetectedCounts
                ? this.reportsDetectedCounts.healthy_control
                : 0,
            ],
          ],
          options: {
            bars: 'vertical',
            vAxis: { format: 'decimal' },
            backgroundColor: 'transparent',
            legend: { position: 'top', maxLines: 3 },
            colors: ['#b53f3f', '#3fb56a'],
          },
        };

        this.featureChart = {
          chartType: 'ColumnChart',
          data: [...datiGrafico],
          columnNames: [
            '',
            translations['homepage.sections.analysis-result.unhealthy'],
            translations['homepage.sections.analysis-result.healthy'],
          ],
          options: {
            bars: 'vertical',
            vAxis: { format: 'decimal' },
            //hAxis: { textPosition: 'none' },
            backgroundColor: 'transparent',
            legend: { position: 'top', maxLines: 3 },
            colors: ['#b53f3f', '#3fb56a'],
          },
        };

        this.cdr.detectChanges();
      });
  }

  loadReports(): void {
    this.reportService.getLatestsReports().subscribe(
      (response) => {
        this.reportsUser = response;
        this.dataSourceReport.data = this.reportsUser;
      },
      (error) => {
        console.error('Errore nel recupero dei report:', error);
      }
    );
  }

  loadTranscriptions(): void {
    this.transcriptionDataSource.data = this.transcriptions;
  }

  loadJobs(): void {
    this.jobDataSource.data = this.jobs;
  }

  goToTranscriptionDetail(transcription: Transcription): void {
    this.router.navigate(['/transcription-detail', transcription.upload_id]);
    console.log(
      'Navigazione al dettaglio della trascrizione:',
      transcription.filename
    );
  }

  goToJobDetail(job: Job): void {
    this.router.navigate(['/job-detail', job.upload_id]);
    console.log('Navigazione al dettaglio del job:', job.filename);
  }

  goToAllFeatures(): void {
    this.router.navigate(['/features']);
  }

  fetchTranscriptions(): void {
    try {
      this.transcriptionService
        .getTranscriptions(this.transcriptionPage, this.transcriptionPerPage)
        .subscribe((response) => {
          this.transcriptionDataSource = response.transcriptions;
          this.totalCount = response.total_count;
        });
    } catch (e) {}
  }

  fetchChartsData(): Observable<ChartsData> {
    return this.featuresService.getFeaturesChardData().pipe(
      tap((response) => {
        const data = response.data;
        this.chartsData = {
          healthy_control: data.healthy_control.map((item) => ({
            ...item,
            features: {
              Sentence_Length_Avg: item.features.Sentence_Length_Avg,
              RMS_Energy: item.features.RMS_Energy,
              Prosody_Variation: item.features.Prosody_Variation,
              Latency_Intra_Turn: item.features.Latency_Intra_Turn,
              Syntactic_Complexity: item.features.Syntactic_Complexity,
              Fluency_Disfluency: item.features.Fluency_Disfluency,
              Predictability_Entropy: item.features.Predictability_Entropy,
            },
          })),
          detected_disorder: data.detected_disorder.map((item) => ({
            ...item,
            features: {
              Sentence_Length_Avg: item.features.Sentence_Length_Avg,
              RMS_Energy: item.features.RMS_Energy,
              Prosody_Variation: item.features.Prosody_Variation,
              Latency_Intra_Turn: item.features.Latency_Intra_Turn,
              Syntactic_Complexity: item.features.Syntactic_Complexity,
              Fluency_Disfluency: item.features.Fluency_Disfluency,
              Predictability_Entropy: item.features.Predictability_Entropy,
            },
          })),
        };
      })
    );
  }

  fetchJobs(): void {
    try {
      this.jobService
        .getJobs(this.jobPage, this.jobPerPage)
        .subscribe((response) => {
          this.jobDataSource = response.jobs;
          this.jobTotalCount = response.total_count;
        });
    } catch (e) {}
  }

  fetchReportsDetectedCount(): Observable<ChartsData> {
    return this.reportService.getReportDetectedCount().pipe(
      tap((response: any) => {
        this.reportsDetectedCounts = response;
      })
    );
  }

  onPageChange(event: any): void {
    this.transcriptionPage = event.pageIndex + 1;
    this.transcriptionPerPage = event.pageSize;
    this.fetchTranscriptions();
  }

  onJobPageChange(event: any): void {
    this.jobPage = event.pageIndex + 1;
    this.jobPerPage = event.pageSize;
    this.fetchJobs();
  }

  loadNotification() {
    this.notificationService.notification().subscribe({
      next: (data) => {
        this.reports = data;
      },
      error: (error) => {
        console.error('Errore nel recupero delle notifiche', error);
      },
    });
  }

  goToReportDetail(upload_id: string): void {
    this.router.navigate(['/report'], { state: { upload_id } });
  }

  showNotificationTab(): boolean {
    return this.reports?.length >= 1;
  }

  shouldScroll(): boolean {
    return this.reports?.length >= 3;
  }

  showReportsTab(): boolean {
    return this.dataSourceReport.data?.length >= 1;
  }
}
