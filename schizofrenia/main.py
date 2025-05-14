import sys

from scripts.file_utils import *
from scripts.realsense_utils import *
from scripts.pose_estimation import *

# Funzione che processa un file di tipo bag
def process_bag_file(bag_file):
    print(f"Processo file: {bag_file}")
    pipeline, playback, profile = setup_realsense(bag_file)
    sequences = []
    total_frames = 0
    lost_frames = 0
    invalid_keypoint_frames = 0
    previous_timestamp = None

    try:
        while True:
            color_frame, depth_frame, current_timestamp = get_frames(pipeline, playback)

            if color_frame is None or current_timestamp is None:
                print("Fine del file .bag, terminazione...")
                break

            total_frames += 1

            if previous_timestamp is not None:
                if check_frame_loss(previous_timestamp, current_timestamp):
                    lost_frames += 1
                    previous_timestamp = current_timestamp
                    continue

            previous_timestamp = current_timestamp

            color_frame = apply_brightness_contrast(color_frame)

            #color_frame = process_pose(color_frame)
            keypointsa = process_pose_3d(color_frame,depth_frame)
            #color_frame = draw_pose_on_grid(keypoints)
            #color_frame = draw_pose_on_grid_with_depth(keypoints)

            keypoints = process_pose_2d(color_frame)

            # Verifica se ci sono abbastanza keypoints
            if has_sufficient_keypoints(keypoints):
                #color_frame = draw_pose_on_grid(keypoints)
                #color_frame = draw_pose_on_grid_3d(keypointsa)
                pass
            else:
                invalid_keypoint_frames += 1
                continue

            #sequences.append(keypoints)
            sequences.append(keypointsa)

            # Mostra il risultato
            #cv2.imshow("Pose Estimation2", color_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    finally:
        stop_realsense(pipeline)
        cv2.destroyAllWindows()

    lost_frames_results = process_video_result(total_frames, lost_frames, invalid_keypoint_frames)

    return sequences, lost_frames_results


# Funzione che processa i risultati per un paziente
def process_patient_result(patient_path: Path, metadata: dict) -> dict:
    patient_result = {
        "patient": patient_path.name,
        "metadata": metadata,
        "videos": [],
        "quality_results": [],
        "lost_frames_results": []
    }

    for bag_file in patient_path.glob("*.bag"):
        sequences, lost_frames_results = process_bag_file(bag_file)

        patient_result["videos"].append({
            "video_file": bag_file.name,
            "sequences": sequences
        })

        patient_result["quality_results"].append({
            "File": bag_file.name,
            "Quality measures": assessment_quality(bag_file)
        })

        patient_result["lost_frames_results"].append({
            "File": bag_file.name,
            "Frames": lost_frames_results
        })

    return patient_result

def main():
    if len(sys.argv) < 2:
        base_dir = Path(r"D:\Universita\UNISA\Magistrale\Tesi")
    else:
        base_dir = Path(sys.argv[1])

    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Errore: {base_dir} non esiste o non è una directory valida.")
        return

    #base_dir = Path(r"D:\Universita\UNISA\Magistrale\Prova")
    all_results = []

    # Scorri tutte le cartelle dentro la directory base
    for folder_path in base_dir.iterdir():
        if not folder_path.is_dir():
            continue

        metadata_file = folder_path / "metadati.txt"
        if not metadata_file.exists():
            print(f"Il file metadati.txt non è presente in {folder_path}, salto questa cartella.")
            continue

        metadata_list = read_metadata(metadata_file)
        metadata_map = {m["ID"]: m for m in metadata_list if "ID" in m}

        folder_result = {
            "folder": folder_path.name,
            "patients": []
        }

        for patient_dir in folder_path.iterdir():
            if not patient_dir.is_dir() or not patient_dir.name.startswith("PAZIENTE"):
                continue

            patient_number = patient_dir.name.split()[-1]
            if patient_number not in metadata_map:
                print(f"Il paziente {patient_number} non è presente nei metadati, salto la cartella {patient_dir}.")
                continue

            patient_result = process_patient_result(patient_dir, metadata_map[patient_number])
            folder_result["patients"].append(patient_result)

        all_results.append(folder_result)

    # Salva tutti i risultati in un file JSON
    save_results(all_results)


if __name__ == "__main__":
    main()
