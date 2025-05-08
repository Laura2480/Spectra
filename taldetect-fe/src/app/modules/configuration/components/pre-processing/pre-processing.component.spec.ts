import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PreProcessingComponent } from './pre-processing.component';

describe('PreProcessingComponent', () => {
  let component: PreProcessingComponent;
  let fixture: ComponentFixture<PreProcessingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PreProcessingComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PreProcessingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
