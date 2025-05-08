import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeaturesDetailComponent } from './features-detail.component';

describe('FeaturesDetailComponent', () => {
  let component: FeaturesDetailComponent;
  let fixture: ComponentFixture<FeaturesDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeaturesDetailComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FeaturesDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
