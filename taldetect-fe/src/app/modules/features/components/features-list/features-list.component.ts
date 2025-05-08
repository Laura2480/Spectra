import { CommonModule, isPlatformBrowser } from '@angular/common';
import {
  Component,
  ChangeDetectorRef,
  Inject,
  PLATFORM_ID,
} from '@angular/core';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { FeaturesService } from '../../services/features.service';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ChartsData, DataItem, Features, RegistrationSelect, Transcription } from '../../../../core/utils/BeanSupport';
import { NgSelectModule } from '@ng-select/ng-select';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-features-list',
  standalone: true,
  imports: [MatCardModule, MatIconModule, MatTooltipModule, TranslateModule, CommonModule, NgSelectModule, FormsModule],
  templateUrl: './features-list.component.html',
  styleUrl: './features-list.component.scss'
})
export class FeaturesListComponent {
  punteggio: number = 0;
  indicatorRotation: number = 0;
  isBrowser = false;
  riscontriChart: any = {};
  featureChart: any = {};
  transcriptionPage: number = 1;
  transcriptionPerPage: number = 10;
  totalCount: number = 0;
  jobPage: number = 1;
  jobPerPage: number = 10;
  jobTotalCount: number = 0;
  chartsData: ChartsData = null;
  dataList: any[] = [];
  selectedReg!: string;
  registrations: RegistrationSelect[] = [];
  showFeatures = [
    "Fluency_Disfluency",
    "Turn_Taking_Coordination",
    "Energy_Modulation",
    "Turn_Response_Time",
    "HNR",
    "Latency_Intra_Turn",
    "Syntactic_Complexity",
    "Functional_Word_Frequency",
    "Predictability_Entropy",
    "Stress_Voice",
    "Speech_Rate",
    "Sentence_Length_Avg",
    "Prosody_Variation",
    "RMS_Energy",
    "Pause_Duration",
    "Total_Speech_Duration",
    "Speech_Frequency",
    "Articulation_Pronunciation",
    "Speech_Emotions",
    "Echolalia_Repetition"
  ]
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
    Speech_Frequency: { min: 0, max: 60 },
    Speech_Emotions: { min: 0, max: 100 },
    Articulation_Pronunciation: { min: 0, max: 100 },
    Echolalia_Repetition: { min: 0, max: 2 },
  };

  legendConfig = {
    ranges: [
      { color: '#00C853', label: 'features.HEALTHY_RANGE', start: 0, end: 50 },
      { color: '#FFD600', label: 'features.WARNING_RANGE', start: 50, end: 80 },
      { color: '#D50000', label: 'features.CRITICAL_RANGE', start: 80, end: 100 }
    ],
    scaleMarks: [0, 25, 50, 75, 100]
  };

  constructor(
    private cdr: ChangeDetectorRef,
    @Inject(PLATFORM_ID) private platformId: any,
    private translate: TranslateService,
    private featuresService: FeaturesService,
    private router: Router
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
    this.getAllReg();
    translate.onLangChange.subscribe(() => {
      this.loadCharts();
    });
  }

  ngAfterViewInit(): void {
    if (this.isBrowser) {
      this.fetchChartsData().subscribe(() => {
        this.loadCharts();
      });
    }
    this.cdr.detectChanges();
  }

  public getChartData(value: number) {
    return [
      ['Punteggio', value],
    ];
  }

  calculateSpeechEmotions(features: Features): number {
    return (features["Prosody_Variation"] + features["Speech_Intonation"] + features["Stress_Voice"] + features["Energy_Modulation"] + features["HNR"]) / 5;
  }

  detectAnomaly(mean: number, std: number, threshold: number, value: number): boolean {
    const upperLimit = mean + threshold * std;
    const lowerLimit = mean - threshold * std;
    return value > upperLimit || value < lowerLimit;
  }

  classify_ecolalia(features: Features): number {
    if (features["Fluency_Disfluency"] > 0.4 && features["Energy_Modulation"] > 0.15) {
      return 2
    }
    if (features["Fluency_Disfluency"] > 0.2) {
      return 1
    }
    return 0
  }

  normalizeFeature(value: number, min: number, max: number): number {
    if (value <= min) return 0;
    if (value >= max) return 100;
    return Math.round(((value - min) / (max - min)) * 100);
  }

  normalizeFeatures(features: { [key: string]: number }): { [key: string]: number } {
    const normalized: { [key: string]: number } = {};
    for (const key in features) {
      if (this.featureScale[key]) {
        normalized[key] = this.normalizeFeature(features[key], this.featureScale[key].min, this.featureScale[key].max);
      } else {
        normalized[key] = 0;
      }
    }
    return normalized;
  }

  getMood(score: number): string {
    if (score > 70) return '<div class="d-flex flex-column justify-content-center align-center"> <span class="text-center display-4">😊</span> <span class="text-center">Felice</span></div>';
    else if (score > 40) return '<div class="d-flex flex-column justify-content-center align-center"> <span class="text-center display-4">😐</span> <span class="text-center">Neutro</span></div>';
    else if (score > 10) return '<div class="d-flex flex-column justify-content-center align-center"> <span class="text-center display-4">😢</span> <span class="text-center">Triste</span></div>';
    else return '<div class="d-flex flex-column justify-content-center align-center"> <span class="text-center display-4">😠</span> <span class="text-center">Arrabbiato</span></div>';
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

  addFeatures() {
    if (this.chartsData.detected_disorder != null) {
      this.chartsData.detected_disorder.forEach((item: any) => {
        item.features['Speech_Frequency'] = item.features.Speech_Rate && item.features.Speech_Rate >= 0 ? (item.features.Speech_Rate * 60) : 0;
        item.features['Articulation_Pronunciation'] = item.features.Speech_Rate && item.features.Prosody_Variation ? (item.features.Speech_Rate * item.features.Prosody_Variation) / 2 : 0;
        item.features['Echolalia_Repetition'] = this.classify_ecolalia(item.features);
        item.features['Speech_Emotions'] = this.calculateSpeechEmotions(item.features);
      });
    }

    if (this.chartsData.healthy_control != null) {
      this.chartsData.healthy_control.forEach((item: any) => {
        item.features['Speech_Frequency'] = item.features.Speech_Rate && item.features.Speech_Rate >= 0 ? item.features.Speech_Rate * 60 : 0;
        item.features['Articulation_Pronunciation'] = item.features.Speech_Rate && item.features.Prosody_Variation ? (item.features.Speech_Rate * item.features.Prosody_Variation) / 2 : 0;
        item.features['Echolalia_Repetition'] = this.classify_ecolalia(item.features);
        item.features['Speech_Emotions'] = this.calculateSpeechEmotions(item.features);
      });
    }
  }

  async loadCharts(): Promise<void> {
    this.addFeatures();
    const medieHealthy = this.chartsData.healthy_control ? this.calcolaMedie(this.chartsData.healthy_control) : [];
    const medieDisorder = this.chartsData.detected_disorder ? this.calcolaMedie(this.chartsData.detected_disorder) : [];
    const datiGrafico: any[] = Object.keys(medieHealthy).map((caratteristica) => [
      caratteristica,
      medieDisorder[caratteristica] || -1,
      medieHealthy[caratteristica] || -1,
    ]);
    const datiGraficoFiltrato = datiGrafico.filter(([caratteristica]) => this.showFeatures.includes(caratteristica));
    this.dataList = datiGraficoFiltrato;
    this.translate
      .get([
        'homepage.sections.analysis-result.unhealthy',
        'homepage.sections.analysis-result.healthy',
      ])
      .subscribe((translations) => {
        translations['homepage.sections.analysis-result.unhealthy'];
        this.cdr.detectChanges();
      });
  }

  goToTranscriptionDetail(transcription: Transcription): void {
    this.router.navigate(['/transcription-detail', transcription.upload_id]);
    console.log(
      'Navigazione al dettaglio della trascrizione:',
      transcription.filename
    );
  }

  fetchChartsData(): Observable<ChartsData> {
    return this.featuresService.getFeaturesChardData().pipe(
      tap((response) => {
        const data = response.data;
        this.chartsData = {
          healthy_control: data.healthy_control.map((item: any) => ({
            ...item,
            features: { ...item.features }
          })),
          detected_disorder: data.detected_disorder.map((item: any) => ({
            ...item,
            features: { ...item.features }
          }))
        };
      })
    );
  }

  calculateRotation(value: number): number {
    const minValue = 0;
    const maxValue = 100;
    const minAngle = -135;
    const maxAngle = 135;

    return Math.max(-93, (Math.min((((value - minValue) * (maxAngle - minAngle)) / (maxValue - minValue) + minAngle), 93)));
  }

  getAllReg() {
    this.featuresService.getAllReg().subscribe({
      next: (response) => {
        this.registrations = response;
      },
      error: (error) => {
      },
    });
  }

  onRegistrationChange(selected: string): void {
    if (selected) {
      this.featuresService.getFeaturesByFilename(selected).subscribe({
        next: (response) => {
          if (response.status === "healthy_control") {
            this.chartsData.healthy_control = [{
              filename: selected,
              features: response.features
            }];
            this.chartsData.detected_disorder = null;
          } else {
            this.chartsData.healthy_control = null
            this.chartsData.detected_disorder = [{
              filename: selected,
              features: response.features
            }];
          }
          this.loadCharts();
        },
        error: (error) => {
        },
      });
    } else {
      this.fetchChartsData().subscribe(() => {
        this.loadCharts();
      });
    }
  }
}