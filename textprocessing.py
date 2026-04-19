from natasha import Doc
import argostranslate.translate

def lemmatize_text(text, segmenter, morph_tagger, morph_vocab):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    omit_pos = {"PRON", "ADP", "PART", "CCONJ", "SCONJ", "INTJ", "NUM", "PUNCT"}
    lemma_data = {}  # lemma -> (pos, freq)

    for token in doc.tokens:
        if not token.text.isalpha():
            continue
        token.lemmatize(morph_vocab)
        lemma = token.lemma.lower()
        pos = token.pos
        if pos not in omit_pos:
            if lemma in lemma_data:
                lemma_data[lemma] = (pos, lemma_data[lemma][1] + 1)
            else:
                lemma_data[lemma] = (pos, 1)

    result = [(lemma, pos, freq) for lemma, (pos, freq) in lemma_data.items()]
    result.sort(key=lambda x: x[2], reverse=True)
    return result

def translate_lemmas(lemmas_with_pos):
    translations = []
    for lemma, pos in lemmas_with_pos:
        try:
            translation = argostranslate.translate.translate(lemma, "ru", "en")
        except Exception as e:
            print(f"Translation failed for '{lemma}': {e}")
            translation = ""
        translations.append((lemma, pos, translation))
    return translations


def format_flashcards(translated_lemmas):
    formatted = []
    for lemma, pos, translation in translated_lemmas:
        if not translation:
            continue
        if pos == "NOUN":
            back = f"{translation.title()}"
        elif pos == "VERB":
            back = f"to {translation}"
        elif pos == "ADJ":
            back = f"{translation} (adj.)"
        elif pos == "ADV":
            back = f"{translation} (adv.)"
        else:
            back = f"{translation}"
        formatted.append((lemma, back))
    return formatted