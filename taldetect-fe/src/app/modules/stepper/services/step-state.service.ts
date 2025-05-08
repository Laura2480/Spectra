import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StepStateService {
  private stepValidities: Record<number, BehaviorSubject<boolean>> = {};
  private stepErrors: Record<number, BehaviorSubject<string | null>> = {};
  private stepData: Record<number, BehaviorSubject<any>> = {};

  setStepValid(stepIndex: number, isValid: boolean) {
    if (!this.stepValidities[stepIndex]) {
      this.stepValidities[stepIndex] = new BehaviorSubject<boolean>(false);
    }
    this.stepValidities[stepIndex].next(isValid);

    if (isValid) {
      this.setStepError(stepIndex, null);
    }
  }

  getStepValid(stepIndex: number) {
    if (!this.stepValidities[stepIndex]) {
      this.stepValidities[stepIndex] = new BehaviorSubject<boolean>(false);
    }
    return this.stepValidities[stepIndex].asObservable();
  }

  setStepError(stepIndex: number, errorMessage: string | null) {
    if (!this.stepErrors[stepIndex]) {
      this.stepErrors[stepIndex] = new BehaviorSubject<string | null>(null);
    }
    this.stepErrors[stepIndex].next(errorMessage);
  }

  getStepError(stepIndex: number) {
    if (!this.stepErrors[stepIndex]) {
      this.stepErrors[stepIndex] = new BehaviorSubject<string | null>(null);
    }
    return this.stepErrors[stepIndex].asObservable();
  }

  setStepData(stepIndex: number, data: any) {
    this.stepData[stepIndex] = new BehaviorSubject<any>(data);
  }

  getStepData(stepIndex: number) {
    if (!this.stepData[stepIndex]) {
      this.stepData[stepIndex] = new BehaviorSubject<any>({});
    }
    return this.stepData[stepIndex].asObservable();
  }
  
}
