import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChooiceModalityComponent } from './chooice-modality.component';

describe('ChooiceModalityComponent', () => {
  let component: ChooiceModalityComponent;
  let fixture: ComponentFixture<ChooiceModalityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChooiceModalityComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChooiceModalityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
