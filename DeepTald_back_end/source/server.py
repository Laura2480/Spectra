from itertools import groupby
import re
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask import Flask, make_response, request, jsonify, render_template 
from copy import deepcopy
from flask_cors import CORS
from inflection import underscore
from transcriber.audio_transcript import transcribe_audio as vincent_pipeline
from transcriber.audio_transcript_ad_hoc_whisper import transcribe_audio as sara_pipeline
from scale_items import Strategy
from os.path import join, exists
from pathlib import Path
from dotenv import dotenv_values
from json import loads, load, dump

app = Flask(__name__, template_folder="../templates")
CORS(app)

env = dotenv_values()
strategies = {}

################################ UTILITIES ###################################

def generate_hbar_plot(plot_data:dict):
    # Valori da visualizzare nel grafico
    if not "labels" in plot_data: raise Exception("labels not specified")
    if not "values" in plot_data: raise Exception("values not specified")
    if not "colors" in plot_data: raise Exception("colors not specified")

    labels, values, colors = plot_data['labels'], plot_data['values'], plot_data['colors']
    if not(len(labels) == len(values) == len(colors)): raise Exception("malformed plot") 
    
    xlabel, title = plot_data.get("xlabel", ""), plot_data.get("title", "")
    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(labels, values, color=colors)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    fig.tight_layout()

    # Save the figure to a BytesIO object as a PNG
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)  # Close the figure to free resources

    # Encode the PNG image to base64
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()

    return base64_image
############################ THRESHOLDS ENDPOINTS ############################

@app.route("/api/thresholds", methods = ["GET"])
def initialize(): 
    strategies_schemas = {}
    for name, instance in strategies.items():
        dict_obj:dict = {key : value for key, value in instance.__dict__.items()}
        dict_obj.pop('schema')

        strategies_schemas[name] = dict_obj
    
    return jsonify(strategies_schemas)

@app.route("/api/thresholds/<item>", methods = ["POST"] )
def modify_threshold(item):
    if item is None: return make_response(jsonify({'message' : 'Item della scala non è stato specificato'}), 400)
   
    try:
        strategy:Strategy = strategies[item]
        json = request.get_json()
        thresholds = json[item]["thresholds"]
        weights = json[item]["weights"]

        strategy.setValues(weights, thresholds)
        with open(env["METRICS_THRESHOLDS"], "r") as file: schema = load(file)
        
        schema[item]["thresholds"] = thresholds
        schema[item]["weights"] = weights

        with open(env["METRICS_THRESHOLDS"], "w") as file: dump(schema, file, indent=5)
    except ValueError as e:
        error_message = e.args[0]
        match = re.search(r"'(weights|thresholds)': \['(.*?)'\]", error_message)
        specific_message = match.group(2)  if match else "thresholds or weights have not been set correctly!"
        return make_response(jsonify({'message' : specific_message}), 400)
    except KeyError as key:
        return make_response(jsonify({'message' : 'strategia non è modificabile'}), 400)
    return jsonify({'message' : f"threshold e pesi per {item} sono stati modificati"})

@app.route("/api/thresholds", methods = ["POST"] )
def modify_thresholds():
    if (items := request.json["items"]) is None: return make_response(jsonify({'message' : 'Items della scala non sono stati specificati'}), 400)
   
    global strategies
    cache = deepcopy(strategies)

    for item, value in items.items():
        try:
            strategy:Strategy = strategies[item]
            thresholds = value["thresholds"]
            weights = value["weights"]

            strategy.setValues(weights, thresholds)
            with open(env["METRICS_THRESHOLDS"], "w") as file: dump(thresholds, file, indent=5)
        except ValueError:
            print(e)
            strategies = cache
            return make_response(jsonify({'message' : 'Pesi o soglie passati non sono corretti'}), 400)
        except KeyError as e:
            print(e)
            strategies = cache
            return make_response(jsonify({'message' : f'Pesi o soglie non sono quelli definiti per {item}'}), 400)
        
    return jsonify({'message' : "thresholds sono stati modificati"})

############################ RECORDING ENDPOINTS ############################

@app.route("/api/recording", methods=["PUT"])
def upload_file():
    # Verifica se il file è stato effettivamente caricato
    if not (file := request.files.get('audio_file')) : return make_response(jsonify({'message' : 'Nessun file audio caricato'}), 400)
    if (filename := file.filename) == '': return make_response(jsonify({'message' : 'Nessun file selezionato'}), 400)
    
    # Salva il file audio
    file.save(join(env['RECORDINGS_FOLDER'], filename))
    return jsonify({'message': 'File audio caricato con successo'})

############################ TRANSCRIPTIONS ENDPOINTS ############################
def word_level_transcript(segments):
    words = [word for segment in segments for word in segment["words"]]
    segments = [
        {
            "words": (words := list(group)),
            "start": words[0]['start'],
            "end": words[-1]['end'],
            "text": ''.join([word['word'] for word in words]),
            "speaker": curr_speaker
        }
        for curr_speaker, group in groupby(words, key=lambda x: x["speaker"])
    ]

    return segments
#@app.route("/api/transcription/<filename>", methods=["POST"])
#def start_transcription(filename):
#    # Verifica se il parametro 'file_name' è presente nella richiesta
#    with open("data/transcriptions/DeFilippisTagliato_WNoise_Test.json", "r") as fp: segments = load(fp)
#
#    # Restituisci il risultato della trascrizione al frontend
#    return jsonify({'transcription': segments, 'message' : "Trascrizione completata"})

@app.route("/api/transcription/<filename>", methods=["POST"])
def start_transcription(filename):
    # # Verifica se il parametro 'file_name' è presente nella richiesta
    # if filename is None: return make_response(jsonify({'message' : 'Nome del file audio mancante'}), 400)
    #
    # # Recupera il file audio e avvia trascrizione
    # path_to_recording = join(env['RECORDINGS_FOLDER'], f'{Path(filename).stem}.wav')
    # path_to_transcription = join(env['TRANSCRIPTIONS_FOLDER'], f'{Path(filename).stem}.json')
    #
    #
    # if not exists(path_to_recording): return make_response(jsonify({'message' : 'Registrazione non è stata caricata'}), 400)
    # #if exists(path_to_transcription): return make_response(jsonify({'message' : 'La trascrizione è stata già creata'}), 400)
    #
    # # Esegui la trascrizione dell'audio con il nome del file fornito
    # data = request.get_json()
    # pipeline = data.get('pipeline') if data else None
    # token = env["HF_TOKEN"]
    #
    # if (not pipeline) or pipeline == "whisper_ad_hoc": segments = sara_pipeline(path_to_recording, token)
    # elif pipeline == "whisper_pyannote":  segments = vincent_pipeline(path_to_recording, token)
    # #se pipeline "whisper_ad_hoc" o per default esegue la pipeline di sara
    # with open(path_to_transcription, "w") as transcription_file: dump(segments, transcription_file)
    if filename is None: return make_response(jsonify({'message': 'Nome del file audio mancante'}), 400)

    # Recupera il file audio e avvia trascrizione
    path_to_recording = join(env['RECORDINGS_FOLDER'], f'{Path(filename).stem}.wav')
    path_to_transcription = join(env['TRANSCRIPTIONS_FOLDER'], f'{Path(filename).stem}.json')
    if not exists(path_to_recording): return make_response(jsonify({'message': 'Registrazione non è stata caricata'}),
                                                           400)
    # if exists(path_to_transcription): return make_response(jsonify({'message' : 'La trascrizione è stata già creata'}), 400)

    # Esegui la trascrizione dell'audio con il nome del file fornito
    data = request.get_json()
    pipeline = data.get('pipeline') if data else None
    word_level = data.get('word_level') if data else None
    token = env['HF_TOKEN']
    if (not pipeline) or pipeline == "whisper_ad_hoc":
        segments = sara_pipeline(path_to_recording, token)
    elif pipeline == "whisper_pyannote":
        segments = vincent_pipeline(path_to_recording, token)
    # se pipeline "whisper_ad_hoc" o per default esegue la pipeline di sara
    with open(path_to_transcription, "w") as transcription_file:
        dump(segments, transcription_file)
    segments = segments if not word_level else word_level_transcript(segments)
    # Restituisci il risultato della trascrizione al frontend
    return jsonify({'transcription': segments, 'message' : "Trascrizione completata"})

@app.route("/api/transcription/<name>", methods=["GET"])
def get_transcription(name):
    # Verifica se il parametro 'file_name' è presente nella richiesta
    if name is None: return make_response(jsonify({'message' : 'Nome del file audio mancante'}), 400)

    # Recupera il nome del file audio dalla richiesta
    audio_file_name = Path(name).stem
    path_to_transcription = join(env['TRANSCRIPTIONS_FOLDER'], f'{audio_file_name}.json')

    if not exists(path_to_transcription): return make_response(jsonify({'message' : 'Transcription does not exist'}), 400)
    with open(path_to_transcription, "r") as transcription_file: segments = load(transcription_file)
    
    return jsonify({'transcription': segments, 'message' : 'Trascrizione trovata'})

@app.route("/api/transcription/<name>/<strategy>", methods = ["GET"] )
def compute_scale_item(name, strategy):
    if strategy not in strategies: return make_response(jsonify({'message' : 'item selezionato non esiste'}), 400)
    if (response := get_transcription(name)).status_code != 200: return response

    message, transcription = loads(response.data).values()
    
    strategy:Strategy = strategies.get(strategy) 
    score, byproduct = strategy.execute(transcription, "CLINICIAN", "PATIENT")

    return jsonify({'score' : score, 'byproduct': byproduct, 'message' : 'Computazione Terminata'})

############################ TRANSCRIPTIONS ENDPOINTS ############################

@app.route("/transcription/<name>/report/<strategy>", methods = ["GET"] )
def generate_report(name, strategy):
    if (response := compute_scale_item(name, strategy)).status_code != 200: return response
    
    data = loads(response.data)
    score, byproducts = data['score'], data['byproduct'] 
    path_to_file = Path(join(env["REPORT_TEMPLATES"], f'{strategy}.html')).as_posix()

    if "plot" in byproducts: return render_template(path_to_file, plot_64=generate_hbar_plot(byproducts['plot']), score=score, **byproducts)

    return render_template(path_to_file, score=score, **byproducts)

@app.route("/transcription/<name>/report", methods = ["GET"] )
def generate_full_report(name):
    if (strategies := request.json["items"]) is None: return make_response(jsonify({'message' : 'item non sono stati specificati'}), 400)
   
    reports = []
    for strategy in strategies:
        if (response := compute_scale_item(name, strategy)).status_code != 200: return response
    
        score, byproducts = loads(response.data)['results']
        path_to_file = Path(join(env["REPORT_TEMPLATES"], f'{strategy}.html')).as_posix()

        content = render_template(path_to_file, score=score, **byproducts)
        reports.append(content)

    path_to_summary = Path(join(env["REPORT_TEMPLATES"], 'summary.html')).as_posix()
    return render_template(path_to_summary, embedded_contents=reports)


############################ FEEDBACKS ENDPOINTS ############################

@app.route("/api/feedback", methods = ["POST"] )
def feedback_addition():
    if (item_checked := request.json.get('item')) : return make_response(jsonify({'message' : 'item non è specificato'}), 400)
    if (response_first := request.json.get('first')) : return make_response(jsonify({'message' :'prima domanda non è stata riempita'}), 400)
    if (response_second := request.json.get('second')) : return make_response(jsonify({'message' :'seconda domanda non è stata riempita'}), 400)
    if (response_third := request.json.get('third')) : return make_response(jsonify({'message' :'terza domanda non è stata riempita'}), 400)

    # Carica il file JSON
    folder = env['FEEDBACK_FOLDER']
    with open(join(folder, 'feedback.json'), 'r') as json_file:
        data = load(json_file)

    #Aggiorna i counter associati a ciascuna domanda e il numero di sottomissioni
    responses = [response_first, response_second, response_third]
    questions = data.get(item_checked, {}).get('domande', [])

    for idx, (question, response) in enumerate(zip(questions, responses)):
        if not 0 <= response < len(question["risposte"]): return make_response(jsonify(f"Risposta '{response}' non trovata per la domanda {idx + 1}"), 400)
        
        answers = question.get('risposte', {})
        answers[response]['contatore'] = answers[response].get('contatore', 0) + 1
            
    # Increment submission counter
    data["submissions"] = data.get("submissions", 0) + 1

    # Scrivi le modifiche nel file JSON
    with open(join(folder, 'feedback.json'), 'w') as json_file:
        dump(data, json_file, indent=4)

    return jsonify({'message':'Feedback aggiunto correttamente'})


############################ MAIN SETUP ############################ 

if __name__ == "__main__":
    with open(env["METRICS_THRESHOLDS"], "r") as config: metrics_options:dict[str, dict] = load(config)
    for x in Strategy.__subclasses__():
        weights, thresholds = metrics_options.get(underscore(x.__name__), {"weights" : {}, "thresholds" : {}}).values()
        instance = x(**weights, **thresholds)

        strategies[underscore(x.__name__)] = instance

    app.run(port=5000)