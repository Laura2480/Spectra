import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-transcribe',
  standalone: true,
  imports: [MatProgressBarModule, CommonModule, FormsModule, TranslateModule],
  templateUrl: './transcribe.component.html',
  styleUrl: './transcribe.component.scss'
})
export class TranscribeComponent implements OnInit {
  ngOnInit(): void {
    this.sendTranscribeAudio();
  }
  transcription: any = [];
  progress = 0;
  trascriptionBackup: string = "";
  private isValidSubject = new BehaviorSubject<boolean>(false);
  showProgress:boolean = true;
  isValid$ = this.isValidSubject.asObservable();
  isEdited:boolean = false;

  @Output() transcribeAudio = new EventEmitter();
  
  sendTranscribeAudio() {
    this.transcribeAudio.emit();
  }

  editIndex: number | null = null;

  editTranscription(index: number): void {
    this.trascriptionBackup = this.transcription[index].text;
    this.editIndex = index;
  }

  saveEdit(index: number): void {
    console.log(`Trascrizione aggiornata per l'indice ${index}: ${this.transcription[index].text}`);
    this.isEdited = true;
    this.editIndex = null;
  }

  cancelSegment(index: number): void {
    if (index >= 0 && index < this.transcription.length) {
      this.transcription.splice(index, 1);
      this.isEdited = true;
    }
  }  

  cancelEdit(index: number) {
    this.transcription[index].text = this.trascriptionBackup;
    this.editIndex = null;
  }

  selectText(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (window.getSelection && document.createRange) {
      const range = document.createRange();
      range.selectNodeContents(target);
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(range);
    }
  }

  getIsValidSubject(){
    return this.isValidSubject;
  }
}
