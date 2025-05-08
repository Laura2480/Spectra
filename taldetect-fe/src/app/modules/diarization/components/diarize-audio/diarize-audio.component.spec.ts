import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DiarizeAudioComponent } from './diarize-audio.component';

describe('DiarizeAudioComponent', () => {
  let component: DiarizeAudioComponent;
  let fixture: ComponentFixture<DiarizeAudioComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DiarizeAudioComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DiarizeAudioComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
