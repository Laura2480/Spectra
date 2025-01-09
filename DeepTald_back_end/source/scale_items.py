from collections import namedtuple
from itertools import groupby, chain
from operator import itemgetter
from numpy import digitize
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics.pairwise import cosine_similarity
from abc import ABC, abstractmethod
from cerberus import Validator
from sorcery import dict_of
from phonemizer import phonemize
from torch.nn import functional as F
from schemas import *
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.cuda import empty_cache
from gc import collect
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import math
import re
import utils

class Strategy(ABC):
    """
    Abstract class Strategy is used to generically define a Tald Scale item algorithm
    
    Attributes
    ----------
    schema : any
        a cerberus validator schema to enforce validation logic that self.thresholds and self.weights must follow
    weights : dict
        holds the percentages of relevance each computed factor is given
    thresholds : dict
        holds the thresholds the algorithms uses during computation
    """

    def __init__(self, schema, weights:dict, thresholds:dict) -> None:
        """
        Parameters
        ----------
        schema : any
            a cerberus validator schema to enforce validation logic that self.thresholds and self.weights must follow
        weights : dict
            holds the percentages of relevance each computed factor is given
        thresholds : dict
            holds the thresholds the algorithms uses during computation
        """
        self.schema = Validator(schema)
        self.weights = {}
        self.thresholds = {}

        self.setValues(weights, thresholds)
        
    def execute(self, segments:list[any], 
                speaker_1:str, speaker_2:str) -> tuple[int, dict]: 
        '''
        The following is a template method that executes a strategy's algorithm 
        after performing a series of checks on the given parameters

        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        
        Returns
        -------
        score : int
            a score compliant to Tald scale (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        if segments is None: raise ValueError("segments cannot be None")
        if len(segments) == 0: raise ValueError("segments cannot be Empty")
        if not speaker_1 or not speaker_2: raise ValueError("speakers must be defined")

        return self._execute_impl(segments, speaker_1, speaker_2)

    def setValues(self, weights:dict, thresholds:dict):
        '''
        The following updates self.weights and self.thresholds only if 
        there is no violation of self.schema

        Parameters
        ----------
        weights : dict
            the weights to update
        thresholds : str
            the thresholds to update
        '''
        data = dict_of(weights, thresholds)
        if not self.schema.validate(data): 
            raise ValueError(f"Validation failed: {self.schema.errors}, given are inamissable")
        
        self.weights = weights
        self.thresholds = thresholds

    @abstractmethod
    def _execute_impl(self, segments:list[any], 
                speaker_1:str, speaker_2:str) -> tuple[int, dict]:
        '''
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker
        '''
        pass

# Concrete Strategies
class Logorrhea(Strategy):
    '''
    A class to implement strategy to compute Logorrhea item
    '''

    def __init__(self, interruptions_weight:float, response_length_weight:float, 
                 min_value_avg_response_length:int, max_value_avg_response_length:int) -> None:
        """
        Parameters
        ----------
        interruptions_weight : float
            percentage score to attribute to the interruptions factor. 
            An interruption is detected whenever speaker change between segments
            occurs at really low intervals of time  
        response_length_weight : float
            percentage score to attribute to the response length factor. 
            Response length is the amount of words in a sentence.
        min_value_avg_response_length : int
            the minimum expected average response length 
        max_value_avg_response_length : int
            the maximum expected average response length 
        """
        weights = dict_of(interruptions_weight, response_length_weight)
        thresholds = dict_of(min_value_avg_response_length, max_value_avg_response_length)
        super().__init__(logorrea_schema, weights, thresholds)

    def _execute_impl(self, segments:list[any], speaker_1:str, speaker_2:str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Logorrhea item on speaker_2 by
        considering the two factors interruptions and response lenght of the 
        conversation. 
        The interruptions are computed by seeing how many times speaker_2 intervenes
        after speaker_1 in low intervals of time. The average response lenght is how
        many words are uttered per response on average. 
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale Logorrhea (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        interruptions_weight, response_length_weight = self.weights.values()
        min_value_avg_response_length, max_value_avg_response_length = self.thresholds.values()

        normalize_interruption_score, question_count, interruption_count = utils.counter_interruption(segments, speaker_1, speaker_2)
        speaking_time_patient = utils.calculate_speaking_time(segments, speaker_2)
        speaking_time_doctor = utils.calculate_speaking_time(segments, speaker_1)   
        avg_response_length = utils.avg_response_length(segments, speaker_2)

        normalize_avg_respons_length = (avg_response_length - min_value_avg_response_length) / (max_value_avg_response_length - min_value_avg_response_length)
        normalize_avg_respons_length = 0 if normalize_avg_respons_length < 0 else 4 if normalize_avg_respons_length > 1 else normalize_avg_respons_length
        final_score = (interruptions_weight * normalize_interruption_score) + (response_length_weight * normalize_avg_respons_length)

        n_words_doctor = sum(word["speaker"] == speaker_1 for segment in segments for word in segment["words"])
        n_words_patient = sum(word["speaker"] == speaker_2 for segment in segments for word in segment["words"])
        word_count = {speaker_1 : n_words_doctor, speaker_2 : n_words_patient}
        plot = {
            "values" : [speaking_time_doctor +  speaking_time_patient, speaking_time_patient, speaking_time_doctor],
            "labels" : ['Duration', 'Speaking Time (Patient)', 'Speaking Time (Doctor)'],
            "colors" : ['blue', 'green', 'orange'],
            "xlabel" : 'Time (in sec)',
            "title" : 'Interview time (in sec)'
        }

        intermediate_score = final_score * 4
        score = 4 if intermediate_score > 4 else 0 \
                  if intermediate_score < 0 else round(intermediate_score)

        return score, dict_of(question_count, interruption_count, avg_response_length, speaking_time_patient, speaking_time_doctor, word_count, plot)

class SlowedThinking(Strategy):
    '''
    A class to implement strategy to compute Slowed Thinking item
    '''

    def __init__(self, pause_time_weight:float, response_time_weight:float, 
                 min_value_response_time:int, max_value_response_time:int) -> None:
        """
        Parameters
        ----------
        pause_time_weight : float
            percentage score to attribute to the pause time factor. 
            Pause time is the interval of time in between two spoken words.
        response_time_weight : float
            percentage score to attribute to the response time factor. 
            Response time is the time interval between the end time of 
            one speaker and the start time of the second speaker
        min_value_response_time : int
            the minimum expected response time 
        max_value_avg_response_length : int
            the maximum expected response time  
        """
        weights = dict_of(pause_time_weight, response_time_weight)
        thresholds = dict_of(min_value_response_time, max_value_response_time)
        super().__init__(slowed_thinking_schema, weights, thresholds)
    
    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Slowed Thinking item on speaker_2 by
        considering the two factors pause time  and response time of the 
        conversation. 
        The pause time is computed by summing all time intervals in between speaker_2 
        spoken words. The response time is computed by summing all time intervals in  
        between speaker_1 to speaker_2 transitions.
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Slowed Thinking (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        
        pause_time_weight, response_time_weight = self.weights.values()
        min_value_response_time, max_value_response_time = self.thresholds.values()

        interruption_score, question_count, interruption_count = utils.counter_interruption(segments, speaker_1, speaker_2)
        pause_between_words = utils.pause_time_between_words(segments, speaker_2)
        average_response_time = utils.response_time(segments, speaker_1, speaker_2)
        speaking_time_patient = utils.calculate_speaking_time(segments, speaker_2)
        speaking_time_doctor = utils.calculate_speaking_time(segments, speaker_2)

        n_words_doctor = sum(word["speaker"] == speaker_1 for segment in segments for word in segment["words"])
        n_words_patient = sum(word["speaker"] == speaker_2 for segment in segments for word in segment["words"])
        word_count = {speaker_1 : n_words_doctor, speaker_2 : n_words_patient}

        #Percentuale di pause nei segmenti di parlato rispetto al discorso totale del paziente
        normmalized_score_pause = pause_between_words / speaking_time_patient
        normalized_time_response = (average_response_time - min_value_response_time) / (max_value_response_time - min_value_response_time)
        normalized_time_response = 0 if normalized_time_response < 0 else 1 if normalized_time_response > 1 else normalized_time_response
        plot = {
            "values" : [speaking_time_doctor +  speaking_time_patient, speaking_time_patient, speaking_time_doctor],
            "labels" : ['Duration', 'Speaking Time (Patient)', 'Speaking Time (Doctor)'],
            "colors" : ['blue', 'green', 'orange'],
            "xlabel" : 'Time (in sec)',
            "title" : 'Interview time (in sec)'
        }
        
        final_score = (pause_time_weight * normmalized_score_pause) + (response_time_weight * normalized_time_response)
        intermediate_score = final_score * 4
        score = 4 if intermediate_score > 4 else 0 \
                  if intermediate_score < 0 else round(intermediate_score)

        return score, dict_of(question_count, pause_between_words, average_response_time, speaking_time_patient, speaking_time_doctor, word_count, plot)

class LossOfThought(Strategy):
    '''
    A class to implement strategy to compute Loss of Thought item
    '''

    def __init__(self) -> None:
        thresholds = dict_of(threshold_next_token = 0.2)
        super().__init__(loss_of_thought_schema, {}, thresholds)
    
    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Loss of Thought item on speaker_2 by
        considering the single factor number of pauses. 
        The number of pauses is computed by means of next token prediction on each
        speaker_2 response and semantic similarity on speaker_1 questions. If the 
        next predicted token is not a end of sentence (.) or the next speaker_1 question
        is similar to TALD manual follow up questions then a rupture has occured.  
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Loss of Thought (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''

        threshold_next_token = self.thresholds['threshold_next_token']
        clinician_segments = [list(group) for curr_speaker, group in groupby(segments, key=lambda x: x["speaker"]) if curr_speaker == speaker_1]
        patient_segments = [list(group) for curr_speaker, group in groupby(segments, key=lambda x: x["speaker"]) if curr_speaker == speaker_2]
        conversation = zip(patient_segments, clinician_segments[1:])

        tokenizer = AutoTokenizer.from_pretrained("GroNLP/gpt2-small-italian", clean_up_tokenization_spaces=True)
        llm = AutoModelForCausalLM.from_pretrained("GroNLP/gpt2-small-italian")

        vuoti = 0
        detected = []
        punctuations = ['.', '!', '?', ';']

        for speaker_1_segments, speaker_2_segments in conversation:
            input_text = " ".join([segment['text'].strip() for segment in speaker_1_segments])
            ends_with_punctuation = any(input_text.endswith(punctuation) for punctuation in punctuations) 
            inputs = tokenizer(input_text, return_tensors="pt")

            outputs = llm(**inputs)
            logits = outputs.logits
            last_token_logits = logits[:, -2, :] if ends_with_punctuation else logits[:, -1, :]
 
            probs = F.softmax(last_token_logits, dim=-1)

            eos_tokens = ["."]
            eos_token_ids = [tokenizer.convert_tokens_to_ids(eos_token) for eos_token in eos_tokens]
            eos_token_probs = [probs[0, eos_token_id].item() for eos_token_id in eos_token_ids]
            flags = [eos_token_prob < threshold_next_token for eos_token_prob in eos_token_probs]

            if (not any(flags)):
                vuoti = vuoti + 1
                detected += [speaker_1_segments]

        score = round(4 * (vuoti / len(patient_segments)))

        return score, dict_of(detected)

class NarrowThinking(Strategy):
    '''
    A class to implement strategy to compute Narrow Thinking item
    '''

    def __init__(self) -> None:
        super().__init__(narrow_thinking_schema, {}, {})
    
    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Narrow thinking item on speaker_2
        based on the number of times speaker_2 returns on preceding topics
        in the conversation and that are initiated by them. 
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Narrow Thinking (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        
        topics = utils.topic_analysis(segments)
        narrow_thoughts = 0
        occurences = {}
        answers_count = 0

        for topic, related_items in topics.items():
        
            lst = [topic] + related_items
            answers_count = answers_count + len([answer for answer in lst if answer.speaker == speaker_2])
            consecutives = [list(map(itemgetter(1), g)) for k, g in groupby(enumerate(lst), lambda item: item[0] - item[1][0])]

            if not topic.speaker == speaker_2: continue

            for portion in consecutives:
                speaker_consecutives = [list(group) for curr_speaker, group in groupby(portion, key=lambda x: x[1])]
                first_block = speaker_consecutives[0]

                if first_block[0].speaker == speaker_2:
                    narrow_thoughts += len(first_block)
                    occurences.setdefault(topic, []).extend(first_block)


        topics = {key.text : [segment.text for segment in value] for key, value in topics.items()}
        occurences = {key.text : [segment.text for segment in value] for key, value in occurences.items()}

        score = round(4 * (narrow_thoughts / (answers_count)))

        return score, dict_of( topics, occurences, answers_count )

class Perseverance(Strategy): 
    '''
    A class to implement strategy to compute Perseverance item
    '''
    def __init__(self, cutoff:int) -> None:
        thresholds = dict_of(cutoff)
        super().__init__(perseverance_schema, {}, thresholds)

    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Perseverance item on speaker_2
        based on the number of times speaker_2 returns on preceding topics
        in the conversation. 
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Perseverance (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''

        topics = utils.topic_analysis(segments)
        occurences = {}
        counters = { topic : (0, 0) for topic in topics.keys()  }
        cutoff = self.thresholds['cutoff']
        answers_count = sum([1 for segment in segments if segment['speaker'] == speaker_2]) 

        for topic, related_items in topics.items():
            lst = [topic] + related_items
            consecutives = [list(map(itemgetter(1), g)) for k, g in groupby(enumerate(lst), lambda item: item[0] - item[1].index)]
            first = consecutives.pop(0)

            first_consecutives = [
                (first_group := next(((curr_speaker, list(group)) for curr_speaker, group in groupby(portion, key=lambda x: x[1])), ('Uknown', [])))
                for portion in consecutives
                if portion
            ]
            first_consecutives = [lst for curr_speaker, lst in first_consecutives if curr_speaker == speaker_2]
            
            if len(first_consecutives) >= cutoff:
                perseverances = sum(len(lst) for lst in first_consecutives)
                answers_to_ommit = len([answer for answer in first if answer.speaker == speaker_2])

                counters[topic] = (answers_to_ommit, perseverances)
                occurences.setdefault(topic, []).extend(chain(*first_consecutives))

        topics = {key.text : [segment.text for segment in value] for key, value in topics.items()}
        occurences = {key.text : [segment.text for segment in value] for key, value in occurences.items()}
        
        i = sum([answers_to_ommit for answers_to_ommit, perseverance in counters.values()])
        perseverances = sum([perseverance for answers_to_ommit, perseverance in counters.values()])

        score = round(4 * (perseverances / (answers_count - i)))         
         
        return score, dict_of(answers_count, topics, occurences)

class PressureToSpeech(Strategy):
    '''
    A class to implement strategy to compute PressureToSpeech item
    '''

    def __init__(self, min_num_per_min:int, max_num_per_min:int) -> None:
        """
        Parameters
        ----------
        min_num_per_min : int
            the minimum expected word per minute
        max_num_pause : int
            the maximum expected word per minute  
        """
        thresholds = dict_of(min_num_per_min, max_num_per_min)
        super().__init__(pressure_to_speech_schema, {}, thresholds)

    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Pressure to Speech item on speaker_2
        based on the average word per minute. 
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Pressure to Speech (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        min_num_per_min, max_num_per_min = self.thresholds.values()
        #per ciascun segmento di speaker raccogli total_words_segment e total_seconds_segment
        words_and_durations = [(len(obj["words"]), (obj["end"] - obj["start"])) 
                               for obj in segments if obj ["speaker"] == speaker_2] 
        word_counts, time_counters = zip(*words_and_durations)

        word_count = sum(word_counts) #somma tutti total_words_segment -> total_words
        time_duration = sum(time_counters) #somma tutti total_seconds_segment -> total_seconds

        avg_speaker_time = round(word_count / (time_duration / 60))
        norm_score = round((avg_speaker_time - min_num_per_min) / (max_num_per_min - min_num_per_min)* 4)
        score = 4 if norm_score > 4 else 0 if norm_score < 0 else norm_score

        return score, dict_of(avg_speaker_time)

class Rumination(Strategy):
    
    def __init__(self) -> None:
        super().__init__(rumination_schema, {}, {})
    
    def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
        '''
        The algorithm assumes that the given transcription is the resulting transcription of 
        a doctor patient interview where: 
            - speaker_1 is always first
            - speaker_1 mainly asks questions and speaker_2 answers them

        This algorithm computes a score for Rumination item on speaker_2
        based on the number of times speaker_2 returns on preceding topics
        in the conversation. The topics and recursions should also 
        have a negative tone. 
        
        Parameters
        ----------
        segments : list[any]
            the Whisper segments combined with speaker label information
        speaker_1 : str
            the speaker label associated to the first speaker
        speaker_2 : str
            the speaker label associated to the second speaker

        Returns
        -------
        score : int
            a score compliant to Tald scale for Rumination (0-4)
        byproduct : dict
            by products of the computation that might be of interest
        '''
        item = namedtuple('item', ['index', 'speaker', 'text', 'sentiment'])
        topics = { item(*key, utils.sentence_sentiment_analysis(key.text)) : 
                  [ item(*sentence, utils.sentence_sentiment_analysis(sentence.text)) for sentence in value] 
                  for key, value in utils.topic_analysis(segments).items()}
        counters = { topic : (0, 0) for topic in topics.keys()  }
        occurences = {}
        answers_count = 0

        for topic, related_items in topics.items():
            lst = [topic] + related_items
            answers_count = answers_count + len([answer for answer in lst if answer.speaker == speaker_2])
            consecutives = [list(map(itemgetter(1), g)) for k, g in groupby(enumerate(lst), lambda item: item[0] - item[1].index)]
        
            first = consecutives.pop(0)
        
            for portion in consecutives:
                speaker_consecutives = [list(group) for curr_speaker, group in groupby(portion, key=lambda x: x[1])]
                first_block = speaker_consecutives[0]
                if not first_block[0].speaker == speaker_1:
                
                    ruminations = [sentence for sentence in first_block if sentence.sentiment == "Negative"]
                    answers_to_ommit = len([answer for answer in first if answer.speaker == speaker_2])
                    counters[topic] = (answers_to_ommit, len(ruminations))
        
                    occurences.setdefault(topic, []).extend(ruminations)
        
        topics = {key.text : [segment.text for segment in value] for key, value in topics.items()}
        occurences = {key.text : [segment.text for segment in value] for key, value in occurences.items()}
        
        i = sum([answers_to_ommit for answers_to_ommit, ruminations in counters.values()])
        ruminations = sum([ruminations for answers_to_ommit, ruminations in counters.values()])
        
        score = round(4 * (ruminations / (answers_count - i)))
        return score, dict_of(answers_count, topics, occurences)

class Tangentiality(Strategy):
        def __init__(self) -> None:
            thresholds = dict_of(similarity_threshold=0.3)
            super().__init__(tangentiality_schema, {}, thresholds)

        def _execute_impl(self, segments: list, speaker_1: str, speaker_2: str) -> tuple[int, dict]:
            #Riorganizza il corpus in una lista di coppie (domanda clinico, risposte paziente)
            threshold =  self.thresholds['similarity_threshold']
            speech = [(curr_speaker, [segment for segment in group]) 
                             for curr_speaker, group in groupby(segments, key=lambda x: x["speaker"]) ]
            question_answers = zip([segments[-1] for speaker, segments in speech if speaker == speaker_1], 
                                       [segments for speaker, segments in speech if speaker == speaker_2])

            #Inizializza contatori
            model = SentenceTransformer('efederici/sentence-BERTino', tokenizer_kwargs={ "clean_up_tokenization_spaces" : True})
            lst = list(question_answers)
            tangent_dict = []

            for question, answers in lst:
                if len(answers) == 0: continue
                #Computa embeddings della domanda e delle risposte
                question_embedding = model.encode([question["text"]])
                answers_embeddings = [model.encode([answer["text"]]) for answer in answers] 

                #Computa la cosine similarity tra domanda e risposta
                cosine_similarity_arr = [cosine_similarity(question_embedding, answer_embedding)[0][0] for answer_embedding in answers_embeddings]
                pairwise = list(zip(cosine_similarity_arr[:-1], cosine_similarity_arr[1:]))

                number_of_gaps, normalized_gaps, tangency, brief = 0, 0, False, len(pairwise) == 0
                tangent_counter_dict = [{"score" : 0, "first" : x, "second" : y} for x, y in pairwise]

                #se la conversazione inizia in maniera sensata e non è breve
                if cosine_similarity_arr[0] > threshold and not brief: 
                    #Conta il numero di volte che c'è una dimunuzione della cosine similarity (number_of_gaps) tra una risposta e l'altra
                    #Normalizza in un range [0, 1] prendendo (number_of_gaps) / (numero di coppie di segmenti consecutivi)
                    tangent_counter_dict = [{"score" : 1, "first" : x, "second" : y} if y - x < 0 
                                        else {"score" : 0, "first" : x, "second" : y} for x, y in pairwise]

                    number_of_gaps = sum(pair["score"] for pair in tangent_counter_dict)
                    normalized_gaps = number_of_gaps / len(pairwise)
                    tangency = True

                
                tangent_dict.append({**dict_of(
                    question, answers, tangent_counter_dict,
                    number_of_gaps, normalized_gaps), 
                    "tangency" : tangency, "brief": brief})


            bins = [0.1, 0.5, 0.75, 0.9]
            sum_tan_score = sum(obj["normalized_gaps"] for obj in tangent_dict)
            average_norm_tan = sum_tan_score / len(tangent_dict)
            score = int(digitize(average_norm_tan, bins))

            return score, dict_of(tangent_dict)
        
class Blocking(Strategy):
    def __init__(self, pause = 2.0) -> None:
            thresholds = dict_of(pause)
            super().__init__(blocking_schema, {}, thresholds)

    def _execute_impl(self, segments, speaker_1, speaker_2):
        speaker_map = {
    "PATIENT": "SPEAKER 2",
    "CLINICIAN": "SPEAKER 1"
	}
	
        corpus = [
        [f"{speaker_map[entry['speaker']]}: {entry['text'].strip()}", str(entry["start"]), str(entry["end"])]
        for entry in segments
    ]
        count_blocking = 0 
        count_answer = 0
        corpus_cleaned = [sentence[0].replace("SPEAKER 1: ", "").replace("SPEAKER 2: ", "").strip() for sentence in corpus]
        sentences_semantic = []
        i=0
        try:
            tokenizer = AutoTokenizer.from_pretrained("iproskurina/tda-itabert-ita-cola")
            model = AutoModelForSequenceClassification.from_pretrained("iproskurina/tda-itabert-ita-cola")
        
            #calcolo valore semantico
            for sentence in corpus_cleaned:
                inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
                outputs = model(**inputs)
                predictions = outputs.logits.argmax(dim=-1)
                sentences_semantic.append(str(predictions.item()))
                corpus[i].append(str(predictions.item()))
                i=i+1
            
        finally:
            del tokenizer
            del model
            empty_cache()
            collect()
            
        #calcolo pausa lunga
        pause = self.thresholds['pause']
        end = 0
        i = 0
        patientSpoke = False
        for sentence in corpus:
            if(sentence[0].startswith("SPEAKER 1:")):
                if((float(sentence[1]) > float(end+pause)) and patientSpoke and corpus[i-1][3]=='0'):
                    print("Long pause detected from: ", end, " to: ", sentence[1], "for sentence: ", sentence[0])
                    count_blocking = count_blocking + 1
            else:
                count_answer = count_answer + 1
                patientSpoke = True
                end = float(sentence[2])
            i = i + 1
        
        def finalScore(counter_answer):

            if (counter_answer - 1)==0:

                return 'La conversazione è troppo breve per essere valutata'

            else:
                score_bloking = count_blocking/counter_answer
                normalized_score_bloking = score_bloking * 4
                print(normalized_score_bloking)
                
                if normalized_score_bloking > 4:
                    normalized_score_bloking = math.floor(normalized_score_bloking)
                    return normalized_score_bloking
                else:
                    if normalized_score_bloking - math.floor(normalized_score_bloking) >= 0.5:
                        final_score_bloking_approximate = math.ceil(normalized_score_bloking)  
                    else:
                        final_score_bloking_approximate = round(normalized_score_bloking)

                return final_score_bloking_approximate 

        score_bloking = finalScore(count_answer)
        return score_bloking, {}
    
class Derailment(Strategy):
    def __init__(self):
        thresholds = dict_of(similarity_threshold=0.3)
        super().__init__(derailment_schema, {}, thresholds)
    
    def _execute_impl(self, segments, speaker_1, speaker_2):
        speaker_map = {
    "PATIENT": "SPEAKER 2",
    "CLINICIAN": "SPEAKER 1"
    }

        corpus = [
        f"{speaker_map[entry['speaker']]}: {entry['text'].strip()}"
        for entry in segments
    ]

        subsets = []
        current_subset = []
        counter_answer = 0

        #crea dei subset inerenti a domande + risposta del paziente. Ad ogni domanda del medico se ne crea uno nuovo
        #esempio risultato finale: subset=[ [domanda1, risposta1, ..., rispostaN], [domanda2, risposta1, ..., rispostaN], ... , [domandaN, risposta1, ... rispostaN]]
        for idx, sentence in enumerate(corpus):
            if sentence.startswith("SPEAKER 1"):
                current_subset = []
                current_subset.append({"idx": idx, "sentence": sentence})
                subsets.append(current_subset)

            else:
                counter_answer = counter_answer + 1
                current_subset.append({"idx": idx, "sentence": sentence})

        #corpus_cleaned = [sentence.replace("SPEAKER 1: ", "CLINICIAN: ").replace("SPEAKER 2: ", "PATIENT: ").strip() for sentence in corpus]
        #corpus_cleaned = [sentence.replace("SPEAKER 1: ", "").replace("SPEAKER 2: ", "").strip() for sentence in corpus]
        corpus_cleaned = []
        for sentence in corpus:
            corpus_cleaned += [self.clean(sentence)]
        #print(corpus_cleaned)

        model = SentenceTransformer('efederici/sentence-BERTino')
        sentence_embeddings = model.encode(corpus_cleaned)

        # imposto una soglia per la similarità
        threshold = self.thresholds['similarity_threshold']

        # inizializzazione delle variabili per il conteggio degli argomenti
        counter_perseverance = 0
        counter_derailment = 0
        topics_dict = {}
        score_perseverance = 0
        
        # ricerca delle coppie di frasi simili
        for subset in subsets:
            for i in range(len(subset) - 1):
                if(i == 0):
                    print("Nuova domanda dal medico avente topic: ", subset[i]["sentence"])
                    new_topic = subset[i]["sentence"]
                    #mappa dove la chiave è la frase, il value è una lista contenente (al momento) solo la frase stessa
                    topics_dict[new_topic] = [subset[i]["sentence"]]
                idx = subset[i]["idx"]
                idx1 = subset[i + 1]["idx"]
                

                # confronto la frase corrente con la successiva
                similarity = cosine_similarity([sentence_embeddings[idx]], [sentence_embeddings[idx1]])[0][0]
                print('1*:',subset[i]["sentence"] + '\n2*: ' + subset[i+1]["sentence"], '\n\tSimil: ', similarity)

                #prendo l'ultimo topic dalla mappa
                last_topic = list(topics_dict.keys())[-1]

                #confronto la frase successiva con l'ultimo topic
                similarity_1 = cosine_similarity([sentence_embeddings[idx1]], model.encode([last_topic]))[0][0]

                print('FRASE*:',subset[i+1]["sentence"],'\nTOPIC*:',last_topic,'\n\tSimil*: ',similarity_1)
                print('\n\n')

                # se la similarità supera la soglia sia tra le due frasi che tra la frase successiva e il topic, 
                # aggiungo la frase successiva alla lista del topic corrispondente
                if similarity >= threshold and similarity_1 >= threshold:
                    topics_dict[last_topic].append(subset[i+1]["sentence"])

                else:
                    # se la similarità è inferiore alla soglia, cerco prima se la frase corrente appartiene ad un topic esistente
                    print('Similarità non sufficiente')
                    print('Ricerca nei topic...')
                    #ricerca per tutte le chiavi la similarity
                    keys_list = list(topics_dict.keys())
                    for key in keys_list:
                        similarity = cosine_similarity([sentence_embeddings[idx1]], model.encode([key]))[0][0]
                        print('Topic: ', key, "\n\tSimilarity:",similarity)

                        # se la frase successiva appartiene ad un topic esistente, la aggiungo alla lista del topic 
                        # ed incremento il counter per indicare che c'è stata perseveranza (ritorno ad un argomento trattato in precedenza)
                        # se la trovo fermo il ciclo
                        if similarity >= threshold:
                            print("Perseveranza per", subset[i+1]["sentence"], "\nRitorno al topic:", key)
                            topics_dict[key].append(subset[i+1]["sentence"] + ' ->  +1')
                            counter_perseverance = counter_perseverance + 1
                            print('counter perseverance: ',counter_perseverance, "\n\n")
                            break
                        
                        # se la frase successiva non appartiene ad alcun topic esistente, creo un nuovo topic con la frase come chiave
                        else:
                            #sono arrivata alla fine delle chiavi
                            if key == keys_list[-1]:
                                #nuovo topic perchè mi sono discostato solo dall'ultimo topic e creo un nuovo topic
                                if(similarity_1 < threshold):
                                    counter_derailment = counter_derailment+1
                                    print("Deragliamento per:\t", subset[i+1]["sentence"], "\nderagliamento: ", counter_derailment)
                                new_topic = subset[i+1]["sentence"]
                                topics_dict[new_topic] = [subset[i+1]["sentence"]]
                                print("New topic: ", subset[i+1]["sentence"], "\n\n")
                                break   
                        

        print('Il numero totale di domande fatte è:', len(subsets))
        print("Il numero di volte che si è ritornati all'argomento precedente durante la conversazione è:", counter_perseverance)
        print("Il numero di volte che si è deragliati è:", counter_derailment)

        def finalScore(counter_answer):

            if (counter_answer - 1)==0:

                return 'La conversazione è troppo breve per essere valutata'
            
            else:
                score_derailment = (counter_derailment)/(counter_answer)
                score_perseverance = (counter_perseverance) / (counter_answer)
                normalized_score_perserverance = score_perseverance * 4
                normalized_score_derailment = score_derailment * 4
                print(normalized_score_perserverance)
                print(normalized_score_derailment)

                if normalized_score_perserverance > 4:
                    normalized_score_perserverance = math.floor(normalized_score_perserverance)
                    final_score_perseverance_approximate = 4
                else:
                    if normalized_score_perserverance - math.floor(normalized_score_perserverance) >= 0.5:
                        final_score_perseverance_approximate = math.ceil(normalized_score_perserverance)  
                    else:
                        final_score_perseverance_approximate = round(normalized_score_perserverance)
                
                if normalized_score_derailment > 4:
                    normalized_score_derailment = math.floor(normalized_score_derailment)
                    final_score_derailment_approximate = 4
                else:
                    if normalized_score_derailment - math.floor(normalized_score_derailment) >= 0.5:
                        final_score_derailment_approximate = math.ceil(normalized_score_derailment)  
                    else:
                        final_score_derailment_approximate = round(normalized_score_derailment)

                return final_score_perseverance_approximate,final_score_derailment_approximate 

        score_perseverance, score_derailment = finalScore(counter_answer)


        print('Score perseverance: ', score_perseverance)
        print('Score derailment: ', score_derailment)

        return score_derailment, dict_of(counter_answer, topics_dict, counter_derailment)

    def clean(self, sentence):
        stemmer = PorterStemmer()
        sentence_cleaned = sentence.replace("SPEAKER 1: ", "").replace("SPEAKER 2: ", "").strip()
        cleaned_sentence =''
        # Rimuovi punteggiatura e numeri
        sentence = re.sub(r'[^\w\s]', '', sentence_cleaned)
        sentence = re.sub(r'\d+', '', sentence_cleaned)
        # Converti a minuscolo
        sentence = sentence.lower()
        # Rimozione stopwords
        stop_words = set(stopwords.words('italian'))
        words = sentence_cleaned.split()
        words = [word for word in words if word not in stop_words]
        # Stemming
        sentence = cleaned_sentence.join(' ').join(words)
        return sentence
    
class Clanging(Strategy):
    def __init__(self, low_treshold=0.045, high_treshold=0.3):
        thresholds = dict_of(low_treshold, high_treshold)
        super().__init__(clanging_schema, {}, thresholds)
    
    def _execute_impl(self, segments, speaker_1, speaker_2):
        speaker_map = {
        "PATIENT": "SPEAKER 2",
        "CLINICIAN": "SPEAKER 1"
        }
        counter_answer = 0
        counter_clanging = 0
 
        corpus = [
            f"{speaker_map[entry['speaker']]}: {entry['text'].strip()}"
            for entry in segments
        ]
        for sentence in corpus:
            value_clanging, value_question = self.calculateClanging(sentence[0])
            counter_clanging = counter_clanging + value_clanging
            counter_answer = counter_answer + value_question

            def finalScore(counter_answer):

                if (counter_answer - 1)==0:

                    return 'La conversazione è troppo breve per essere valutata'

                else:
                    print("counter_clanging: ", counter_clanging, "counter answer: ", counter_answer)
                    score_clanging = (counter_clanging)/(counter_answer)
                    normalized_score_clanging = score_clanging * 4
                    print('normalized score clanging', normalized_score_clanging)
                    
                    if normalized_score_clanging > 4:
                        normalized_score_clanging = math.floor(normalized_score_clanging)
                        final_score_clanging_approximate = 4
                    else:
                        if normalized_score_clanging - math.floor(normalized_score_clanging) >= 0.5:
                            final_score_clanging_approximate = math.ceil(normalized_score_clanging)  
                        else:
                            final_score_clanging_approximate = round(normalized_score_clanging)

                    return final_score_clanging_approximate 

        score_clanging = finalScore(counter_answer)
        return score_clanging, {}
    
    def calculateClanging (self, sentence):

        low_treshold = self.thresholds['low_treshold']
        high_treshold = self.thresholds['high_treshold']
        print("Sentence: ",sentence)
        if(sentence.startswith("SPEAKER 1:")):
            return 0,0
        
        cleaned_sentence = self.clean(sentence)
        print("Cleaned dentence: ",cleaned_sentence)

        phonema_sentence = self.phonemizer(cleaned_sentence)
        print("Phonema sentence: ",phonema_sentence)

        densita = self.count_density(phonema_sentence,cleaned_sentence)
        print("Density: ",densita)
        
        semantic_value = 1
        if(densita != 0):
            semantic_value = self.semantic(sentence)
            print("Semantic value: ", semantic_value)

        final_score = self.punteggio_finale(float(densita),int(semantic_value))
        print("Final score: ", final_score, "\n")
        
        #print(sentence,'\n',cleaned_sentence, '\n',phonema_sentence,'\n',semantic_value,'\n',densita,'\n',final_score,'\n')
        if (final_score>high_treshold):
            return 1.5, 1.5
        elif (final_score>low_treshold):
            return 1, 1
        else:
            return 0, 1
        
    #Step 1 pulizia frase
    def clean(self, sentence):
        sentence_cleaned = sentence.replace("SPEAKER 1: ", "").replace("SPEAKER 2: ", "").strip()
        cleaned_sentence =''
        # Rimuovi punteggiatura e numeri
        sentence = re.sub(r'[^\w\s]', '', sentence_cleaned)
        sentence = re.sub(r'\d+', '', sentence)
        # Converti a minuscolo
        sentence = sentence.lower()
        # Rimozione stopwords
        stop_words = set(stopwords.words('italian'))
        words = sentence.split()
        words = [word for word in words if word not in stop_words]
        sentence = cleaned_sentence.join(' ').join(words)
        return sentence

    #Step 2 phonemi
    def phonemizer(self, cleaned_sentence):
        phonemes = phonemize(cleaned_sentence, language='it')
        phonema_sentence = phonemes.strip()
        return phonema_sentence

    #Step 3 valore semantico
    def semantic(self, sentence):
        try:
            tokenizer = AutoTokenizer.from_pretrained("iproskurina/tda-itabert-ita-cola")
            model = AutoModelForSequenceClassification.from_pretrained("iproskurina/tda-itabert-ita-cola")
            inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
            outputs = model(**inputs)
            predictions = outputs.logits.argmax(dim=-1)
            value=str(predictions.item())
            return value
        finally:
            del tokenizer
            del model
            empty_cache()
            collect()
    #Step 4 conta densita ripetizioni
    def count_density(self, sentence,cleaned_sentence):
        trigrams = self.count_trigram_repetitions(sentence)
        somma = sum(trigrams.values())
        densita = somma/len(cleaned_sentence)
        return densita

    # Step 4.1 conta ripetizioni di 3 phonemi
    def count_trigram_repetitions(self, sentence):
        # Normalize the sentence by converting it to lowercase
        sentence = sentence.lower()

        # Dictionary to store the count of each trigram
        trigram_counts = {}

        # Iterate through the sentence and extract trigrams
        for i in range(len(sentence) - 2):
            # Extract a group of 3 letters (trigram)
            trigram = sentence[i:i+3]

            # Ignore non-alphabetic trigrams (e.g., "a b", "1ab")
            if not trigram.isalpha():
                continue

            # Count the trigram in the dictionary
            if trigram in trigram_counts:
                trigram_counts[trigram] += 1
            else:
                trigram_counts[trigram] = 1
        frequent_trigrams = {trigram: count for trigram, count in trigram_counts.items() if count > 2}
        if not frequent_trigrams: frequent_trigrams = {'': 0}
        return frequent_trigrams

    #Step 5 calcolo punteggio finale
    def punteggio_finale(self, punteggio_fonetico, punteggio_semantico):
        punteggio_semantico= punteggio_semantico * -1 + 1
        punteggio_combinato = (0.7 * punteggio_fonetico) + (0.3 * punteggio_semantico)
        return punteggio_combinato

    