import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { PreProcessingComponent } from "../../../configuration/components/pre-processing/pre-processing.component";
import { StepStateService } from '../../services/step-state.service';

@Component({
  selector: 'app-step-1',
  standalone: true,
  imports: [PreProcessingComponent],
  templateUrl: './step-1.component.html',
  styleUrl: './step-1.component.scss'
})
export class Step1Component {
  isValid: boolean = false;
  @ViewChild(PreProcessingComponent) preProcessingComponent!: PreProcessingComponent;
  @Output() changedStep: EventEmitter<number> = new EventEmitter<number>();

  constructor(private stepStateService: StepStateService) { }

  ngAfterViewInit(): void {
    this.preProcessingComponent.isValid$.subscribe(isValid => {
      this.isValid = isValid;
      this.stepStateService.setStepValid(0, isValid);
      this.stepStateService.setStepError(0, isValid ? null : 'Devi selezionare almeno una feature e un parametro per il report.');
      this.stepStateService.setStepData(0, this.preProcessingComponent.getPreProcessingData());
    });
  }

  isChangedStep() {
    this.changedStep.emit(0);
  }
}
