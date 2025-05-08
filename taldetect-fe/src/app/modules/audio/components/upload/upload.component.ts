import { CommonModule, NgFor, NgIf } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { NgSelectModule } from '@ng-select/ng-select';
import { FormsModule } from '@angular/forms';
import { Doctor, PatientSelect } from '../../../../core/utils/BeanSupport';
import { HttpClient } from '@angular/common/http';
import { LocalStorageService } from '../../../../core/services/local-storage.service';
import { GET_DOCTORS_API, GET_PATIENTS_API } from '../../../../core/constants/api';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, NgFor, NgIf, MatProgressBarModule, MatIconModule, TranslateModule, NgSelectModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss'
})
export class UploadComponent {
  @Input() accuracy = 0;
  @Input() estimatedTime = 0;
  @Output() uploadFile = new EventEmitter<any>();
  @Output() removeFile = new EventEmitter<any>();
  private isValidSubject = new BehaviorSubject<boolean>(true);
  isValid$ = this.isValidSubject.asObservable();
  acceptedExtensions = ['.mp3', '.wav', '.aiff', '.flac', '.ogg', '.aac', '.m4a'];
  maxSizeMB = 1000;
  maxFiles = 1;
  progress: number = 0;
  files: File[] = [];
  selectedClinician!: string;
  selectedPatient!: string;
  doctors: Doctor[] = [];
  patients: PatientSelect[] = [];

  constructor(private toastr: ToastrService, private http: HttpClient, private localStorageService: LocalStorageService) {
    this.getDoctors();
    this.getPatients();
  }

  ngOnInit(): void {
    this.checkValidity();
  }

  checkValidity(): void {
    const isValidFile = this.files.length > 0;
    this.isValidSubject.next(isValidFile);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;
    if (input.files.length === 0) return;
    this.aggiungiFiles(input.files);
    input.value = '';
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer?.files) {
      this.aggiungiFiles(event.dataTransfer.files);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  aggiungiFiles(fileList: FileList) {
    const nuoviFile = Array.from(fileList);

    for (const file of nuoviFile) {
      if (!this.isEstensioneValida(file)) {
        this.toastr.warning(`Formato non consentito: ${file.name}`)
        continue;
      }
      if (file.size > this.maxSizeMB * 1024 * 1024) {
        this.toastr.warning(`Il file ${file.name} supera i ${this.maxSizeMB}MB`)
        continue;
      }
      if (this.files.length >= this.maxFiles) {
        this.toastr.warning('Raggiunto il numero massimo di file caricabili')
        break;
      }

      const formData = new FormData();
      formData.append('file', file);
      this.uploadFile.emit(formData);
      this.files.push(file);
    }

    this.checkValidity();
  }

  isEstensioneValida(file: File): boolean {
    return this.acceptedExtensions.some(ext =>
      file.name.toLowerCase().endsWith(ext)
    );
  }

  selezionaFile(inputRef: HTMLInputElement) {
    inputRef.click();
  }

  getEstimatedTimePercent(time: number): number {
    const maxTime = 60;
    return Math.round((time / maxTime) / maxTime * 100);
  }

  getEstimatedTimeColor(time: number): string {
    let intensity: number;
    if (time > 30) {
      intensity = Math.max(0.5, 1 - ((time - 30) / 30));
      return `rgba(255, 0, 0, ${intensity})`;
    } else if (time > 20) {
      intensity = Math.max(0.5, 1 - ((time - 20) / 10));
      return `rgba(255, 255, 0, ${intensity})`;
    } else {
      intensity = Math.max(0.5, 1 - (time / 20));
      return `rgba(0, 255, 0, ${intensity})`;
    }
  }

  getAccuracyColor(acc: number): string {
    let intensity: number;
    if (acc > 90) {
      intensity = Math.max(0.5, 1 - ((acc - 90) / 10));
      return `rgba(0, 255, 0, ${intensity})`;
    } else if (acc > 60) {
      intensity = Math.max(0.5, 1 - ((acc - 60) / 30));
      return `rgba(255, 255, 0, ${intensity})`;
    } else {
      intensity = Math.max(0.5, 1 - (acc / 60));
      return `rgba(255, 0, 0, ${intensity})`;
    }
  }

  sendRemoveFile(index: any) {
    this.removeFile.emit(index);
  }

  getIsValidSubject() {
    return this.isValidSubject;
  }

  getDoctors() {
    this.http.post<Doctor[]>(`${this.localStorageService.getItem("BASE_URL")}/${GET_DOCTORS_API}`, {}).subscribe(
      (data: Doctor[]) => {
        this.doctors = data.map(doctor => ({
          ...doctor,
          fullName: `${doctor.name} ${doctor.surname}`
        }));
      },
      (error) => {
        console.error('Errore durante il recupero dei medici', error);
      }
    );
  }

  getPatients() {
    this.http.post<PatientSelect[]>(`${this.localStorageService.getItem("BASE_URL")}/${GET_PATIENTS_API}`, {}).subscribe(
      (data: PatientSelect[]) => {
        this.patients = data.map(patient => ({
          ...patient,
          fullName: `${patient.name} ${patient.surname}`
        }));
      },
      (error) => {
        console.error('Errore durante il recupero dei medici', error);
      }
    );

  }

}
