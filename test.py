import nltk
from googletrans import Translator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

# Download the necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')

def translate_text(text, src_lang='auto', dest_lang='en'):
    translator = Translator()
    translation = translator.translate(text, src=src_lang, dest=dest_lang)
    return translation.text

def find_keywords(text, num_keywords=5):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    # Compute the frequency distribution
    freq_dist = FreqDist(filtered_tokens)
    # Get the most common keywords
    keywords = [word for word, freq in freq_dist.most_common(num_keywords)]
    return keywords

# Input sentence in Vietnamese
input_text = "Tôi muốn đổi ngôn ngữ qua tiếng Anh với Python và tìm từ khóa chính trong một câu"

# Translate the sentence to English
translated_text = translate_text(input_text)

# Find the main keywords in the translated sentence
keywords = find_keywords(translated_text)

print(f"Original text: {input_text}")
print(f"Translated text: {translated_text}")
print(f"Keywords: {keywords}")




# https://www.pexels.com/_next/data/xxlKmaj_HcAZ7qYWjlvew/en-US/search/videos/korea.json?query=korea