import json
import logging
from pathlib import Path

from model_pillow import Model


def evaluate(logging, input_directory:Path, output_directory:Path, integration_output:Path):
    model_path = input_directory / "final_model.h5"
    model = Model(logging, str(model_path))

    results = []
    cats_directory = input_directory / "evaluate"
    for path in cats_directory.glob("**/*"):
        if path.is_dir():
            continue
        model_result = model.execute(str(path))

        prediction = model_result["prediction"]
        prediction_truth = path.parent.name.lower().replace("s", "")
        result = {"filename": path.name,
                  "ok": prediction_truth == prediction.lower(),
                  "prediction": prediction,
                  "prediction_truth": prediction_truth,
                  "values": model_result["values"]}
        results.append(result)

    with open(output_directory / "predictions.json", 'w') as file_stream:
        json.dump(results, file_stream, indent=4)

    model_path_output = output_directory / "final_model.h5"
    model_path_output.write_bytes(model_path.read_bytes())

    mlcli_directory = integration_output / "mlcli"
    mlcli_directory.mkdir(parents=True, exist_ok=True)
    for source_path in cats_directory.glob("**/*"):
        if source_path.is_dir():
            continue
        destination_path = mlcli_directory / source_path.name
        destination_path.write_bytes(source_path.read_bytes())

    ground_truth_directory = integration_output / "ground_truth"
    ground_truth_directory.mkdir(parents=True, exist_ok=True)
    for file in results:
        filename = file["filename"]
        data = {
            "Url": "https://www.groundtruth.fr",
            "FileName": filename,
            "FileDirectory": "",
            "ImageDirectory": "",
            "FrontDefaultStringsMatcher": "",
            "StatusCode": 200,
            "Body": json.dumps(file),
            "Headers": [],
            "TimeMs": 0,
            "TicksAt": 0
        }
        truth_filename = Path(filename).stem + "_" + Path(filename).suffix.lower().replace(".", '') + ".json"
        with open(ground_truth_directory / truth_filename, 'w') as file_stream:
            json.dump(data, file_stream, indent=4)