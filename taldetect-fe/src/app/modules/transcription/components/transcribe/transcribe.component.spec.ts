import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TranscribeComponent } from './transcribe.component';

describe('TranscribeComponent', () => {
  let component: TranscribeComponent;
  let fixture: ComponentFixture<TranscribeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranscribeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TranscribeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
