from os.path import isfile
from torch.cuda import is_available,empty_cache
from pathlib import Path
from itertools import groupby
import whisper
from pyannote.audio import Audio
from pyannote.audio import Pipeline
from pyannote.core import Segment, Annotation
from datetime import timedelta

num_speakers = 2 #@param {type:"integer"}
language = 'any' #@param ['any', 'English']
model_size = 'medium' #@param ['tiny', 'base', 'small', 'medium', 'large']
model_name = model_size
if language == 'English' and model_size != 'large':
  model_name += '.en'

def _get_closest_segment(diary:Annotation, target_segment:Segment):
    closest_segment = None
    min_distance = float('inf')

    for segment in diary.itersegments():
        distance = distance = min(
            abs(target_segment.start - segment.end),
            abs(target_segment.end - segment.start),
            abs(target_segment.start - segment.start),
            abs(target_segment.end - segment.end)
        )

        if distance < min_distance:
            min_distance = distance
            closest_segment = segment

    return diary.crop(closest_segment).argmax()

def _assign_speaker(diary:Annotation, segment:Segment):
  speaker = diary.crop(segment).argmax()
  return speaker if speaker is not None else _get_closest_segment(diary, segment)

def transcribe_audio(path, token):
  if not (isfile(path) and Path(path).suffix == ".wav"): raise Exception("Given path does not lead to a wav audio file!")
  device = "cuda" if is_available() else "cpu"

  try:
      pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)
      diary: Annotation = pipeline(path, num_speakers=2)
  finally:
      empty_cache()

  #Eseguo la pipeline per la diarization
  #diary:Annotation = pipeline(path, num_speakers=2)
  
  #Mappa gli speaker
  first_speaker = next(diary.itertracks(yield_label=True))[-1]
  label_mapping = {"SPEAKER_00" : "CLINICIAN", "SPEAKER_01" : "PATIENT"} if first_speaker == "SPEAKER_00" else \
                  {"SPEAKER_00" : "PATIENT", "SPEAKER_01" : "CLINICIAN"}
  diary = diary.rename_labels(label_mapping)

  #effettua il transcribing su tutte il file audio e combinalo con le informazioni di diarization
  #result = model.transcribe(path, word_timestamps = 'true', language = "it")
  try:
      model = whisper.load_model(model_size, device=device)
      result = model.transcribe(path, word_timestamps='true', language="it")
  finally:
      empty_cache()

  segments = [
    {**segment_data, 
     "speaker": _assign_speaker(diary, Segment(segment_data["start"], segment_data["end"])), 
     "words": [{**word, "speaker":  _assign_speaker(diary, Segment(word["start"], word["end"]))} 
               for word in segment_data["words"]]
    } 
    for segment_data in result["segments"]
  ]

  return segments

####### TEST WITH MAIN #######

import json

if __name__ == "__main__":
  try:
    transcription,duration,result,word_count,n_words_doctor,n_words_patient = transcribe_audio("./AudioTest/DeFilippisTagliato_WNoise_Test.wav")
    
    with open('results/result.json', 'w') as fp:
      json.dump(transcription, fp)
    
    transcription_feed = [(segment["speaker"], timedelta(seconds=round(segment["start"])),  \
                           timedelta(seconds=round(segment["end"])), segment["text"]) for segment in transcription]

    with open('results/transcription-original.txt', 'w', encoding="utf-8") as file:
        for speaker, start, end, text in transcription_feed:
            file.write(f"{speaker} {start} {end}\n")
            file.write(f"{text.strip()}\n")
  except Exception as e:
    print(e)