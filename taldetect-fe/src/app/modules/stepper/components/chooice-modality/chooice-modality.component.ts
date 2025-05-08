import { Component, EventEmitter, Output } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AnalysisMode } from '../../../../core/utils/BeanSupport';

@Component({
  selector: 'app-chooice-modality',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule],
  templateUrl: './chooice-modality.component.html',
  styleUrl: './chooice-modality.component.scss'
})
export class ChooiceModalityComponent {
  @Output() confirmChoice: EventEmitter<AnalysisMode> = new EventEmitter<AnalysisMode>();

  modes: AnalysisMode[] = [
    {
      mode: 'real-time',
      title: 'Analisi in Tempo Reale',
      description: 'Analisi in tempo reale dell\'intervista, con feedback immediato.',
      icon: 'timelapse'
    },
    {
      mode: 'job',
      title: 'Analisi tramite Job',
      description: 'Analisi tramite job, con elaborazione in background e report dettagliato.',
      icon: 'work'
    }
  ];

  selectedMode: AnalysisMode | null = null;

  constructor(private translate: TranslateService) {
    translate.onLangChange.subscribe(() => {
      this.translateCard();
    });
    this.translateCard();
  }

  translateCard(){
    this.translate.get(['stepper.chooice_modality.real_time.title', 'stepper.chooice_modality.real_time.description',
      'stepper.chooice_modality.job.title', 'stepper.chooice_modality.job.description'
    ]).subscribe(translations => {
      this.modes = [
        {
          mode: 'real-time',
          title: translations['stepper.chooice_modality.real_time.title'],
          description: translations['stepper.chooice_modality.real_time.description'],
          icon: 'timelapse'
        },
        {
          mode: 'job',
          title: translations['stepper.chooice_modality.job.title'],
          description: translations['stepper.chooice_modality.job.description'],
          icon: 'work'
        }
      ]
    });
  }

  selectMode(mode: AnalysisMode): void {
    this.selectedMode = mode;
  }

  sendConfirmChoice(): void {
    this.confirmChoice.emit(this.selectedMode);
  }

}
