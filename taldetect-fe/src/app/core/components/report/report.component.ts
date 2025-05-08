import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { Router, RouterModule } from '@angular/router';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { ReportService } from './services/report.service';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { Patient, ReportUser } from '../../utils/BeanSupport';

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    TranslateModule,
    ReactiveFormsModule,
    RouterModule,
    MatProgressBarModule,
    MatIconModule,
  ],
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.scss'],
})
export class ReportComponent implements OnInit {
  BASE_URL: string;
  reportUser: ReportUser;
  patient: Patient;
  upload_id: string;
  editingIndex: number | null = null;
  isDisabledEdit: boolean = false;
  isClosedEvaluation: boolean = false;
  isEditing: boolean = false;
  isLoading: boolean = false;

  constructor(
    private router: Router,
    private toastr: ToastrService,
    private reportService: ReportService
  ) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state?.['upload_id']) {
      this.upload_id = navigation.extras.state['upload_id'];
    } else {
      this.toastr.error('Errore uploadId');
      this.router.navigate(['/not-found']);
    }
  }

  ngOnInit(): void {
    if (!this.upload_id) {
      this.toastr.error('Errore: upload_id mancante');
      throw new Error('Upload ID non passato.');
    }

    forkJoin({
      report: this.reportService.reportById(this.upload_id),
      patient: this.reportService.patientById(this.upload_id),
    }).subscribe({
      next: ({ report, patient }) => {
        this.isLoading = true;
        this.reportUser = report;
        this.patient = patient;

        console.log('Report ricevuto:', report);
        console.log('Paziente ricevuto:', patient);
      },
      error: (err) => {
        console.error('Errore nel caricamento dei dati:', err);
        this.toastr.error('Errore nel caricamento dei dati.');
      },
    });
  }

  toggleEdit(index: number) {
    this.editingIndex = this.editingIndex === index ? null : index;
  }

  acceptEvaluation() {
    this.isClosedEvaluation = true;
    this.isDisabledEdit = false;
    this.isEditing = false;

    //SALVARE STATO
    this.reportUser.status = 'COMPLETED';
    this.reportUser.score = this.calculateScore();

    this.reportService.updateReport(this.reportUser).subscribe({
      next: () => {
        this.toastr.success('Valutazione aggiornata con successo!');
        this.router.navigate(['']);
      },
      error: (err) => {
        console.error('Errore durante l’aggiornamento della valutazione:', err);
        this.toastr.error(
          'Errore durante l’aggiornamento della valutazione.',
          'Errore'
        );
      },
    });

    this.toastr.info('Valutazione Conclusa');
  }

  editAction() {
    this.isDisabledEdit = true;
    this.isEditing = true;
  }

  saveEditEvaluation() {
    this.isEditing = false;
    this.isDisabledEdit = false;
    this.isClosedEvaluation = true;

    this.reportUser.status = 'COMPLETED';
    this.reportUser.score = this.calculateScore();

    this.reportService.updateReport(this.reportUser).subscribe({
      next: () => {
        this.toastr.success('Valutazione aggiornata con successo!');
      },
      error: (err) => {
        console.error('Errore durante l’aggiornamento della valutazione:', err);
        this.toastr.error(
          'Errore durante l’aggiornamento della valutazione.',
          'Errore'
        );
      },
    });
    this.toastr.info('Valutazione Conclusa');
  }

  calculateScore() {
    let score = 0;
    this.reportUser.report.forEach((element) => {
      score = score + element.punteggio;
    });
    return score;
  }

  showScore() {
    return this.reportUser.score != 0;
  }

  getReportScoreById() {
    const uploadId = this.upload_id;
    console.log('Requested template: ', uploadId);

    this.reportService.getReportScorePatient(uploadId).subscribe(
      (blob) => {
        const a = document.createElement('a');
        const objectUrl = URL.createObjectURL(blob);
        a.href = objectUrl;
        a.download = 'report_tald_score.xlsx';
        a.click();
        URL.revokeObjectURL(objectUrl);
      },
      (error) => {
        console.error('Errore nel download:', error);
      }
    );
  }

  getReportCompletedById() {
    const uploadId = this.upload_id;
    console.log('Requested template: ', uploadId);

    this.reportService.getReportCompletedPatient(uploadId).subscribe(
      (blob) => {
        const a = document.createElement('a');
        const objectUrl = URL.createObjectURL(blob);
        a.href = objectUrl;
        a.download = 'report_tald_completed.pdf';
        a.click();
        URL.revokeObjectURL(objectUrl);
      },
      (error) => {
        console.error('Errore nel download:', error);
      }
    );
  }
}
