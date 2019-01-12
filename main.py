'''Module responsible for initializing the question-answering system.

Made by: Stevica Bozhinoski, Ivana Bozhinova and Jasmina Armenska

'''

import os
import math
import yaml

def calculate_lecture_tfidf(bag_words_per_slide):
    '''Calculate TF-IDF scores for each word in a lecture'''

    n_slides = len(bag_words_per_slide)
    slide_number = 1
    lecture_content = {}

    for bag_words_slide1 in bag_words_per_slide:

        slide_content = {}
        n_words = len(bag_words_slide1)

        for word in bag_words_slide1:
            n_slides_containing_word = 0

            for bag_words_slide2 in bag_words_per_slide:
                if word in bag_words_slide2:
                    n_slides_containing_word += 1

            # Main TF-IDF formula.
            term_freq = bag_words_slide1.count(word)/(n_words+1)
            inv_term_freq = math.log(n_slides/(n_slides_containing_word))
            if term_freq*inv_term_freq != 0:
                slide_content[word] = term_freq*inv_term_freq

        lecture_content[str(slide_number)] = slide_content
        slide_number += 1
    return lecture_content

def split_foreign_words(words):
    '''Spliting words into two groups: macedonian and foreign based on the script.'''

    capital_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                       'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                       'U', 'V', 'W', 'X', 'Y', 'Z']
    lower_letters = [letter.lower() for letter in capital_letters]
    letters = lower_letters + capital_letters

    foreign_words = other_words = []

    for word in words:
        is_foreign = True
        for letter in word:
            if letter not in letters:
                is_foreign = False
                break
        if word.strip() != '':
            if is_foreign:
                foreign_words.append(word)
            else:
                other_words.append(word)

    return foreign_words, other_words

def get_document_weights(using_foreign, config):
    '''Calculating the weights of the words in each lecture based on TF-IDF.'''

    remove_symbols = ['', ' ', '-', '\n', '\t']
    document_weights = {}

    lecture_number = 1
    for lecture in config['lectures']:

        bag_words_per_slide = []
        bag_words = []
        with open(os.path.join(os.getcwd(), config['data_dir'], config['lectures_dir'], lecture),
                  encoding='utf-8') as lecture_file:
            lecture_text = lecture_file.readlines()

        for line in lecture_text:

            if line.startswith('Слајд:'):

                # Splitting the bag of words into two subsets: macedonian and foreign words.

                foreign_words, other_words = split_foreign_words(bag_words)

                if using_foreign:
                    other_words += foreign_words
                if other_words:
                    bag_words_per_slide.append(other_words)
                bag_words = []
            else:
                words = line.split(' ')

                # Filter each word.
                for word in words:
                    word = filter_word(word, config['removal_symbols'])
                    if word not in remove_symbols:
                        bag_words.append(word.lower())

        document_weights[str(lecture_number)] = calculate_lecture_tfidf(bag_words_per_slide)
        lecture_number += 1
    return document_weights

def cosine_similarity(doc1, doc2):
    '''Calculate cosine similarity between two documents'''

    intersection = set(doc1.keys()) & set(doc2.keys())
    numerator = sum([doc1[x] * doc2[x] for x in intersection])
    sum1 = sum([doc1[x]**2 for x in doc1.keys()])
    sum2 = sum([doc2[x]**2 for x in doc2.keys()])

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    # In order to avoid division by 0
    if denominator == 0:
        return 0

    return float(numerator) / denominator

def get_topic(question_number, data_dir, map_topics_questions_file):
    '''Get the topic for a given question.'''

    with open(os.path.join(data_dir, map_topics_questions_file),
              encoding='utf-8') as topic_mapping:
        topic_content = topic_mapping.readlines()

    for line in topic_content:
        parts = line.split()
        parts2 = parts[1].split('-')
        if question_number >= int(parts2[0]) and question_number <= int(parts2[1]):
            return parts[0]
    return None

def check_correct(question_number, calculated_answer, data_dir, answers_file):
    '''Check if the guessed number is correct.'''

    with open(os.path.join(data_dir, answers_file), encoding='utf-8') as answers:
        answers_content = answers.readlines()

    result = 'maybe'
    for line in answers_content:
        parts = line.split()
        if parts[0] == question_number:
            true_answer = parts[1]
            print('The correct answer is: '+true_answer)
            if true_answer == calculated_answer:
                result = 'true'
            elif true_answer != calculated_answer:
                result = 'false'
            break
    return result

def filter_word(word, removal_symbols):
    '''Removing unwanted symbols at the beginning and end of a given word.'''

    while word != '' and word[0] in removal_symbols:
        word = word[1:]
    while word != '' and word[-1] in removal_symbols:
        word = word[:-1]
    return word

def get_similar_slide(weight_question, topic, document_weights):
    '''Get the most similar slide based on the question.'''

    most_similar_slide = {}
    highest_similarity = -2

    for slide_n in document_weights[topic]:
        slide = document_weights[topic][slide_n]
        similarity = cosine_similarity(weight_question, slide)

        if similarity > highest_similarity:
            most_similar_slide = slide
            highest_similarity = similarity

    return most_similar_slide

def get_closest_answer(answers, most_similar_slide, config):
    '''Get the closest slide based on the available multiple-choice answers.'''

    most_similar_answer = 'A'
    highest_similarity = -2

    for key in answers.keys():
        answer_weights = {}
        answer = answers[key]

        for word in answer.split():
            answer_weights[filter_word(word, config['removal_symbols']).lower()] = 1
        similarity = cosine_similarity(answer_weights, most_similar_slide)
        if highest_similarity < similarity:
            highest_similarity = similarity
            most_similar_answer = key

    print('The guessed answer is '+most_similar_answer)
    #print(highest_similarity)
    return most_similar_answer

def calculate_accuracy(questions, document_weights, config):
    '''Calculates the accuracy of the system.'''

    correct_questions = 0
    all_questions = 0

    # For each question
    for question in questions:
        print('Question: '+question)
        parts = question.split('.')

        question_n = int(parts[0])

        # Get the topic of the question
        topic = get_topic(question_n, config['data_dir'], config['map_topics_questions_file'])
        words = parts[1].split()
        weight_question = {}
        for word in words:
            weight_question[word.lower()] = 1

        most_similar_slide = get_similar_slide(weight_question, topic, document_weights)

        answers = questions[question]

        is_correct = check_correct(str(question_n),
                                   get_closest_answer(answers, most_similar_slide, config),
                                   config['data_dir'],
                                   config['answers_file'])
        if is_correct == 'true':
            correct_questions += 1
        if is_correct != 'maybe':
            all_questions += 1

    print('\nAccuracy')
    print(str(correct_questions/all_questions * 100)+'%')

def get_questions(filename, data_dir, answer_letters):
    '''Reads all of the questions and available answers from a file.'''

    with open(os.path.join(data_dir, filename), encoding='utf-8') as file_questions:
        lines = [x.strip('\n').strip() for x in file_questions.readlines()]

    all_questions = {}
    question_text = ''
    answers = {}

    for line in lines:
        if line == '':
            continue
        if line[0].isdigit():
            if question_text:
                all_questions[question_text] = answers
            question_text = line
            answers = {}

        elif any(line[0] for x in answer_letters):
            answers[line[0]] = line[2:]
    if question_text:
        all_questions[question_text] = answers
    return all_questions

def run_app():
    '''Running anautomated question-answering system for macedonian test collection.'''

    config = {}
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    questions = get_questions(config['questions_file'],
                              config['data_dir'],
                              config['answer_letters'])
    print('\nRunning the question-answering system...\n')
    document_weights = get_document_weights(False, config)
    calculate_accuracy(questions, document_weights, config)

if __name__ == '__main__':

    run_app()
