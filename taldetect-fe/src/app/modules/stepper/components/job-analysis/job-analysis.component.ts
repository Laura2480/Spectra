import { AfterViewInit, ChangeDetectorRef, Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { UploadComponent } from "../../../audio/components/upload/upload.component";
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { ALL_FEATURES, ALL_PARAMETERS } from '../../../../core/constants/default';

@Component({
  selector: 'app-job-analysis',
  standalone: true,
  imports: [UploadComponent, TranslateModule, CommonModule],
  templateUrl: './job-analysis.component.html',
  styleUrl: './job-analysis.component.scss'
})
export class JobAnalysisComponent implements AfterViewInit {
  @ViewChild(UploadComponent) uploadComponent!: UploadComponent;
  @Output() removeFile = new EventEmitter<any>();
  @Output() uploadFile = new EventEmitter<any>();
  isValidUpload = false;
  payload = {
    diarization_model: 'pyannote/speaker-diarization-3.1',
    //selected_transcription_model: 'turbo',
    selected_transcription_model: 'large',
    selected_gpt_model: 'Mixtral-8x7B-v0.1',
    features: ALL_FEATURES,
    parameters: ALL_PARAMETERS.filter(
      (el) => !el.name.includes("Total TALD") && !el.name.includes("TALD totale")
    )
  }

  constructor(private cdr: ChangeDetectorRef) { }

  ngAfterViewInit(): void {
    this.cdr.detectChanges();
  }

  sendUploadFile(formData: any) {
    this.uploadFile.emit(formData);
  }

  sendRemoveFile(index: any) {
    this.removeFile.emit(index);
  }

}
