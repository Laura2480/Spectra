import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { TranscribeComponent } from "../../../transcription/components/transcribe/transcribe.component";
import { StepStateService } from '../../services/step-state.service';

@Component({
  selector: 'app-step-4',
  standalone: true,
  imports: [TranscribeComponent],
  templateUrl: './step-4.component.html',
  styleUrl: './step-4.component.scss'
})
export class Step4Component {
  @ViewChild(TranscribeComponent) trascribeAudioComponent!: TranscribeComponent;
  @Output() transcribeAudio = new EventEmitter();
  isValid: boolean = false;

  constructor(private stepStateService: StepStateService) {

  }

  sendTranscribeAudio() {
    this.transcribeAudio.emit();
  }

  ngAfterViewInit(): void {
    this.trascribeAudioComponent.isValid$.subscribe(isValid => {
      this.isValid = isValid;
      this.stepStateService.setStepValid(3, isValid);
    });
  }
}
