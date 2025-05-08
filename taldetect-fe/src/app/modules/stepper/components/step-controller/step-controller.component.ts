import { Component, ChangeDetectorRef, ViewChild } from '@angular/core';
import { StepStateService } from '../../services/step-state.service';
import { CommonModule } from '@angular/common';
import { MatStepper, MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { Step1Component } from '../step-1/step-1.component';
import { Step2Component } from '../step-2/step-2.component';
import { Step3Component } from '../step-3/step-3.component';
import { Step4Component } from '../step-4/step-4.component';
import { Step5Component } from '../step-5/step-5.component';
import { ConfigService } from '../../../configuration/services/config.service';
import { FileService } from '../../../audio/services/file.service';
import { Subscription } from 'rxjs';
import { mapError } from '../../../../core/utils/remapError';
import { DiarizationService } from '../../../diarization/services/diarization.service';
import { UPDATE_DIARIZATION_PROGRESS_INTERVAL_MS, UPDATE_REPORT_STATUS_INTERVAL_MS } from '../../../../core/constants/interval';
import { TranscriptionService } from '../../../transcription/services/transcription.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ChooiceModalityComponent } from '../chooice-modality/chooice-modality.component';
import { JobAnalysisComponent } from '../job-analysis/job-analysis.component';
import { JobService } from '../../../job/services/job.service';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { MatIconModule } from '@angular/material/icon';
import {
  AnalysisMode,
  ConfigPayload,
} from '../../../../core/utils/BeanSupport';
import { ReportService } from '../../../../core/components/report/services/report.service';
import { StepperReportService } from '../../../report/services/stepper-report.service';
import { interval } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';

@Component({
  selector: 'app-step-controller',
  templateUrl: './step-controller.component.html',
  standalone: true,
  imports: [
    CommonModule,
    MatStepperModule,
    MatButtonModule,
    MatIconModule,
    Step1Component,
    Step2Component,
    Step3Component,
    Step4Component,
    Step5Component,
    TranslateModule,
    ChooiceModalityComponent,
    JobAnalysisComponent,
  ],
  styleUrl: './step-controller.component.scss',
})
export class StepControllerComponent {
  @ViewChild(MatStepper) stepper!: MatStepper;
  @ViewChild(Step1Component) step1Component!: Step1Component;
  @ViewChild(Step2Component) step2Component!: Step2Component;
  @ViewChild(Step3Component) step3Component!: Step3Component;
  @ViewChild(Step4Component) step4Component!: Step4Component;
  @ViewChild(Step5Component) step5Component!: Step5Component;
  @ViewChild(JobAnalysisComponent) jobAnalysisComponent!: JobAnalysisComponent;
  activeStep: number = 0;
  stepValidities: Record<number, boolean> = {};
  stepErrors: Record<number, string | null> = {};
  uploadSubscription: Subscription | null = null;
  upload_id: any;
  selectedMode: null | 'real-time' | 'job' = null;
  steps = [
    { title: 'Configuration', component: Step1Component },
    { title: 'Upload File', component: Step2Component },
    { title: 'Diarize Audio', component: Step3Component },
    { title: 'Transcription', component: Step4Component },
    { title: 'Report', component: Step5Component },
  ];
  stepsEditable = [false, false, false, false, false];
  stepsCompleted = [false, false, false, false, false];
  private pollingSubscription: Subscription;

  constructor(
    private stepStateService: StepStateService,
    private configService: ConfigService,
    private fileService: FileService,
    private diarizationService: DiarizationService,
    private transcriptionService: TranscriptionService,
    private jobService: JobService,
    private cdr: ChangeDetectorRef,
    private translate: TranslateService,
    private router: Router,
    private toastr: ToastrService,
    private stepperReportService: StepperReportService,
    private reportService: ReportService
  ) {
    translate.onLangChange.subscribe(() => {
      this.translate
        .get([
          'stepper.configuration.title',
          'stepper.upload.title',
          'stepper.diarize.title',
          'stepper.transcription.title',
          'stepper.report.title',
        ])
        .subscribe((translations) => {
          this.steps = [
            {
              title: translations['stepper.configuration.title'],
              component: Step1Component,
            },
            {
              title: translations['stepper.upload.title'],
              component: Step2Component,
            },
            {
              title: translations['stepper.diarize.title'],
              component: Step3Component,
            },
            {
              title: translations['stepper.transcription.title'],
              component: Step4Component,
            },
            {
              title: translations['stepper.report.title'],
              component: Step5Component,
            },
          ];
        });
    });
  }

  ngOnInit() {
    for (let i = 0; i < this.steps.length; i++) {
      this.stepStateService.getStepValid(i).subscribe((valid) => {
        this.stepValidities[i] = valid;
        this.cdr.detectChanges();
      });
      this.stepStateService.getStepError(i).subscribe((error) => {
        this.stepErrors[i] = error;
        this.cdr.detectChanges();
      });
    }
  }

  isValidStep(step: number): boolean {
    return this.stepValidities[step] ?? false;
  }

  getErrorForStep(step: number): string | null {
    return this.stepErrors[step] ?? null;
  }

  goToNextStep(currentStep: number) {
    if (
      currentStep == 0 &&
      this.step1Component &&
      this.isValidStep(currentStep)
    ) {
      this.sendConfig();
    }
    if (
      currentStep == 1 &&
      this.step2Component &&
      this.isValidStep(currentStep)
    ) {
      this.stepsCompleted[1] = true;
      setTimeout(() => {
        this.stepper.next();
      });
    }
    if (
      currentStep == 2 &&
      this.step2Component &&
      this.isValidStep(currentStep)
    ) {
      this.assignRoleToSpeakers();
    }
    if (
      currentStep == 3 &&
      this.step3Component &&
      this.isValidStep(currentStep)
    ) {
      this.stepsCompleted[3] = true;
      this.saveTranscription();
      setTimeout(() => {
        this.stepper.next();
      });
    }
  }

  loadedStep() {
    this.startGenerateReport();
  }

  assignRoleToSpeakers() {
    const roles: Record<string, string> = {};
    this.step3Component.diarizeAudioComponent.speakers.forEach(
      (speakerObj, index) => {
        if (this.step3Component.diarizeAudioComponent.selectedRoles[index]) {
          roles[speakerObj.speaker] =
            this.step3Component.diarizeAudioComponent.selectedRoles[index];
        }
      }
    );
    this.diarizationService.assignRoles(this.upload_id, roles).subscribe(
      (response) => {
        console.log('Ruoli assegnati:', response);
        this.stepsCompleted[2] = true;
        setTimeout(() => {
          this.stepper.next();
        });
      },
      (error) => {
        console.error("Errore nell'assegnazione dei ruoli:", error);
        this.toastr.error("Errore nell'assegnazione dei ruoli:" + error);
      }
    );
  }

  goToPreviusStep(index: number) {
    this.stepsEditable[index - 1] = true;
    this.stepsCompleted[index] = false;
    setTimeout(() => {
      this.stepper.previous();
      this.stepsEditable[index - 1] = false;
    });
  }

  changedStep(currentStep: any) {
    if (currentStep == 0 && this.step2Component) {
      this.step2Component.uploadComponent.files = [];
    }
  }

  /* Step 0 Choice Modality */
  setSelectedMode(mode: AnalysisMode) {
    this.selectedMode = mode.mode;
  }

  uploadFileByJob(formData: any): void {
    this.uploadSubscription = this.fileService.uploadFile(formData.get("file"), this.jobAnalysisComponent.uploadComponent.selectedClinician, this.jobAnalysisComponent.uploadComponent.selectedPatient).subscribe({
      next: (result: any) => {
        if (result != null) {
          if (typeof result === 'number') {
            this.jobAnalysisComponent.uploadComponent.progress = result;
          } else {
            this.upload_id = result.upload_id;
            this.jobAnalysisComponent.isValidUpload = true;
            this.startJob(result.upload_id);
          }
        }
      },
      error: (err) => {
        this.toastr.error("Errore durante l'upload: Server offline");
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      },
    });
  }

  jobRemoveFile(index: number) {
    this.jobAnalysisComponent.uploadComponent.files.splice(index, 1);
    if (this.uploadSubscription) {
      this.uploadSubscription.unsubscribe();
      this.uploadSubscription = null;
    }
    this.jobAnalysisComponent.uploadComponent.progress = 0;
    this.jobAnalysisComponent.uploadComponent.checkValidity();
  }

  startJob(uploadId: string) {
    this.jobService
      .startJob(uploadId, this.jobAnalysisComponent.payload)
      .subscribe({
        next: (result: any) => {
          this.router.navigate(['/job-detail', uploadId]);
          console.log('Job started:', result);
        },
        error: (err) => {
          this.toastr.error("Errore durante l'upload: Server offline");
          window.location.reload();
        },
      });
  }

  /* Step 1 Save Config */
  sendConfig(): void {
    if (this.step1Component) {
      const payload: ConfigPayload = {
        diarization_model:
          this.step1Component.preProcessingComponent.selectedDiarizationModel,
        selected_transcription_model:
          this.step1Component.preProcessingComponent.selectedTranscriptionModel,
        selected_gpt_model:
          this.step1Component.preProcessingComponent.selectedGptModel,
        features: this.step1Component.preProcessingComponent.features,
        parameters: this.step1Component.preProcessingComponent.parameters.filter(
          (el) => !el.name.includes("Total TALD") && !el.name.includes("TALD totale")
        )
        // features: this.step1Component.preProcessingComponent.features.filter(
        //   (el) => el.checked
        // ),
        // parameters:
        //   this.step1Component.preProcessingComponent.parameters.filter(
        //     (el) => el.checked
        //   ),
      };

      this.configService.configure(payload).subscribe({
        next: (data) => {
          this.stepsCompleted[0] = true;
          setTimeout(() => {
            this.stepper.next();
          });
          console.log('Configurazione salvata:', data);
        },
        error: (error) => {
          this.toastr.error(mapError(error.statusText));
          console.error('Errore:', error);
        },
      });
    }
  }

  /* Step 2 Upload File */
  uploadFile(formData: any): void {
    this.uploadSubscription = this.fileService.uploadFile(formData.get("file"), this.step2Component.uploadComponent.selectedClinician, this.step2Component.uploadComponent.selectedPatient).subscribe({
      next: (result: any) => {
        if (result != null) {
          if (typeof result === 'number') {
            this.step2Component.uploadComponent.progress = result;
            this.step2Component.uploadComponent.getIsValidSubject().next(false);
          } else {
            console.log('Response from server:', result);
            this.step2Component.uploadComponent.getIsValidSubject().next(true);
            this.upload_id = result.upload_id;
          }
        }
      },
      error: (err) => {
        this.step2Component.uploadComponent.getIsValidSubject().next(false);
        this.toastr.error("Errore durante l'upload: Server offline");
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      },
    });
  }

  removeFile(index: number) {
    this.step2Component.uploadComponent.files.splice(index, 1);
    if (this.uploadSubscription) {
      this.uploadSubscription.unsubscribe();
      this.uploadSubscription = null;
    }
    this.step2Component.uploadComponent.progress = 0;
    this.step2Component.uploadComponent.checkValidity();
  }

  /* Step 3 Diarization */
  startDiarization() {
    setTimeout(() => {
      this.diarizationService.startDiarization(this.upload_id).subscribe(() => {
        const intervalId = setInterval(() => {
          this.updateDiarizationProgress();
          if (this.step3Component.diarizeAudioComponent.progress >= 100) {
            clearInterval(intervalId);
          }
        }, UPDATE_DIARIZATION_PROGRESS_INTERVAL_MS);
      });
    });
  }

  updateDiarizationProgress() {
    this.diarizationService
      .getDiarizationProgress(this.upload_id)
      .subscribe((response) => {
        this.step3Component.diarizeAudioComponent.progress = response.progress;
        if (
          this.step3Component.diarizeAudioComponent.progress >= 100 &&
          !this.step3Component.diarizeAudioComponent.isDiarizationCompleted
        ) {
          this.step3Component.diarizeAudioComponent.isDiarizationCompleted =
            true;
          this.getDiarizationSpeakers();
        }
      });
  }

  getDiarizationSpeakers() {
    this.diarizationService
      .getDiarizationSpeakers(this.upload_id)
      .subscribe((response) => {
        /* Lista di parlanti */
        if (response.speakers != null && response.speakers.length > 0) {
          this.step3Component.diarizeAudioComponent.selectedRoles =
            response.speakers.map(() => 'paziente');
          for (let i = 0; i < response.speakers.length; i++) {
            this.loadSpeakersExcerpt(response.speakers[i]);
          }
        }

        this.stepStateService.setStepValid(2, false);
        this.stepStateService.setStepError(
          2,
          'Per procedere, assicurati di selezionare almeno un medico e un paziente'
        );
      });
  }

  loadSpeakersExcerpt(speaker: string) {
    this.diarizationService
      .getSpeakerExcerpt(this.upload_id, speaker)
      .subscribe((blob) => {
        const audioUrl = URL.createObjectURL(blob);
        this.step3Component.diarizeAudioComponent.speakers.push({
          speaker: speaker,
          audioUrl: audioUrl,
        });
      });
  }

  /* Step 4 Transcription */
  transcribeAudio() {
    this.transcriptionService.transcribeAudio(this.upload_id).subscribe(
      (response) => {
        console.log('Trascrizione avviata:', response);

        this.transcriptionService
          .getTranscriptionProgress(this.upload_id)
          .subscribe({
            next: (progress) => {
              console.log('Progresso trascrizione:', progress);
              this.step4Component.trascribeAudioComponent.progress = progress;

              if (progress === 100) {
                console.log('Trascrizione completata');
                this.getFinalTranscription();
              }
            },
            error: (err) =>
              console.error(
                'Errore nella progressione della trascrizione:',
                err
              ),
            complete: () => console.log('Monitoraggio completato'),
          });
      },
      (error) => {
        console.error('Errore nella trascrizione:', error);
      }
    );
  }

  getFinalTranscription() {
    this.transcriptionService
      .getTranscriptionResult(this.upload_id)
      .subscribe((response) => {
        console.log('Trascrizione:', response.transcription);
        this.step4Component.trascribeAudioComponent.transcription =
          response.transcription;
        this.step4Component.trascribeAudioComponent.transcription.sort(
          (a: any, b: any) => {
            if (a.start === b.start) {
              return a.end - b.end;
            }
            return a.start - b.start;
          }
        );
        this.step4Component.trascribeAudioComponent
          .getIsValidSubject()
          .next(true);
      });
  }

  saveTranscription() {
    const corrected_transcription =
      this.step4Component.trascribeAudioComponent.transcription;

    if (!corrected_transcription) {
      console.warn(
        'Nessuna trascrizione corretta disponibile per il salvataggio.'
      );
      return;
    }

    this.transcriptionService
      .saveCorrectedTranscription(this.upload_id, corrected_transcription)
      .subscribe(
        (response) => {
          console.log(response.message);
        },
        (error) => {
          console.error('Errore nel salvataggio della trascrizione:', error);
        }
      );
  }

  /* Step 5 Generate Report */
  startGenerateReport() {
    this.stepperReportService.startGenerateReport(this.upload_id).subscribe(response => {
      this.pollingSubscription = interval(UPDATE_REPORT_STATUS_INTERVAL_MS)
        .pipe(
          switchMap(() => this.reportService.reportById(this.upload_id)),
          takeWhile(response => response.status !== 'TO_EVALUATE', true)
        )
        .subscribe(response => {
          if (response.status === 'TO_EVALUATE') {
            this.pollingSubscription.unsubscribe();
            this.goToReportDetail();
          }
        });
    });
  }

  goToReportDetail() {
    this.router.navigate(['/report-detail', this.upload_id]);
  }

  ngOnDestroy() {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
    }
  }
}
