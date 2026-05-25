import os


def save_dataframe_to_csv(dataframe, outputs_dir="outputs", file_name="sevilla_pixel_data.csv"):
    os.makedirs(outputs_dir, exist_ok=True)
    output_csv_path = os.path.join(outputs_dir, file_name)
    dataframe.to_csv(output_csv_path, index=False)
    return output_csv_path
