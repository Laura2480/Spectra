import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, EventEmitter, Output } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-step-5',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule, TranslateModule],
  templateUrl: './step-5.component.html',
  styleUrl: './step-5.component.scss'
})
export class Step5Component implements AfterViewInit {
  isInProgress: boolean = true;
  @Output() loadedStep = new EventEmitter();

  constructor() {
  }

  ngAfterViewInit(): void {
    this.loadedStep.emit();
  }

}
