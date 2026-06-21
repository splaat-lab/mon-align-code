import collections
import os
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

export_directory = r"D:\Data\experiments\mon-align"

special_files = {"1995-1837-0012", "237-126133-0015", "3570-5695-0006"}

if __name__ == "__main__":
    output_path = os.path.join(root_directory, 'data', 'file_stats.csv')
    data = {}
    with open(output_path, "r", encoding='utf8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            print(line)
            if line['file'] in special_files:
                continue
            data[line['file']] = line

    print(len(data), len(data)/40)
    error