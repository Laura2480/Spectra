import { Injectable } from '@angular/core';

export interface ReportItem {
  tipologia: string;
  punteggio: number;
  giustificazione: string;
  pattern_rilevati: string[];
}

export interface ReportUser {
  id: string;
  upload_id: string;
  filename: string;
  report: ReportItem[];
  status: string;
  score: number;
}

export interface Patient {
  id: string;
  name: string;
  surname: string;
  email: string;
  age: string;
  _id?: string;
}

export interface LoginForm {
  email: string;
  password: string;
}

export interface User {
  email: string;
  role: string;
  name: string;
  surname: string;
}

export interface Token {
  jwt: string;
  auth: string;
}

export interface Transcription {
  filename: string;
  transcription: Array<TranscriptionElement>;
  upload_id: string;
}

export interface Job {
  filename: string;
  completed_at: string;
  created_at: string;
  status: string;
  step: string;
  updated_at: string;
  upload_id: string;
}

export interface Features {
  [key: string]: number;
}

export interface DataItem {
  filename: string;
  features: Features;
}

export interface ChartsData {
  healthy_control: DataItem[];
  detected_disorder: DataItem[];
}

export interface TranscriptionElement {
  speaker: string;
  role: string;
  start: number;
  end: number;
  text: string;
}

export interface Model {
  name: string;
  value: string;
}

export interface Feature {
  name: string;
  checked: boolean;
  description: string;
}

export interface Parameter {
  name: string;
  checked: boolean;
  description: string;
}

export interface ConfigPayload {
  diarization_model: string;
  selected_transcription_model: string;
  selected_gpt_model: string;
  features: Feature[];
  parameters: Parameter[];
}

export interface AnalysisMode {
  mode: 'real-time' | 'job';
  title: string;
  description: string;
  icon: string;
}

export interface AnalysisParameters {
  selectedFeatures: string[];
  exportParameters: string[];
  audioDuration: number;
  diarizationModel: string;
  transcriptionModel: string;
  gptModel: string;
}

export interface Transcript {
  speaker: string;
  role: string;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionUpdatePayload {
  transcription: Transcript[];
}

export interface Feature {
  name: string;
  checked: boolean;
  description: string;
}

export interface Parameter {
  name: string;
  checked: boolean;
  description: string;
}

export interface ConfigPayload {
  diarization_model: string;
  selected_transcription_model: string;
  selected_gpt_model: string;
  features: Feature[];
  parameters: Parameter[];
}

export interface Doctor {
  _id: string;
  name: string;
  surname: string;
  email: string;
}

export interface PatientSelect {
  _id: string;
  name: string;
  surname: string;
  age: string;
}

export interface RegistrationSelect {
  filename: string;
  upload_id: string;
}

@Injectable({ providedIn: 'root' })
export class BeanSupport {}
