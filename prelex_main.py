import streamlit as st
from file_utils import load_seen_lemmas, read_file, export_to_anki, save_seen_lemmas, get_base_path
from textprocessing import lemmatize_text, translate_lemmas, format_flashcards
import os
import subprocess
import sys
from pathlib import Path
from natasha import NewsEmbedding, NewsMorphTagger, Segmenter, MorphVocab
from datetime import datetime

import argostranslate.package
import argostranslate.translate

@st.cache_resource
def setup_argos():
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    package = next(
        p for p in available_packages
        if p.from_code == "ru" and p.to_code == "en"
    )

    download_path = package.download()
    argostranslate.package.install_from_path(download_path)

    return True

setup_argos()


segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#APP_DATA = Path(os.environ["LOCALAPPDATA"]) / "Prelex"
#APP_DATA.mkdir(exist_ok=True)
#VOCAB_REPO_PATH = APP_DATA / f"anki_export_{timestamp}.tsv"
#SEEN_LEMMAS_PATH = APP_DATA / "extant_lemmas.tsv"
#NEW_LEMMAS_PATH = APP_DATA / "new_lemmas.txt"

# Step 1 Display opening screen, provide text uploading options
#

st.title(f":primary[Prelit]")
st.subheader(f":primary[Input Options]")
# Opening Screen: Pick language, paste text or upload file. Displays preview of uploaded file 
#streamlit run prelex_main.py --theme.base="dark" --theme.primaryColor='2979FF'
language = st.selectbox("Select a language:", ['Russian', 'Martian', 'lolzsp33k'])
#if language == 'Russian':
    #lang_processor = russian_text_processing
st.write("Paste text or upload a file to learn new vocabulary")
text_input = st.text_area(f"Paste {language} text here:")
uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])
if uploaded_file is not None:
    text_input = uploaded_file.read().decode("utf-8")
    st.markdown(":primary[File loaded successfully!]")
    st.text_area("Preview:", value=text_input[:500], height=200)
word_counter = len(text_input.split())
st.write(f":primary[{word_counter}] total words")

# Step 2 - Lemmatize Text, Get Total Identified Lemma Count. Remove existing words. Write lemmas and count to txt. 
new_lemmas = []
new_lemma_volume = 0
if text_input: #and st.button(":primary[Analyse]"):
    all_lemmas = lemmatize_text(text_input, segmenter, morph_tagger, morph_vocab)
    total_lemma_count = len(all_lemmas)
    #seen_lemmas = load_seen_lemmas(SEEN_LEMMAS_PATH)
    new_lemmas = [(lemma, pos, freq) for lemma, pos, freq in all_lemmas if lemma.strip().lower()] #not in seen_lemmas]
    
    new_lemma_output = "\n".join(f"{l:<20} {f}" for l, _, f in new_lemmas)
    new_lemma_volume = int(len(new_lemmas))
    unknown_token_count = sum(freq for _, _, freq in new_lemmas)
    st.text_area(f"Preview: :primary[{total_lemma_count}] total unique words. :primary[{new_lemma_volume}] \
                  previously unseen shown below:", value=new_lemma_output[:500], height=200)
    unknown_perc = int((unknown_token_count / word_counter) * 100)
    text_comprehension = int(100 - unknown_perc)
    st.write(f"Estimated Text Comprehension - :primary[~{text_comprehension}%]")

# Step 3 - Determine output volume (percentage and absolute options) and filter results
st.subheader(f":primary[Output Options]")
new_lemmas.sort(key=lambda x: x[2], reverse=True)
top_n = 0
top_new_lemmas = new_lemmas[:top_n]
return_status = ""
filter_option = st.radio("Select Output:", ['Percentage', 'Absolute'])
if new_lemma_volume == 0:
    st.info("No new lemmas found.")
    st.stop()

elif new_lemma_volume == 1:
    st.write("Only 1 new lemma found — automatically selected.")
    returned_value = 1
    top_n = 1

else: 
    if filter_option == 'Percentage':

        returned_value = st.slider("Select percentage of words to return", min_value=1, max_value=100, step=1)
        top_n = max(1, round(len(new_lemmas) * returned_value / 100))
        return_status = "percent of total words."

    else:
        returned_value = st.slider("Select number of words to return", min_value=1, max_value=new_lemma_volume, step=1) 
        top_n = returned_value
        top_new_lemmas = new_lemmas[:top_n]
        return_status = "word" if returned_value == 1 else "words"

    top_new_lemmas = new_lemmas[:top_n]
    st.write(f"Returning top :primary[{returned_value}] {return_status}")



# Step 4 - Translate selected amount of lemmas and format into flashcards for export
selected = [(l, p) for l, p, f in top_new_lemmas]
translated_lemmas = translate_lemmas(selected)

formatted_flashcards = format_flashcards(translated_lemmas)
tsv_data = "\n".join("\t".join(row) for row in formatted_flashcards)
# Step 5 - Provide options for export to SEEN VOCAB PATH and ANKI DECK 
col1, col2 = st.columns([1, 1])


if col1.download_button(f":primary[📤 Download Flashcards]", data=tsv_data,
                        file_name="anki_export.tsv",
                        mime="text/tab-separated-values"):
    st.text("Exporting Flashcards")



if col2.button(":primary[🧠 Add to Known Words]"):
    st.text("Feature Not Yet Available")
    #save_these = [l for l, _, _ in top_new_lemmas]
    #save_seen_lemmas(SEEN_LEMMAS_PATH, save_these)

st.markdown(":primary[---]")



