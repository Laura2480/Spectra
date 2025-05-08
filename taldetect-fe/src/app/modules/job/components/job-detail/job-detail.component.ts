import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { ActivatedRoute, Router } from '@angular/router';
import { JobService } from '../../services/job.service';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { TranscriptionService } from '../../../transcription/services/transcription.service';
import { DiarizationService } from '../../../diarization/services/diarization.service';

@Component({
  selector: 'app-job-detail',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule],
  templateUrl: './job-detail.component.html',
  styleUrl: './job-detail.component.scss'
})
export class JobDetailComponent implements OnInit {
  jobData: any;
  upload_id: string = '';
  progress: number = -1;

  constructor(private route: ActivatedRoute, private router: Router, private jobService: JobService, private transcriptionService: TranscriptionService, private diarizationService: DiarizationService) {}

  ngOnInit(): void {
    this.upload_id = this.route.snapshot.paramMap.get('upload_id') || '';
    this.getJobDetail();
  }

  getJobDetail(): void {
    this.jobService.getJobDetail(this.upload_id)?.subscribe(
      (data) => {
        this.jobData = data;
        if(data.step == "diarization"){
          this.diarizationService.getDiarizationProgress(this.upload_id).subscribe(
            (data) => {
              this.progress = data.progress;
            }
          )
        }
        if(data.step == "transcription"){
          this.progress = 0;
          this.transcriptionService.getSingleTranscriptionProgress(this.upload_id).subscribe(
            (data) => {
              this.progress = data;
            }
          )
        }
      },
      (error) => {
        console.error('Errore nel recupero del job detail:', error);
      }
    );
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'COMPLETED':
        return 'check_circle';
      case 'FAILED':
        return 'error';            
      case 'IN_PROGRESS':
        return 'hourglass_empty';   
      default:
        return 'help_outline';
    }
  }

  goBack(): void {
    this.router.navigate(['/']);
  }
}
