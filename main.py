import os
import glob
import pandas as pd
import requests
from bs4 import BeautifulSoup
import string
import re
import nltk

nltk.download('cmudict')
cmudict = nltk.corpus.cmudict.dict()

list_positive_scores = []
list_negative_scores = []
list_polarity_scores = []
list_subjectivity_scores = []
list_avg_sentence_length = []
list_percentage_of_complex_words = []
list_fog_index = []
list_avg_words_per_sentence = []
list_total_complex_words_count = []
list_total_words_count = []
list_syllable_per_word = []
list_personal_pronounce = []
list_avg_word_length = []

# Remove punctuation marks from the paragraph
translator = str.maketrans('', '', string.punctuation)

# STOPWORDS
# Add the local path to your folder
stopwords_path = 'C:/Users/91942/Desktop/Blackcoffer/Data/StopWords'

# get a list of all text files in the folder
stopwords_files_list = glob.glob(os.path.join(stopwords_path, '*.txt'))

# loop through each file and read its contents
allstopwords = ''
for stopwords_file in stopwords_files_list:
    with open(stopwords_file, 'r') as stopwords:
        allstopwords = allstopwords + ' ' + stopwords.read()
        # do something with the file contents

# Remove punctuation marks from the allstopwords
allstopwords = allstopwords.translate(translator)

allstopwords = allstopwords.lower()
allstopwords = allstopwords.replace("\n", " ")
allstopwords = allstopwords.split(" ")
while " " in allstopwords:
    allstopwords.remove('')

# The Master Dictionary (found in the folder MasterDictionary) is used for creating a dictionary of Positive and Negative words.
with open('C:/Users/91942/Desktop/Blackcoffer/Data/MasterDictionary/positive-words.txt', 'r') as file:
    positive_words = file.read()
positive_words = positive_words.split('\n')

# The Master Dictionary (found in the folder MasterDictionary) is used for creating a dictionary of Positive and Negative words.
with open('C:/Users/91942/Desktop/Blackcoffer/Data/MasterDictionary/negative-words.txt', 'r') as file:
    negative_words = file.read()
negative_words = negative_words.split('\n')

vowels = ['a', 'e', 'i', 'o', 'u']

input = pd.read_excel("Data/input.xlsx")

for index in range(114):
    page = ''
    page = requests.get(input.iloc[index][1]).text

    soup = BeautifulSoup(page, 'lxml')

    title = soup.find('title').text

    div = soup.find_all('div', class_='td-post-content')

    ptags = 0
    if len(div) != 0:  # index 7
        ptags = len(div[0].find_all('p'))

    art_text = ''
    for j in range(ptags):
        art_text = art_text + ' ' + div[0].find_all('p')[j].text

    article = title + art_text

    article = article.replace('₹', 'Rs.')  # index 47
    article = article.replace('≈', '~')  # index 80
    article = article.replace("\xa0", "")
    article = article.replace("’", "'")

    filename = input.iloc[index][1].replace(':', '%3A')
    filename = filename.replace('/', '%2F')
    filename = filename + '.txt'

    f = open(filename,"x")
    f.write(article)
    f.close()

    article_lower = article.lower()

    # Remove punctuation marks from the paragraph
    clean_article = article_lower.translate(translator)

    clean_article_list = clean_article.split(' ')
    while '' in clean_article_list:
        clean_article_list.remove('')

    '''
    The Stop Words Lists (found in the folder StopWords) are used to clean the text
    so that Sentiment Analysis can be performed by excluding the words found in Stop Words List.
    '''
    j = -1
    no_stopwords_list = clean_article_list.copy()
    for i in range(len(no_stopwords_list)):
        if no_stopwords_list[j] in allstopwords:
            no_stopwords_list.pop(j)
        else:
            j = j - 1

    # Positive Score:
    #    This score is calculated by assigning the value of +1 for each word if found in the Positive Dictionary and then adding up all the values.
    positive_score = 0
    for i in no_stopwords_list:
        if i in positive_words:
            positive_score += 1
    list_positive_scores.append(positive_score)

    # Negative Score:
    #    This score is calculated by assigning the value of +1 for each word if found in the Negative Dictionary and then adding up all the values.
    negative_score = 0
    for i in no_stopwords_list:
        if i in negative_words:
            negative_score += 1
    list_negative_scores.append(negative_score)

    '''
    Polarity Score: This is the score that determines if a given text is positive or negative in nature.
                    It is calculated by using the formula: 
    Polarity Score = (Positive Score – Negative Score)/ ((Positive Score + Negative Score) + 0.000001)
                    Range is from -1 to +1

    '''
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    list_polarity_scores.append(polarity_score)

    '''
    Subjectivity Score: This is the score that determines if a given text is objective or subjective.
                        It is calculated by using the formula: 
    Subjectivity Score = (Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
                        Range is from 0 to +1

    '''
    subjectivity_score = (positive_score + negative_score) / (len(no_stopwords_list) + 0.000001)
    list_subjectivity_scores.append(subjectivity_score)

    sentences = nltk.sent_tokenize(article)

    words = len(clean_article_list)
    list_total_words_count.append(words)

    avg_words_per_sentence = words / len(sentences)
    # Average Number of Words Per Sentence = the total number of words / the total number of sentences
    list_avg_words_per_sentence.append(avg_words_per_sentence)
    # Average Sentence Length = the number of words / the number of sentences
    list_avg_sentence_length.append(avg_words_per_sentence)

    # Complex words are words in the text that contain more than two syllables.
    complex_words = 0
    total_syllables = 0
    syllables = 0

    esed = ['es', 'ed']
    for i in clean_article_list:
        syllables = 0

        if i[-2:] == 'es' or i[-2:] == 'ed': i = i[:-2]

        for j in i:
            if j in vowels: syllables += 1

        if syllables > 2: complex_words += 1

        total_syllables += syllables

    list_total_complex_words_count.append(complex_words)

    syllables_per_word = total_syllables / len(clean_article_list)
    list_syllable_per_word.append(syllables_per_word)

    # Percentage of Complex words = the number of complex words / the number of words
    percent_of_complex_words = complex_words / len(clean_article_list)
    list_percentage_of_complex_words.append(percent_of_complex_words)

    # Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)
    fog_index = 0.4 * (avg_words_per_sentence + percent_of_complex_words)
    list_fog_index.append(fog_index)

    # Define the regular expression pattern to match personal pronouns
    pattern = r'\b(I|me|my|mine|we|us|our|ours|Me|My|Mine|We|Us|Our|Ours)\b'

    # Find all matches of the pattern in the article
    personal_pronouns_list = re.findall(pattern, article)
    personal_pronouns_count = len(personal_pronouns_list)
    list_personal_pronounce.append(personal_pronouns_count)

    char_count = 0
    for i in clean_article_list:
        for j in i:
            char_count += 1
    list_avg_word_length.append(char_count / words)

    if index % 5 == 0:
        print(index)

df = pd.DataFrame({'POSITIVE SCORE': list_positive_scores,
                   'NEGATIVE SCORE': list_negative_scores,
                   'POLARITY SCORE': list_polarity_scores,
                   'SUBJECTIVITY SCORE': list_subjectivity_scores,
                   'AVG SENTENCE LENGTH': list_avg_sentence_length,
                   'PERCENTAGE OF COMPLEX WORDS': list_percentage_of_complex_words,
                   'FOG INDEX': list_fog_index,
                   'AVG NUMBER OF WORDS PER SENTENCE': list_avg_words_per_sentence,
                   'COMPLEX WORD COUNT': list_total_complex_words_count,
                   'WORD COUNT': list_total_words_count,
                   'SYLLABLE PER WORD': list_syllable_per_word,
                   'PERSONAL PRONOUNS': list_personal_pronounce,
                   'AVG WORD LENGTH': list_avg_word_length})

output = pd.concat([input, df], axis=1)
output.to_csv('C:/Users/91942/Desktop/Blackcoffer/Data/Output Data Structure.csv')
output.to_excel('C:/Users/91942/Desktop/Blackcoffer/Data/Output Data Structure.xlsx')