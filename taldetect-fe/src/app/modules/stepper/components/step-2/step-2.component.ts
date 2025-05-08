import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { UploadComponent } from "../../../audio/components/upload/upload.component";
import { StepStateService } from '../../services/step-state.service';
import { AnalysisEstimationService } from '../../services/analysis-estimation.service';

@Component({
  selector: 'app-step-2',
  standalone: true,
  imports: [UploadComponent],
  templateUrl: './step-2.component.html',
  styleUrl: './step-2.component.scss'
})
export class Step2Component {
  isValid: boolean = false;
  timeAndAccurancyObject: { time: number, accuracy: number } = { time: 0, accuracy: 0 };
  @Output() uploadFile = new EventEmitter<any>();
  @Output() removeFile = new EventEmitter<any>();
  @ViewChild(UploadComponent) uploadComponent!: UploadComponent;

  constructor(
    private stepStateService: StepStateService,
    private analysisEstimationTimeAndAccurancyService: AnalysisEstimationService
  ) { }

  ngAfterViewInit(): void {
    this.uploadComponent.isValid$.subscribe(isValid => {
      this.isValid = isValid;
      this.stepStateService.setStepValid(1, isValid);
      //this.stepStateService.setStepError(1, isValid ? null : 'Devi caricare almeno un file per poter proseguire.');
      this.stepStateService.getStepData(0).subscribe(data => {
        const file = this.uploadComponent.files[0];
        if (file) {
          const url = URL.createObjectURL(file);
          const audio = new Audio();
          audio.src = url;

          audio.addEventListener('loadedmetadata', () => {
            const newData = {
              ...data,
              selectedFeatures: data.selectedFeatures,
              exportParameters: data.exportParameters,
              audioDuration: audio.duration,
              diarizationModel: data.diarizationModel,
              transcriptionModel: data.transcriptionModel,
              gptModel: data.gptModel
            };
            const timeAndAccurancyObject: { time: number, accuracy: number } = this.analysisEstimationTimeAndAccurancyService.estimateAnalysisTimeAndAccuracy(newData);
            this.timeAndAccurancyObject = timeAndAccurancyObject;
            URL.revokeObjectURL(url);
          });
        }

      });
    });
  }

  sendUploadFile(formData: any) {
    this.uploadFile.emit(formData);
  }

  sendRemoveFile(index: any) {
    this.removeFile.emit(index);
  }
}
