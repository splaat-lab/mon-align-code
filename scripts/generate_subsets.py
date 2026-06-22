import collections
import os
import shutil

import soundfile as sf
import librosa
import sys
import csv
import re
import numpy as np
from praatio import textgrid as tgio
from splaat.plot.combined import plot_file

root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_dir = r"C:\Users\micha\Documents\Data\benchmarks\librispeech_alignment_benchmark"

export_directory = r"D:\Data\experiments\mon-align\subsets"

special_files = {"1995-1837-0012", "237-126133-0015", "3570-5695-0006"}

def export_file(export_directory, file_name):
    os.makedirs(export_directory, exist_ok=True)
    speaker = file_name.split('-')[0]
    shutil.copyfile(os.path.join(data_dir, speaker, f"{file_name}.wav"), os.path.join(export_directory, f"{file_name}.wav"))
    shutil.copyfile(os.path.join(data_dir, speaker, f"{file_name}.TextGrid"), os.path.join(export_directory, f"{file_name}.TextGrid"))

if __name__ == "__main__":
    everyone_file_path = os.path.join(root_directory, "data", "everyone_files.csv")
    everyone_files = []
    with open(everyone_file_path, "r", encoding='utf8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            everyone_files.append(line['file'])
    cohort_files = {}
    for cohort in range(1, 9):
        cohort_path = os.path.join(root_directory, "data", f"c{cohort}_files.csv")
        cohort_files[cohort] = []
        with open(cohort_path, "r", encoding='utf8') as f:
            reader = csv.DictReader(f)
            for line in reader:
                cohort_files[cohort].append(line['file'])
    for annotator in range(1, 41):
        cohort = int((annotator-1)/5) + 1
        annotator_path = os.path.join(root_directory, "data", f"a{annotator}_files.csv")
        extras_path = os.path.join(root_directory, "data", f"a{annotator}_extra_files.csv")
        annotator_export_directory = os.path.join(export_directory, f"c{cohort}_a{annotator}")
        everyone_export_directory = os.path.join(annotator_export_directory, "common")
        cohort_export_directory = os.path.join(annotator_export_directory, "cohort")
        individual_export_directory = os.path.join(annotator_export_directory, "individual")
        extra_export_directory = os.path.join(annotator_export_directory, "extras")
        for file_name in everyone_files:
            export_file(everyone_export_directory, file_name)
        for file_name in cohort_files[cohort]:
            export_file(cohort_export_directory, file_name)

        with open(annotator_path, "r", encoding='utf8') as f:
            reader = csv.DictReader(f)
            for line in reader:
                export_file(individual_export_directory, line['file'])

        with open(extras_path, "r", encoding='utf8') as f:
            reader = csv.DictReader(f)
            for line in reader:
                export_file(extra_export_directory, line['file'])