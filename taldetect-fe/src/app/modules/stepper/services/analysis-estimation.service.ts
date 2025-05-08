import { Injectable } from '@angular/core';
import { AnalysisParameters } from '../../../core/utils/BeanSupport';

@Injectable({
  providedIn: 'root',
})
export class AnalysisEstimationService {
  private featureExtractionTimes: { [feature: string]: number } = {
    'Durata degli interventi': 0.05,
    'Frequenza degli interventi': 0.02,
    'Tempo medio intervento': 0.02,
    'Pausa tra interventi': 0.03,
    'Sovrapposizione del parlato': 0.01,
    'Emozioni nel parlato': 0.02,
    'Variazione della prosodia': 0.01,
    'Tempo di risposta': 0.04,
    'Pausa intra-parlato': 0.04,
    'Lunghezza media delle frasi': 0.03,
    'Ripetizione e ecolalia': 0.02,
    'Complessità sintattica': 0.01,
    'Velocità del parlato (Speech Rate)': 0.03,
    'Articolazione e pronuncia': 0.03,
    'Intonazione e stress vocale': 0.04,
    'Analisi dello spettrogramma': 0.04,
    'Disfluenze (Um, Eh, Ripetizioni)': 0.05,
    'Coordinazione del turn-taking (dinamica conversazionale)': 0.03,
    'Modulazione dell’energia vocale': 0.06,
    'Tempo di latenza nei dialoghi multipli': 0.07,
    'Analisi delle armoniche (HNR - Harmonics-to-Noise Ratio)': 0.03,
    'Tempo di latenza intra-turno': 0.04,
    'Complessità fonetica': 0.06,
    'Frequenza delle parole funzionali': 0.08,
    'Misura della prevedibilità (Entropia del parlato)': 0.08,
  };

  private modelTimes: { [model: string]: number } = {
    pyannote: 1.2,
    tiny: 0.5,
    'tiny.en': 0.5,
    base: 1,
    'base.en': 1,
    small: 1.5,
    'small.en': 1.5,
    medium: 2,
    'medium.en': 2,
    large: 3,
    'large-v1': 3,
    'large-v2': 3.2,
    'large-v3': 3.5,
    'large-v3-turbo': 3.8,
    turbo: 4,
    'Mixtral-8x7B-v0.1': 5,
    'Falcon3-7B-Base': 4,
    'Llama-2-70b-chat-hf': 6,
  };

  private modelAccuracies: { [model: string]: number } = {
    pyannote: 87.8, // in media su audio di test puliti
    tiny: 60,
    'tiny.en': 60,
    base: 70,
    'base.en': 70,
    small: 80,
    'small.en': 80,
    medium: 85,
    'medium.en': 85,
    large: 90,
    'large-v1': 90,
    'large-v2': 92,
    'large-v3': 93,
    'large-v3-turbo': 94,
    turbo: 95,
    'Mixtral-8x7B-v0.1': 95,
    'Falcon3-7B-Base': 85,
    'Llama-2-70b-chat-hf': 96,
  };

  constructor() {}

  estimateAnalysisTimeAndAccuracy(params: AnalysisParameters): {
    time: number;
    accuracy: number;
  } {
    let totalFeatureTime = 0;
    for (const feature of params.selectedFeatures) {
      const t = this.featureExtractionTimes[feature];
      if (t !== undefined) {
        totalFeatureTime += t * params.audioDuration;
      }
    }

    const exportTime = params.exportParameters.length * 1;

    let totalModelTime = 0;
    if (params.diarizationModel && this.modelTimes[params.diarizationModel]) {
      totalModelTime += this.modelTimes[params.diarizationModel];
    }
    if (
      params.transcriptionModel &&
      this.modelTimes[params.transcriptionModel]
    ) {
      totalModelTime += this.modelTimes[params.transcriptionModel];
    }
    if (params.gptModel && this.modelTimes[params.gptModel]) {
      totalModelTime += this.modelTimes[params.gptModel];
    }

    /*Tempo stimato totale (in secondi)*/
    const totalTime = totalFeatureTime + exportTime + totalModelTime;

    const featureFactor = params.selectedFeatures.length / 25;
    let modelAccuracySum = 0,
      modelCount = 0;
    let modelFactor = 0;

    if (
      params.diarizationModel &&
      this.modelAccuracies[params.diarizationModel]
    ) {
      modelAccuracySum += this.modelAccuracies[params.diarizationModel];
      modelCount++;
    }
    if (
      params.transcriptionModel &&
      this.modelAccuracies[params.transcriptionModel]
    ) {
      modelAccuracySum += this.modelAccuracies[params.transcriptionModel];
      modelCount++;
    }
    if (params.gptModel && this.modelAccuracies[params.gptModel]) {
      modelAccuracySum += this.modelAccuracies[params.gptModel];
      modelCount++;
    }

    if (modelCount > 0) {
      modelFactor = modelAccuracySum / modelCount;
    }

    let totalAccuracy = featureFactor + modelFactor;
    totalAccuracy = Math.min(100, totalAccuracy);

    return { time: totalTime, accuracy: totalAccuracy };
  }
}
