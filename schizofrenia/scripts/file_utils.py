import json
from pathlib import Path

# Salva i risultati secondo la stessa struttura dei file di input
def save_results(results):
    """Salva i risultati in un file JSON."""
    basedir= Path("results")

    for folder_result in results:
        folder_path = basedir / folder_result["folder"]
        folder_path.mkdir(parents=True, exist_ok=True)

        for patient in folder_result["patients"]:
            patient_path = folder_path /  patient["patient"]
            video_results_path = patient_path / "videos_results"
            video_results_path.mkdir(parents=True, exist_ok=True)

            for video in patient["videos"]:
                to_save =  {
                    "patient": patient["metadata"],
                    "frames": video["sequences"],
                }
                filename = Path(video["video_file"][:-4]).with_suffix(".json")
                generate_json_results(to_save, video_results_path / filename, indent=False)

            generate_json_results(patient["quality_results"], patient_path / "quality_results.json")
            generate_json_results(patient["lost_frames_results"], patient_path / "lost_frames_results.json")

# Funzione per leggere il file metadati e restituire una lista di numeri (o stringhe) di paziente
def read_metadata(metadata_path):
    """Legge il file metadati e restituisce una lista di dizionari contenenti le info del paziente."""
    patients = []
    with open(metadata_path, 'r') as f:
        for line in f:
            if line.strip():
                metadata = parse_metadata_line(line)
                patients.append(metadata)
    return patients

# Recupera le informazioni dai file metadati presenti nelle cartelle
def parse_metadata_line(line):
    """Estrae le informazioni da una riga dei metadati.
       Si assume che la riga sia formata da token separati da underscore.
    """
    tokens = line.strip().split('_')
    result = {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "ID" and i + 1 < len(tokens):
            result["ID"] = tokens[i + 1]
            i += 2
        elif token == "INIT":
            init_tokens = []
            j = i + 1
            while j < len(tokens) and tokens[j] != "AGE":
                init_tokens.append(tokens[j])
                j += 1
            result["INIT"] = "_".join(init_tokens)
            i = j
        elif token == "AGE" and i + 1 < len(tokens):
            result["AGE"] = tokens[i + 1]
            i += 2
        elif token == "GENDER" and i + 1 < len(tokens):
            result["GENDER"] = tokens[i + 1]
            i += 2
        elif token == "CLASS" and i + 1 < len(tokens):
            result["CLASS"] = tokens[i + 1]
            i += 2
        else:
            i += 1
    return result


def generate_json_results(results, filename, indent=True):
    with open(filename, "w") as f:
        if indent:
            json.dump(results, f, indent=4)
        else:
            json.dump(results, f)