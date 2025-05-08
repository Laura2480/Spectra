import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeaturesTableComponent } from './features-table.component';

describe('FeaturesTableComponent', () => {
  let component: FeaturesTableComponent;
  let fixture: ComponentFixture<FeaturesTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeaturesTableComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FeaturesTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
