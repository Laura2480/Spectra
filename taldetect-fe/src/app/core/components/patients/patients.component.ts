import { Component, OnInit, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { GoogleChartsModule } from 'angular-google-charts';
import { MatGridListModule } from '@angular/material/grid-list';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Patient } from '../../utils/BeanSupport';
import { PatientService } from './services/patients.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-patients',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    GoogleChartsModule,
    MatGridListModule,
    TranslateModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  templateUrl: './patients.component.html',
  styleUrl: './patients.component.scss',
})
export class PatientsComponent implements OnInit {
  displayedColumns = ['name', 'surname', 'email', 'age', 'actions'];
  patients: Patient[] = [];
  totalPatients = 0;
  pageSize = 10;
  form: Patient = { id: '', name: '', surname: '', email: '', age: '' };
  patientsDataSource = new MatTableDataSource<Patient>([]);
  selectedPatient: Patient | null = null;

  constructor(
    private patientService: PatientService,
    private toastr: ToastrService
  ) {}

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  ngOnInit(): void {
    this.fetchPatients();
  }

  fetchPatients(): void {
    this.patientService.getAllPatients().subscribe({
      next: (data) => {
        this.patients = data.map((patient) => ({
          ...patient,
          id: patient._id,
        }));
        this.totalPatients = this.patients.length;
        this.patientsDataSource.data = this.patients;
        this.patientsDataSource.paginator = this.paginator;
      },
      error: (err) => {
        console.error('Errore durante il fetch dei pazienti:', err);
      },
    });
  }

  onPageChange(event: any): void {
    // Gestione della paginazione
  }

  editPatient(patient: Patient): void {
    this.selectedPatient = patient;
    this.form = { ...patient };
  }

  deletePatient(patient_id: string): void {
    this.patientService.deletePatient(patient_id).subscribe({
      next: () => {
        this.fetchPatients();
      },
      error: (err) => console.error('Errore delete:', err),
    });
  }

  onSubmit(): void {
    const patientToSend = {
      ...this.form,
      id: this.form.id,
      age: this.form.age.toString(),
    };
    console.log(patientToSend);
    if (this.selectedPatient) {
      // Update
      this.patientService.updatePatient(patientToSend).subscribe({
        next: () => {
          this.fetchPatients();
          this.resetForm();
          this.toastr.info('Aggiornamento avvenuto con successo!');
        },
        error: (err) => this.toastr.error('Errore update:', err),
      });
    } else {
      // Save
      this.patientService.savePatient(patientToSend).subscribe({
        next: () => {
          this.fetchPatients();
          this.resetForm();
          this.toastr.info('Salvataggio avvenuto con successo!');
        },
        error: (err) => this.toastr.error('Errore insert:', err),
      });
    }
  }

  resetForm(): void {
    this.form = { id: '', name: '', surname: '', email: '', age: '' };
    this.selectedPatient = null;
  }
}
