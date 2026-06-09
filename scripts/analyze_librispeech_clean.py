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
import matplotlib.pyplot as plt

root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_dir = r"C:\Users\micha\Documents\Data\benchmarks\librispeech_alignment_benchmark"

export_directory = r"D:\Data\experiments\mon-align"

if __name__ == "__main__":
    vowel_pattern = re.compile(r"^[AIEUO].*")
    high_back_vowel_pattern = re.compile(r"^U.*")
    nasals = {'N', "M", "NG"}
    voiceless_sibilants = {"S", "SH"}
    voiced_sibilants = {"Z", "ZH"}
    voiceless_stops = {"P", "T", "K"}
    voiced_stops = {"B", "D", "G"}
    count_thirty = 0
    count_ten = 0
    total_count = 0
    data = {}
    count_headers = set()
    phone_counts = collections.Counter()
    s_file_count = 0
    no_surrounding_silence_count = 0
    output_path = os.path.join(root_directory, 'data', 'file_stats.csv')
    for speaker in os.listdir(data_dir):
        speaker_dir = os.path.join(data_dir, speaker)
        for file_name in os.listdir(speaker_dir):
            if not file_name.endswith(".wav"):
                continue
            file_path = os.path.join(speaker_dir, file_name)
            stem = file_name.rsplit(".",maxsplit=1)[0]
            if stem not in data:
                data[stem] = {
                    "file": stem,
                    "speaker": speaker,
                }
            total_count += 1
            duration = sf.info(file_path).duration
            if duration > 30:
                count_thirty += 1
            if duration > 10:
                count_ten += 1
            data[stem]['duration'] = duration
            audio, sr = librosa.load(
                file_path, sr=16000, mono=False
            )
            rms = librosa.feature.rms(
                S=librosa.magphase(librosa.stft(audio, hop_length=int(0.01 * sr)))[0]
            )[0, ...]
            rms[rms == 0] = sys.float_info.epsilon
            intensity = 20 * np.log10(rms / 2e-5)
            tg_path = file_path.replace(".wav", ".TextGrid")
            tg = tgio.openTextgrid(tg_path, includeEmptyIntervals=False)
            phone_intervals = tg._tierDict["phones"]._entries
            silence_intensity_sum = 0
            silence_frame_count = 0
            counts = collections.Counter()
            has_s = False
            audio_peaked = False
            if np.abs(audio).max() > 0.99:
                audio_peaked = True
            no_surrounding_silence = False
            silence_duration = 0
            s_frame_count = 0
            s_intensity_sum = 0
            primary_environment_count = 0
            secondary_environment_count = 0
            count_ordering = {
                "UWUH_L": 1,
                "vowel_R": 1,
                "W_UWUH": 1,
                "vowel_vowel": 1,
                "sil_HH": 1,
                "sil_F": 1,
                "sil_TH": 1,
                "F_sil": 1,
                "V_sil": 1,
                "TH_sil": 1,
                "sil_DH": 2,
                "sil_V": 2,
                "vowel_L": 2,
                "Y_UWUH": 2,
                "Y_vowel": 2,
                "W_vowel": 2,
                "L_vowel": 2,
                "R_vowel": 2,
                "vowel_T_vowel": 2,
                "vowel_D_vowel": 2,
                "vowel_sil": 2,
                "DH_sil": 2,
            }
            for i, pi in enumerate(phone_intervals):
                phone = pi.label
                if phone == 'S':
                    has_s = True
                    begin_index = int(pi.start / 0.01)
                    end_index = int(pi.end / 0.01)
                    s_frame_count += end_index - begin_index
                    s_intensity_sum += intensity[begin_index:end_index].sum()
                phone_counts[phone] += 1
                previous_phone = ''
                following_phone = ''
                if i != 0:
                    previous_phone = phone_intervals[i-1].label
                if i != len(phone_intervals) - 1:
                    following_phone = phone_intervals[i+1].label
                phone_is_vowel = vowel_pattern.match(phone)
                phone_is_high_back_vowel = high_back_vowel_pattern.match(phone)
                following_is_vowel = vowel_pattern.match(following_phone)
                previous_is_vowel = vowel_pattern.match(previous_phone)
                if phone == 'sil':
                    counts["silence_count"] += 1
                    silence_duration += (pi.end - pi.start)
                else:
                    counts["nonsilence_count"] += 1
                # Approximant things
                if phone_is_vowel and following_phone == 'L':
                    if phone_is_high_back_vowel:
                        counts["UWUH_L"] += 1
                        primary_environment_count += 1
                    else:
                        counts["vowel_L"] += 1
                        secondary_environment_count += 1
                if phone_is_vowel and following_phone == 'R':
                    counts["vowel_R"] += 1
                    primary_environment_count += 1
                    v = re.sub(r'\d', "", phone)
                    counts[f"{v}_R"] += 1
                if phone_is_vowel and previous_phone == 'Y':
                    if phone_is_high_back_vowel:
                        counts["Y_UWUH"] += 1
                        secondary_environment_count += 1
                    else:
                        counts["Y_vowel"] += 1
                        secondary_environment_count += 1
                if phone_is_vowel and previous_phone == 'W':
                    if phone_is_high_back_vowel:
                        counts["W_UWUH"] += 1
                        primary_environment_count += 1
                    else:
                        counts["W_vowel"] += 1
                        secondary_environment_count += 1
                if phone_is_vowel and previous_phone == 'L':
                    counts["L_vowel"] += 1
                    secondary_environment_count += 1
                if phone_is_vowel and previous_phone == 'R':
                    counts["R_vowel"] += 1
                    secondary_environment_count += 1

                # Stop things
                if phone in voiceless_stops and previous_phone == 'sil':
                    counts["sil_PTK"] += 1
                if phone in voiced_stops and previous_phone == 'sil':
                    counts["sil_BDG"] += 1
                if phone in voiceless_stops and previous_is_vowel and following_is_vowel and phone != 'T':
                    counts["vowel_PK_vowel"] += 1
                if phone in voiced_stops and previous_is_vowel and following_is_vowel and phone != 'D':
                    counts["vowel_BG_vowel"] += 1
                if previous_is_vowel and following_is_vowel and phone == 'T':
                    counts["vowel_T_vowel"] += 1
                    secondary_environment_count += 1
                if previous_is_vowel and following_is_vowel and phone == 'D':
                    counts["vowel_D_vowel"] += 1
                    secondary_environment_count += 1

                # Vowel things

                if phone_is_vowel and following_is_vowel:
                    counts["vowel_vowel"] += 1
                    primary_environment_count += 1
                if phone_is_vowel and following_phone == 'sil':
                    counts["vowel_sil"] += 1
                    secondary_environment_count += 1

                # Nasal things

                if phone in nasals and following_is_vowel:
                    counts["nasal_vowel"] += 1
                if phone_is_vowel and following_phone in nasals:
                    counts["vowel_nasal"] += 1

                # Fricative things

                if phone in voiceless_sibilants and previous_phone == 'sil':
                    counts["sil_SSH"] += 1
                if phone in voiced_sibilants and previous_phone == 'sil':
                    counts["sil_ZZH"] += 1
                if phone == "HH" and previous_phone == 'sil':
                    counts["sil_HH"] += 1
                    primary_environment_count += 1
                if phone == "F" and previous_phone == 'sil':
                    counts["sil_F"] += 1
                    primary_environment_count += 1
                if phone == "TH" and previous_phone == 'sil':
                    counts["sil_TH"] += 1
                    primary_environment_count += 1
                if phone == "DH" and previous_phone == 'sil':
                    counts["sil_DH"] += 1
                    secondary_environment_count += 1
                if phone == "V" and previous_phone == 'sil':
                    counts["sil_V"] += 1
                    secondary_environment_count += 1
                if phone == "F" and following_phone == 'sil':
                    counts["F_sil"] += 1
                    primary_environment_count += 1
                if phone == "V" and following_phone == 'sil':
                    counts["V_sil"] += 1
                    primary_environment_count += 1
                if phone == "TH" and following_phone == 'sil':
                    counts["TH_sil"] += 1
                    primary_environment_count += 1
                if phone == "DH" and following_phone == 'sil':
                    counts["DH_sil"] += 1
                    secondary_environment_count += 1


                if i == 0 or i == len(phone_intervals) - 1:
                    if phone == 'sil':
                        begin_index = int(pi.start / 0.01)
                        end_index = int(pi.end / 0.01)
                        silence_frame_count += end_index - begin_index
                        silence_intensity_sum += intensity[begin_index:end_index].sum()
                    else:
                        no_surrounding_silence = True
                if i == 1:
                    output_directory = os.path.join(export_directory, "utterance_initial", f"sil_{following_phone}")
                    os.makedirs(output_directory, exist_ok=True)
                    start = max(phone_intervals[i].end - 0.2, 0)
                    end = min(phone_intervals[i].end + 0.2, duration)
                    output_path = os.path.join(output_directory, f"{file_name}.png")
                    fig = plot_file(file_path, tg_path, start=start, end=end)
                    fig.savefig(output_path, bbox_inches = "tight")
                    plt.close()
                if i == len(phone_intervals) - 1:
                    output_directory = os.path.join(export_directory, "utterance_final", f"{previous_phone}_sil")
                    os.makedirs(output_directory, exist_ok=True)
                    start = max(phone_intervals[i].start - 0.2, 0)
                    end = min(phone_intervals[i].start + 0.2, duration)
                    output_path = os.path.join(output_directory, f"{file_name}.png")
                    fig = plot_file(file_path, tg_path, start=start, end=end)
                    fig.savefig(output_path, bbox_inches = "tight")
                    plt.close()
            if no_surrounding_silence:
                no_surrounding_silence_count += 1
            data[stem]['no_surrounding_silence'] = no_surrounding_silence
            data[stem]['has_s'] = has_s
            data[stem]['audio_peaked'] = audio_peaked
            data[stem]['silence_duration'] = silence_duration
            data[stem]['primary_environment_count'] = primary_environment_count
            data[stem]['secondary_environment_count'] = secondary_environment_count

            data[stem]['silence_intensity'] = silence_intensity_sum / silence_frame_count
            if s_frame_count:
                data[stem]['s_intensity'] = s_intensity_sum / s_frame_count
            else:
                data[stem]['s_intensity'] = None
            if has_s:
                s_file_count += 1
            count_headers.update(counts.keys())
            data[stem].update(counts)

    for k, v in data.items():
        for h in count_headers:
            if h not in v:
                data[k][h] = 0

    print(sorted(phone_counts.items(), key=lambda x: -1*x[1]))
    print(total_count, count_thirty, count_ten, s_file_count, no_surrounding_silence_count)
    with open(output_path, 'w', encoding='utf8', newline='') as f:
        header = ["file", "speaker", "duration", "silence_duration", "silence_intensity", "s_intensity", "no_surrounding_silence", "has_s", "audio_peaked", "primary_environment_count", "secondary_environment_count"]
        header += sorted(count_headers, key=lambda x: count_ordering.get(x, 4))
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        writer.writerows(data.values())
