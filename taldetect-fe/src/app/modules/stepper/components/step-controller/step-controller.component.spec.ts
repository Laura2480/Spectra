import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StepControllerComponent } from './step-controller.component';

describe('StepControllerComponent', () => {
  let component: StepControllerComponent;
  let fixture: ComponentFixture<StepControllerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StepControllerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(StepControllerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
