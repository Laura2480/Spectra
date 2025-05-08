import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { TranscribeComponent } from "../transcribe/transcribe.component";
import { TranscriptionService } from '../../services/transcription.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-transcription-detail',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule, TranscribeComponent],
  templateUrl: './transcription-detail.component.html',
  styleUrl: './transcription-detail.component.scss'
})
export class TranscriptionDetailComponent {
  @ViewChild(TranscribeComponent) transcribe!: TranscribeComponent;

  transcriptionData: any = null;
  upload_id: string | null = '';

  constructor(private route: ActivatedRoute, private router: Router, private transcriptionService: TranscriptionService, private toastService: ToastrService) {

  }

  getTransactionDetail(): void {
    this.transcriptionService.getTranscriptionDetail(this.upload_id)?.subscribe(
      (data) => {
        this.transcriptionData = data;
        this.transcribe.transcription = data.transcription;
        this.transcribe.showProgress = false;
      },
      (error) => {
        console.error('Errore nel recupero del dettaglio della trascrizione:', error);
      }
    );
  }

  ngOnInit(): void {
    this.upload_id = this.route.snapshot.paramMap.get('upload_id') || '';
    this.getTransactionDetail();
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  saveChanges() {
    this.transcriptionService.updateTranscription(this.upload_id, this.transcribe.transcription).subscribe(
      (response) => {
        console.log('Trascrizione aggiornata con successo:', response);
        this.transcribe.isEdited = false;
        this.toastService.success('Trascrizione aggiornata con successo');
      },
      (error) => {
        console.error('Errore durante l\'aggiornamento della trascrizione:', error);
        this.toastService.error('Errore durante l\'aggiornamento della trascrizione');
      }
    );
  }

  downloadtranscription(type: string) {
    if (!this.upload_id) {
      this.toastService.error('Inserisci un Upload ID valido');
      return;
    }
    switch (type) {
      case 'pdf':
        this.transcriptionService.downloadTranscriptionPdf(this.upload_id)
          .subscribe(blob => {
            const downloadLink = document.createElement('a');
            const objectUrl = URL.createObjectURL(blob);
            downloadLink.href = objectUrl;
            downloadLink.download = `trascrizione_${this.transcriptionData.filename}.pdf`;
            downloadLink.click();
            URL.revokeObjectURL(objectUrl);
          }, error => {
            console.error('Errore durante il download', error);
            this.toastService.error('Si è verificato un errore durante il download della trascrizione.');
          });
        break;
      case 'txt':
        this.transcriptionService.downloadTranscriptionTxt(this.upload_id)
          .subscribe(blob => {
            const downloadLink = document.createElement('a');
            const objectUrl = URL.createObjectURL(blob);
            downloadLink.href = objectUrl;
            downloadLink.download = `trascrizione_${this.transcriptionData.filename}.txt`;
            downloadLink.click();
            URL.revokeObjectURL(objectUrl);
          }, error => {
            console.error('Errore durante il download', error);
            this.toastService.error('Si è verificato un errore durante il download della trascrizione.');
          });
        break;
      case 'json':
        this.transcriptionService.downloadTranscriptionJson(this.upload_id)
          .subscribe(blob => {
            const downloadLink = document.createElement('a');
            const objectUrl = URL.createObjectURL(blob);
            downloadLink.href = objectUrl;
            downloadLink.download = `trascrizione_${this.transcriptionData.filename}.json`;
            downloadLink.click();
            URL.revokeObjectURL(objectUrl);
          }, error => {
            console.error('Errore durante il download', error);
            this.toastService.error('Si è verificato un errore durante il download della trascrizione.');
          });
        break;
      case 'verbose':
        this.transcriptionService.downloadVerboseTranscription(this.upload_id)
          .subscribe(blob => {
            const downloadLink = document.createElement('a');
            const objectUrl = URL.createObjectURL(blob);
            downloadLink.href = objectUrl;
            downloadLink.download = `trascrizione_dettagliata_${this.transcriptionData.filename}.json`;
            downloadLink.click();
            URL.revokeObjectURL(objectUrl);
          }, error => {
            console.error('Errore durante il download', error);
            this.toastService.error('Si è verificato un errore durante il download della trascrizione.');
          });
        break;
      default:
        this.toastService.error('Tipo di download non valido');
    }
  }

}
