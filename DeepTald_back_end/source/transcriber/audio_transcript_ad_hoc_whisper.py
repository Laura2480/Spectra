import torch
import torchaudio
from torch.cuda import empty_cache
from gc import collect
from pyannote.audio import Pipeline
from pydub import AudioSegment
from transformers import WhisperForConditionalGeneration, WhisperTokenizer
from speechbrain.inference import SpeakerRecognition
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from decimal import Decimal
import whisper
model_size = 'medium' #@param ['tiny', 'base', 'small', 'medium', 'large']
model_name = model_size


# Carica il modello di trascrizione 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def pad_audio(audio_input, target_length):
    # Pad audio with zeros if it is too short
    padding_size = target_length - audio_input.size(-1)
    if padding_size > 0:
        audio_input = torch.nn.functional.pad(audio_input, (0, padding_size))
    return audio_input

# Funzione per trascrivere l'audio
def transcribe(model, audio_segment):
    #Eseguo la trascrizione del file audio utilizzando il modello caricato
    transcription = model.transcribe(audio_segment, word_timestamps = 'true', language = "it")
    return transcription

# Funzione principale per la diarizzazione e trascrizione
def diarize_and_transcribe(file_path, token):
    # Diarizza l'audio
    # Carica la pipeline di diarizzazione preaddestrata (richiede token Hugging Face)
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    try:
        diarization = pipeline(file_path)
    finally:
        del pipeline
        empty_cache()
        collect()
    # Carica il file audio per segmentarlo
    audio = AudioSegment.from_wav(file_path)

    # Cicla sui segmenti della diarizzazione
    speaker_transcriptions = []
    try:
        model = whisper.load_model(model_size, device = device)

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_time = turn.start * 1000  # Converti in millisecondi
            end_time = turn.end * 1000  # Converti in millisecondi

            # Estrarre segmento di parlato
            audio_chunk = audio[start_time:end_time]

            # Salva temporaneamente il file del segmento
            temp_file = "temp_chunk.wav"
            audio_chunk.export(temp_file, format="wav")
    
            # Trascrivi il segmento (corrisponde ad un intera frase)
            transcription = transcribe(model, temp_file)
            print(transcription,"\n")
            # Sostituisci le etichette degli speaker
            if speaker == "SPEAKER_01":
                speaker = "CLINICIAN"
            elif speaker == "SPEAKER_00":
                speaker = "PATIENT"
            #mi prendo le words
            words=[]
            for segment in transcription['segments']:
                for word in segment['words']:
                    words.append(word)
            #print('words presenti: ', words)
            # Aggiungi la trascrizione per lo speaker corrente
            if not len(transcription['segments']) == 0: 
                speaker_transcriptions.append({
                    'speaker' : speaker,
                    'transcription': transcription['text'],
                    'start_time': turn.start,
                    'end_time': turn.end,
                    'words': words
                })
    except Exception as e:
        print(e)
    finally:
        del model
        empty_cache()
        collect()
    speaker_transcriptions.sort(key=lambda x: x['start_time'])
    return speaker_transcriptions

def diarize_better(file_path):
    try:
        # Caricare il modello pre-addestrato per il riconoscimento dei parlanti
        recognizer = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-xvect-voxceleb", use_auth_token=True)
    

        signal, fs = torchaudio.load(file_path)
        signal = signal.squeeze(0)  # Convertire da (1, num_samples) a (num_samples)

        target_fs = 16000
        if fs != target_fs:
            resampler = torchaudio.transforms.Resample(orig_freq=fs, new_freq=target_fs)
            signal = resampler(signal)
            fs = target_fs  # Aggiorna la frequenza di campionamento

        # Imposta una finestra di 1 secondi (puoi regolare questo parametro in base all'audio)
        window_size = int(1 * fs)

        # Creare i segmenti di audio
        segments = []
        for start in range(0, len(signal), window_size):
            end = min(start + window_size, len(signal))
            segments.append(signal[start:end])

        # Estrazione degli embedding per ogni segmento
        if not segments:  # Controlla se segments è vuoto
            raise ValueError("La lista 'segments' è vuota o non valida!")
        embeddings = []
        for segment in segments:
            if segment is None:  # Aggiungi un controllo per segmenti non validi
                raise ValueError("Trovato un segmento non valido!")
            segment = segment.unsqueeze(0)
            with torch.no_grad():
                embedding = recognizer.encode_batch(segment)
                embeddings.append(embedding.squeeze().cpu().numpy())

        # Convertire gli embedding in un array numpy
        embeddings = np.vstack(embeddings)

        # Applicare il clustering sugli embedding
        n_speakers = 2  # Numero di parlanti atteso (modifica questo valore se necessario)
        clustering = AgglomerativeClustering(n_clusters=n_speakers).fit(embeddings)
    finally:
        del recognizer
        empty_cache()
        collect()

    return clustering

def transcribe_audio(file_path, token):
    #mi restituisce un oggetto contentente: speaker, trascrizione, inizio e fine ma con speaker non affidabile
    
    result = diarize_and_transcribe(file_path, token)
    
    #mi restituisce la classificazione
    clustering =diarize_better(file_path)
    
    signal, fs = torchaudio.load(file_path)
    signal = signal.squeeze(0)  # Convertire da (1, num_samples) a (num_samples)

    target_fs = 16000
    if fs != target_fs:
        resampler = torchaudio.transforms.Resample(orig_freq=fs, new_freq=target_fs)
        signal = resampler(signal)
        fs = target_fs  # Aggiorna la frequenza di campionamento
    
    #Creo un oggetto contenente Speaker, stat_time ed end_time
    window_size = int(1 * fs)
    speaker_diarization = []
    for i, label in enumerate(clustering.labels_):
        start_time = i * (window_size) / fs
        end_time = (i * (window_size) + window_size) / fs
        speaker_diarization.append({
            'speaker' : label,
            'start_time': start_time,
            'end_time': end_time
        })
        #print(f"Segmento {i}: {start_time:.2f}s - {end_time:.2f}s -> Speaker {label}")
    
    #Associazione dei risultati
    corpus=[]
    for segment in result:
        frase =[]
        int_start = int(segment['start_time'])
        int_end = int(segment['end_time'])
        float_start = float(segment['start_time'])
        float_end = float(segment['end_time'])
        
        i = int_start-1
        j = int_end+1
        #print(f"i: {i}\tj: {j}\tint start: {int_start}\tint end: {int_end}\tfloat start: {float_start}\tfloat end: {float_end}")
        labels=[]
        for k in range(i,j+1):
            if(k < len(clustering.labels_)):
                label = clustering.labels_[k]
                labels.append(label)
           
        #print("labels for segment:",segment['transcription'], ": ",labels)
        if(len(set(labels)) == 1): 
            if(labels[0] ==1):
                #print("Solo label dello Speaker 1\n")
                outputSegment ={
                    'speaker':'PATIENT',
                    'text':segment['transcription'],
                    'start':segment['start_time'],
                    'end':segment['end_time'],
                    'words': [{**word, 'speaker' : 'PATIENT'} for word in segment['words']]
                }
                corpus.append(outputSegment)
            else:
                #print("Solo label dello Speaker 1\n")
                outputSegment ={
                    'speaker':'CLINICIAN',
                    'text':segment['transcription'],
                    'start':segment['start_time'],
                    'end':segment['end_time'],
                    'words': [{**word, 'speaker' : 'CLINICIAN'} for word in segment['words']]
                }
                corpus.append(outputSegment)
        else:
            count_ones = labels.count(1)
            count_zeros = len(labels) - count_ones
            if(count_ones>count_zeros):
                #print("Maggioranza label dello Speaker 2\n")
                outputSegment ={
                'speaker':'PATIENT',
                'text':segment['transcription'],
                'start':segment['start_time'],
                'end':segment['end_time'],
                'words': [{**word, 'speaker' : 'PATIENT'} for word in segment['words']]
                }
                corpus.append(outputSegment)
            elif(count_zeros>count_ones):
                #print("Maggioranza label dello Speaker 1\n")
                outputSegment ={
                'speaker':'CLINICIAN',
                'text':segment['transcription'],
                'start':segment['start_time'],
                'end':segment['end_time'],
                'words': [{**word, 'speaker' : 'CLINICIAN'} for word in segment['words']]
                }
                corpus.append(outputSegment)
            else:
                elapsed_zero=0
                elapsed_one=0
                tot = 0.0
                for label in labels:
                    start_i = i
                    end_i = i+1
                    #print("start_i: ", start_i,"\tend_i: ", end_i)
                    if(float_start > start_i ):
                        tot = end_i-float_start
                        #print("La frase è alla fine del segmento con un totale di: ", tot)
                    if(start_i> float_start and end_i<float_end):
                        tot = 1
                        #print("La frase è all'interno del segmento con un totale di: ", tot)
                    if(float_end>start_i and float_end<end_i):
                        tot = end_i-float_end
                        #print("La frase è all'inizio segmento con un totale di: ", tot)
                    if(label==0):
                        elapsed_zero=elapsed_zero+tot
                    else:
                        elapsed_one=elapsed_one+tot
                    #print("elapsed 0: ", elapsed_zero,"\telapsed 1: ", elapsed_one)
                    i=i+1
                if(elapsed_one>elapsed_zero):
                    outputSegment ={
                    'speaker':'PATIENT',
                    'text':segment['transcription'],
                    'start':segment['start_time'],
                    'end':segment['end_time'],
                    'words': [{**word, 'speaker' : 'PATIENT'} for word in segment['words']]
                    }
                    corpus.append(outputSegment) 
                else:
                    outputSegment ={
                    'speaker':'CLINICIAN',
                    'text':segment['transcription'],
                    'start':segment['start_time'],
                    'end':segment['end_time'],
                    'words': [{**word, 'speaker' : 'CLINICIAN'} for word in segment['words']]
                    }
                    corpus.append(outputSegment)

    ''' for x in corpus:
        print(x)'''
    return corpus