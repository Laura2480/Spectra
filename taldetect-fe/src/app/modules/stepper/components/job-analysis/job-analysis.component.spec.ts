import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobAnalysisComponent } from './job-analysis.component';

describe('JobAnalysisComponent', () => {
  let component: JobAnalysisComponent;
  let fixture: ComponentFixture<JobAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobAnalysisComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(JobAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
