import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { DiarizeAudioComponent } from "../../../diarization/components/diarize-audio/diarize-audio.component";
import { StepStateService } from '../../services/step-state.service';

@Component({
  selector: 'app-step-3',
  standalone: true,
  imports: [DiarizeAudioComponent],
  templateUrl: './step-3.component.html',
  styleUrl: './step-3.component.scss'
})
export class Step3Component {
  @ViewChild(DiarizeAudioComponent) diarizeAudioComponent!: DiarizeAudioComponent;
  @Output() diarizeAudio = new EventEmitter();
  isValid: boolean = false;

  constructor(private stepStateService: StepStateService) {
    
  }

  sendDiarizeAudio() {
    this.diarizeAudio.emit();
  }

  ngAfterViewInit(): void {
    this.diarizeAudioComponent.isValid$.subscribe(isValid => {
      this.isValid = isValid;
      this.stepStateService.setStepValid(2, isValid);
      if(this.diarizeAudioComponent.isDiarizationCompleted)
        this.stepStateService.setStepError(2, "Per procedere, assicurati di selezionare almeno un medico e un paziente");
    });
  }

}
