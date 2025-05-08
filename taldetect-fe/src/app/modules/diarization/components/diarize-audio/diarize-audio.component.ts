import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { CommonModule, NgFor } from '@angular/common';
import { NgSelectModule } from '@ng-select/ng-select';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-diarize-audio',
  standalone: true,
  imports: [NgFor, MatProgressBarModule, CommonModule, NgSelectModule, FormsModule, TranslateModule],
  templateUrl: './diarize-audio.component.html',
  styleUrl: './diarize-audio.component.scss'
})
export class DiarizeAudioComponent implements OnInit {
  ngOnInit(): void {
    this.sendDiarizeAudio();
  }
  @Output() diarizeAudio = new EventEmitter();
  progress = 0;
  isDiarizationCompleted = false;
  isCompleted = false;
  speakers: { speaker: string, audioUrl: string }[] = new Array<{ speaker: string, audioUrl: string }>();
  selectedRoles = new Array();
  private isValidSubject = new BehaviorSubject<boolean>(false);

  isValid$ = this.isValidSubject.asObservable();

  roles = [
    { value: 'medico', label: 'Medico' },
    { value: 'paziente', label: 'Paziente' }
  ];

  constructor(private translate: TranslateService) {
    this.translate.get(['stepper.diarize.patient', 'stepper.diarize.doctor']).subscribe(translations => {
      this.roles = [
        { value: 'medico', label: translations['stepper.diarize.doctor'] },
        { value: 'paziente', label: translations['stepper.diarize.patient'] }
      ];
    });
  }

  sendDiarizeAudio() {
    this.diarizeAudio.emit();
  }

  checkValidity(): void {
    const hasMedico = this.selectedRoles.some(role => role === "medico");
    const hasPaziente = this.selectedRoles.some(role => role === "paziente");
    this.isValidSubject.next(hasMedico && hasPaziente);
  }
}