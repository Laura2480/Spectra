import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { BehaviorSubject } from 'rxjs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ALL_FEATURES, ALL_PARAMETERS } from '../../../../core/constants/default';
import { Model } from '../../../../core/utils/BeanSupport';



@Component({
  selector: 'app-pre-processing',
  standalone: true,
  imports: [CommonModule, FormsModule, MatInputModule, MatSelectModule, MatFormFieldModule, MatCheckboxModule, MatTooltipModule, MatIconModule, TranslateModule],
  templateUrl: './pre-processing.component.html',
  styleUrl: './pre-processing.component.scss'
})
export class PreProcessingComponent {
  private isValidSubject = new BehaviorSubject<boolean>(true);
  isValid$ = this.isValidSubject.asObservable();
  @Output() changedStep: EventEmitter<number> = new EventEmitter<number>();

  diarizationModels: Model[] = [{ name: 'pyannote/speaker-diarization-3.1', value: 'pyannote/speaker-diarization-3.1' }];
  transcriptionModels: Model[] = [
    { name: 'whisper/tiny', value: 'tiny' },
    { name: 'whisper/tiny.en', value: 'tiny.en' },
    { name: 'whisper/base', value: 'base' },
    { name: 'whisper/base.en', value: 'base.en' },
    { name: 'whisper/small', value: 'small' },
    { name: 'whisper/small.en', value: 'small.en' },
    { name: 'whisper/medium', value: 'medium' },
    { name: 'whisper/medium.en', value: 'medium.en' },
    { name: 'whisper/large', value: 'large' },
    { name: 'whisper/large-v1', value: 'large-v1' },
    { name: 'whisper/large-v2', value: 'large-v2' },
    { name: 'whisper/large-v3', value: 'large-v3' },
    { name: 'whisper/large-v3-turbo', value: 'large-v3-turbo' },
    { name: 'whisper/turbo', value: 'turbo' }
  ];
  gptModels: Model[] = [
    { name: 'Mixtral-8x7B-v0.1', value: 'Mixtral-8x7B-v0.1' },
    // { name: 'Falcon3-7B-Base', value: 'Falcon3-7B-Base' },
    // { name: 'Llama-2-70b-chat-hf', value: 'Llama-2-70b-chat-hf' }
  ];

  selectedDiarizationModel: string = this.diarizationModels[0].value;
  selectedTranscriptionModel: string = this.transcriptionModels[this.transcriptionModels.length - 4].value;
  selectedGptModel: string = this.gptModels[0].value;
  selectAllFeatures: boolean = true;
  selectAllParameters: boolean = true;

  features = ALL_FEATURES;

  parameters = ALL_PARAMETERS;

  constructor(private translate: TranslateService) {
    this.translate.get([
      'stepper.configuration.features.speech_duration.name', 'stepper.configuration.features.speech_duration.description',
      'stepper.configuration.features.speech_frequency.name', 'stepper.configuration.features.speech_frequency.description',
      'stepper.configuration.features.pause_between_turns.name', 'stepper.configuration.features.pause_between_turns.description',
      'stepper.configuration.features.speech_overlap.name', 'stepper.configuration.features.speech_overlap.description',
      'stepper.configuration.features.speech_emotions.name', 'stepper.configuration.features.speech_emotions.description',
      'stepper.configuration.features.prosody_variation.name', 'stepper.configuration.features.prosody_variation.description',
      'stepper.configuration.features.response_time.name', 'stepper.configuration.features.response_time.description',
      'stepper.configuration.features.avg_sentence_length.name', 'stepper.configuration.features.avg_sentence_length.description',
      'stepper.configuration.features.echolalia_repetition.name', 'stepper.configuration.features.echolalia_repetition.description',
      'stepper.configuration.features.syntactic_complexity.name', 'stepper.configuration.features.syntactic_complexity.description',
      'stepper.configuration.features.speech_rate.name', 'stepper.configuration.features.speech_rate.description',
      'stepper.configuration.features.articulation_pronunciation.name', 'stepper.configuration.features.articulation_pronunciation.description',
      'stepper.configuration.features.pitch_stress.name', 'stepper.configuration.features.pitch_stress.description',
      'stepper.configuration.features.disfluencies.name', 'stepper.configuration.features.disfluencies.description',
      'stepper.configuration.features.turn_taking_coordination.name', 'stepper.configuration.features.turn_taking_coordination.description',
      'stepper.configuration.features.vocal_energy_modulation.name', 'stepper.configuration.features.vocal_energy_modulation.description',
      'stepper.configuration.features.harmonics_to_noise_ratio.name', 'stepper.configuration.features.harmonics_to_noise_ratio.description',
      'stepper.configuration.features.intra_turn_latency.name', 'stepper.configuration.features.intra_turn_latency.description',
      'stepper.configuration.features.functional_word_frequency.name', 'stepper.configuration.features.functional_word_frequency.description',
      'stepper.configuration.features.speech_entropy.name', 'stepper.configuration.features.speech_entropy.description',
      'stepper.configuration.parameters.total_tald.name', 'stepper.configuration.parameters.total_tald.description',
      'stepper.configuration.parameters.circumstantiality.name', 'stepper.configuration.parameters.circumstantiality.description',
      'stepper.configuration.parameters.derailment.name', 'stepper.configuration.parameters.derailment.description',
      'stepper.configuration.parameters.tangentiality.name', 'stepper.configuration.parameters.tangentiality.description',
      'stepper.configuration.parameters.thought_disassociation.name', 'stepper.configuration.parameters.thought_disassociation.description',
      'stepper.configuration.parameters.crosstalk.name', 'stepper.configuration.parameters.crosstalk.description',
      'stepper.configuration.parameters.perseveration.name', 'stepper.configuration.parameters.perseveration.description',
      'stepper.configuration.parameters.verbigeration.name', 'stepper.configuration.parameters.verbigeration.description',
      'stepper.configuration.parameters.thought_break.name', 'stepper.configuration.parameters.thought_break.description',
      'stepper.configuration.parameters.pressure_speech.name', 'stepper.configuration.parameters.pressure_speech.description',
      'stepper.configuration.parameters.logorrhea.name', 'stepper.configuration.parameters.logorrhea.description',
      'stepper.configuration.parameters.mannered_speech.name', 'stepper.configuration.parameters.mannered_speech.description',
      'stepper.configuration.parameters.semantic_paraphasia.name', 'stepper.configuration.parameters.semantic_paraphasia.description',
      'stepper.configuration.parameters.phonemic_paraphasia.name', 'stepper.configuration.parameters.phonemic_paraphasia.description',
      'stepper.configuration.parameters.neologisms.name', 'stepper.configuration.parameters.neologisms.description',
      'stepper.configuration.parameters.clanging.name', 'stepper.configuration.parameters.clanging.description',
      'stepper.configuration.parameters.echolalia.name', 'stepper.configuration.parameters.echolalia.description',
      'stepper.configuration.parameters.speech_content_poverty.name', 'stepper.configuration.parameters.speech_content_poverty.description',
      'stepper.configuration.parameters.restricted_thought.name', 'stepper.configuration.parameters.restricted_thought.description',
      'stepper.configuration.parameters.slowed_thought.name', 'stepper.configuration.parameters.slowed_thought.description',
      'stepper.configuration.parameters.speech_poverty.name', 'stepper.configuration.parameters.speech_poverty.description',
      'stepper.configuration.parameters.concretism.name', 'stepper.configuration.parameters.concretism.description',
      'stepper.configuration.parameters.blocks.name', 'stepper.configuration.parameters.blocks.description',
      'stepper.configuration.parameters.rumination.name', 'stepper.configuration.parameters.rumination.description',
      'stepper.configuration.parameters.thought_poverty.name', 'stepper.configuration.parameters.thought_poverty.description',
      'stepper.configuration.parameters.thought_inhibition.name', 'stepper.configuration.parameters.thought_inhibition.description',
      'stepper.configuration.parameters.receptive_language_dysfunction.name', 'stepper.configuration.parameters.receptive_language_dysfunction.description',
      'stepper.configuration.parameters.expressive_language_dysfunction.name', 'stepper.configuration.parameters.expressive_language_dysfunction.description',
      'stepper.configuration.parameters.thought_initiative_intention_dysfunction.name', 'stepper.configuration.parameters.thought_initiative_intention_dysfunction.description',
      'stepper.configuration.parameters.thought_interference.name', 'stepper.configuration.parameters.thought_interference.description',
      'stepper.configuration.parameters.thought_pressure.name', 'stepper.configuration.parameters.thought_pressure.description',

    ]).subscribe(translations => {
      this.parameters = [
        { name: translations['stepper.configuration.parameters.total_tald.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.total_tald.description'] },
        { name: translations['stepper.configuration.parameters.circumstantiality.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.circumstantiality.description'] },
        { name: translations['stepper.configuration.parameters.derailment.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.derailment.description'] },
        { name: translations['stepper.configuration.parameters.tangentiality.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.tangentiality.description'] },
        { name: translations['stepper.configuration.parameters.thought_disassociation.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_disassociation.description'] },
        { name: translations['stepper.configuration.parameters.crosstalk.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.crosstalk.description'] },
        { name: translations['stepper.configuration.parameters.perseveration.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.perseveration.description'] },
        { name: translations['stepper.configuration.parameters.verbigeration.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.verbigeration.description'] },
        { name: translations['stepper.configuration.parameters.thought_break.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_break.description'] },
        { name: translations['stepper.configuration.parameters.pressure_speech.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.pressure_speech.description'] },
        { name: translations['stepper.configuration.parameters.logorrhea.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.logorrhea.description'] },
        { name: translations['stepper.configuration.parameters.mannered_speech.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.mannered_speech.description'] },
        { name: translations['stepper.configuration.parameters.semantic_paraphasia.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.semantic_paraphasia.description'] },
        { name: translations['stepper.configuration.parameters.phonemic_paraphasia.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.phonemic_paraphasia.description'] },
        { name: translations['stepper.configuration.parameters.neologisms.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.neologisms.description'] },
        { name: translations['stepper.configuration.parameters.clanging.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.clanging.description'] },
        { name: translations['stepper.configuration.parameters.echolalia.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.echolalia.description'] },
        { name: translations['stepper.configuration.parameters.speech_content_poverty.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.speech_content_poverty.description'] },
        { name: translations['stepper.configuration.parameters.restricted_thought.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.restricted_thought.description'] },
        { name: translations['stepper.configuration.parameters.slowed_thought.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.slowed_thought.description'] },
        { name: translations['stepper.configuration.parameters.speech_poverty.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.speech_poverty.description'] },
        { name: translations['stepper.configuration.parameters.concretism.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.concretism.description'] },
        { name: translations['stepper.configuration.parameters.blocks.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.blocks.description'] },
        { name: translations['stepper.configuration.parameters.rumination.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.rumination.description'] },
        { name: translations['stepper.configuration.parameters.thought_poverty.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_poverty.description'] },
        { name: translations['stepper.configuration.parameters.thought_inhibition.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_inhibition.description'] },
        { name: translations['stepper.configuration.parameters.receptive_language_dysfunction.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.receptive_language_dysfunction.description'] },
        { name: translations['stepper.configuration.parameters.expressive_language_dysfunction.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.expressive_language_dysfunction.description'] },
        { name: translations['stepper.configuration.parameters.thought_initiative_intention_dysfunction.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_initiative_intention_dysfunction.description'] },
        { name: translations['stepper.configuration.parameters.thought_interference.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_interference.description'] },
        { name: translations['stepper.configuration.parameters.thought_pressure.name'], scale:[1,5], checked: true, description: translations['stepper.configuration.parameters.thought_pressure.description'] },
      ];

      this.features = [
        { key: 'durata_interventi', name: translations['stepper.configuration.features.speech_duration.name'], checked: true, description: translations['stepper.configuration.features.speech_duration.description'] },
        { key: 'frequenza_interventi', name: translations['stepper.configuration.features.speech_frequency.name'], checked: true, description: translations['stepper.configuration.features.speech_frequency.description'] },
        { key: 'pausa_tra_interventi', name: translations['stepper.configuration.features.pause_between_turns.name'], checked: true, description: translations['stepper.configuration.features.pause_between_turns.description'] },
        { key: 'sovrapposizione_parlato', name: translations['stepper.configuration.features.speech_overlap.name'], checked: true, description: translations['stepper.configuration.features.speech_overlap.description'] },
        { key: 'emozioni_parlato', name: translations['stepper.configuration.features.speech_emotions.name'], checked: true, description: translations['stepper.configuration.features.speech_emotions.description'] },
        { key: 'variazione_prosodia', name: translations['stepper.configuration.features.prosody_variation.name'], checked: true, description: translations['stepper.configuration.features.prosody_variation.description'] },
        { key: 'tempo_risposta', name: translations['stepper.configuration.features.response_time.name'], checked: true, description: translations['stepper.configuration.features.response_time.description'] },
        { key: 'lunghezza_media_frasi', name: translations['stepper.configuration.features.avg_sentence_length.name'], checked: true, description: translations['stepper.configuration.features.avg_sentence_length.description'] },
        { key: 'ripetizione_ecolalia', name: translations['stepper.configuration.features.echolalia_repetition.name'], checked: true, description: translations['stepper.configuration.features.echolalia_repetition.description'] },
        { key: 'complessita_sintattica', name: translations['stepper.configuration.features.syntactic_complexity.name'], checked: true, description: translations['stepper.configuration.features.syntactic_complexity.description'] },
        { key: 'velocita_parlato', name: translations['stepper.configuration.features.speech_rate.name'], checked: true, description: translations['stepper.configuration.features.speech_rate.description'] },
        { key: 'articolazione_pronuncia', name: translations['stepper.configuration.features.articulation_pronunciation.name'], checked: true, description: translations['stepper.configuration.features.articulation_pronunciation.description'] },
        { key: 'intonazione_stress_vocale', name: translations['stepper.configuration.features.pitch_stress.name'], checked: true, description: translations['stepper.configuration.features.pitch_stress.description'] },
        { key: 'disfluenze', name: translations['stepper.configuration.features.disfluencies.name'], checked: true, description: translations['stepper.configuration.features.disfluencies.description'] },
        { key: 'coordinazione_turn_taking', name: translations['stepper.configuration.features.turn_taking_coordination.name'], checked: true, description: translations['stepper.configuration.features.turn_taking_coordination.description'] },
        { key: 'modulazione_energia_vocale', name: translations['stepper.configuration.features.vocal_energy_modulation.name'], checked: true, description: translations['stepper.configuration.features.vocal_energy_modulation.description'] },
        { key: 'analisi_armoniche_hnr', name: translations['stepper.configuration.features.harmonics_to_noise_ratio.name'], checked: true, description: translations['stepper.configuration.features.harmonics_to_noise_ratio.description'] },
        { key: 'tempo_latenza_intra_turno', name: translations['stepper.configuration.features.intra_turn_latency.name'], checked: true, description: translations['stepper.configuration.features.intra_turn_latency.description'] },
        { key: 'frequenza_parole_funzionali', name: translations['stepper.configuration.features.functional_word_frequency.name'], checked: true, description: translations['stepper.configuration.features.functional_word_frequency.description'] },
        { key: 'prevedibilita_entropia_parlato', name: translations['stepper.configuration.features.speech_entropy.name'], checked: true, description: translations['stepper.configuration.features.speech_entropy.description'] },
      ];
    });
  }

  ngOnInit(): void {
    this.checkValidity();
  }

  checkValidity(): void {
    const isValidFeatures = this.features.some(f => f.checked);
    const isValidParameters = this.parameters.some(p => p.checked);
    if (!isValidFeatures) {
      this.selectAllFeatures = false;
    }
    if (!isValidParameters) {
      this.selectAllParameters = false;
    }
    this.isValidSubject.next(isValidFeatures && isValidParameters);
  }

  onChangeView(): void {
    this.changedStep.emit(0);
    this.checkValidity();
  }

  selectAllFeaturesChanged() {
    this.features.forEach(f => f.checked = this.selectAllFeatures);
  }

  selectAllParametersChanged() {
    this.parameters.forEach(p => p.checked = this.selectAllParameters);
  }


  getPreProcessingData() {
    const selectedFeatures = this.features.filter(f => f.checked).map(f => f.name);
    const selectedParameters = this.parameters.filter(p => p.checked).map(p => p.name);
    return {
      selectedFeatures: selectedFeatures,
      exportParameters: selectedParameters,
      diarizationModel: this.selectedDiarizationModel,
      transcriptionModel: this.selectedTranscriptionModel,
      gptModel: this.selectedGptModel
    };
  }

}
