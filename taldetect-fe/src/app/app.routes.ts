import { Routes } from '@angular/router';
import { HomepageComponent } from './core/components/homepage/homepage.component';
import { StepControllerComponent } from './modules/stepper/components/step-controller/step-controller.component';
import { LoginComponent } from './core/components/login/login.component';
import { CreateUserComponent } from './core/components/create-user/create-user.component';
import { TranscriptionDetailComponent } from './modules/transcription/components/transcription-detail/transcription-detail.component';
import { JobDetailComponent } from './modules/job/components/job-detail/job-detail.component';
import { AuthGuard } from './core/guards/auth.guard';
import { NotFoundComponent } from './core/components/not-found/not-found.component';
import { ReportComponent } from './core/components/report/report.component';
import { FeaturesListComponent } from './modules/features/components/features-list/features-list.component';
import { PatientsComponent } from './core/components/patients/patients.component';

export const routes: Routes = [
  { path: '', component: HomepageComponent, canActivate: [AuthGuard] },
  {
    path: 'interview-analysis',
    component: StepControllerComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'transcription-detail/:upload_id',
    component: TranscriptionDetailComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'job-detail/:upload_id',
    component: JobDetailComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'features',
    component: FeaturesListComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'features/detail/:upload_id',
    component: FeaturesListComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'report-detail/:upload_id',
    component: TranscriptionDetailComponent,
    canActivate: [AuthGuard],
  },
  { path: 'login', component: LoginComponent },
  { path: 'create-user', component: CreateUserComponent },
  { path: 'report', component: ReportComponent, canActivate: [AuthGuard] },
  { path: 'patients', component: PatientsComponent },
  { path: 'not-found', component: NotFoundComponent },
  { path: '**', redirectTo: 'not-found' },
];
