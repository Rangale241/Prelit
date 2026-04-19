import os
import platform
import subprocess
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return ""

def write_lemma_frequencies(filepath, lemmas_with_freq):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for lemma, freq in lemmas_with_freq:
                f.write(f"{lemma}\t{freq}\n")
    except Exception as e:
        print(f"Error writing to file '{filepath}': {e}")

def open_file(filepath):
    if not os.path.isfile(filepath):
        print(f"File does not exist: {filepath}")
        return

    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(filepath)
        elif system_name == "Darwin":  # macOS
            subprocess.run(["open", filepath], check=True)
        else:  # Linux and others
            subprocess.run(["xdg-open", filepath], check=True)
    except Exception as e:
        print(f"Failed to open file: {e}")

def export_to_anki(filepath, translated_lemmas):
    try:
        with open(filepath, "w", encoding="utf-8") as f:  # append mode
            for lemma, translation in translated_lemmas:
                f.write(f"{lemma}\t{translation}\n")
    except Exception as e:
        print(f"Error exporting to Anki file '{filepath}': {e}")

def load_seen_lemmas(filepath):
    seen = set()
    if not os.path.isfile(filepath):
        return seen
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if parts and parts[0]:
                    seen.add(parts[0].lower())
    except Exception as e:
        print(f"Error loading seen lemmas from '{filepath}': {e}")
    return seen

def save_seen_lemmas(filepath, lemmas):
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            for lemma in sorted(lemmas):
                f.write(f"{lemma}\tKNOWN\n")
    except Exception as e:
        print(f"Error saving seen lemmas to '{filepath}': {e}")


def count_lemmas(lemmas_with_freq):
    lems = []
    count = len(lems)
    for l in lemmas_with_freq:
        lems.append(l)
        return(count)