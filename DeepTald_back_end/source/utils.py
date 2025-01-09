from collections import namedtuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch import nn, tensor
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def counter_interruption(segments, speaker_1, speaker_2):

  interruption_count = 0
  question_count = 0

  for i in range(len(segments) - 1):
      current_segment = segments[i]
      next_segment = segments[i + 1]

      current_speaker = current_segment['speaker']
      next_speaker = next_segment['speaker']

      if current_speaker == speaker_1 and next_speaker == speaker_2:
          question_count += 1

          if current_segment['end'] >= (next_segment['start'] - 0.20):
              interruption_count += 1

  # Aggiungi il controllo per l'ultimo segmento se necessario
  if segments and segments[-1]['speaker'] == speaker_1:
        question_count += 1

  interruption_score = interruption_count / question_count

  return interruption_score, question_count, interruption_count

def calculate_speaking_time(segments, speaker):

    total_speaking_time_speaker1 = 0

    for i, current_segment in enumerate(segments):
        if current_segment['speaker'] == speaker:
            start_time = current_segment['words'][0]['start']

            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                end_time = next_segment['words'][0]['start']
            else:
                end_time = current_segment['words'][-1]['end']

            speaking_time = end_time - start_time
            total_speaking_time_speaker1 += speaking_time

    return total_speaking_time_speaker1

def avg_response_length(segments, speaker):
    patient_responses = 0
    segments_length = len(segments)

    for i in range(segments_length):
        current_segment = segments[i]

        if current_segment['speaker'] == speaker:
            if i == segments_length - 1 or segments[i+1]['speaker'] != speaker:
                patient_responses += 1

    total_words = sum(word["speaker"] == speaker for segment in segments for word in segment["words"])
    average_response_length = total_words / patient_responses

    return average_response_length

def response_time(segments, speaker_1, speaker_2):
   
  speaker1_responses = []
  speaker2_questions = []
  total_response_time = 0

  for i in range(len(segments) - 1):
      current_segment = segments[i]
      next_segment = segments[i+1]

      if current_segment['speaker'] == speaker_1:
          speaker2_questions.append(current_segment['text'])
          
          if next_segment['speaker'] == speaker_2:
              response_time = next_segment['start'] - current_segment['end']
              if response_time < 0:
                  response_time = 0
              speaker1_responses.append(response_time)
              total_response_time += response_time

  average_response_time = sum(speaker1_responses) / len(speaker1_responses)

  return average_response_time

def pause_time_between_words(segments, speaker):

    last_end_time_speaker1 = None
    total_pause_time_speaker1 = 0

    for segment in segments:
        speaker = segment['speaker']
        
        if speaker == speaker:
            for word in segment['words']:
                start_time = word['start']
                end_time = word['end']

                if last_end_time_speaker1 is not None:
                    pause_time = start_time - last_end_time_speaker1
                    if pause_time > 0:
                        total_pause_time_speaker1 += pause_time
                
                last_end_time_speaker1 = end_time
    
    return total_pause_time_speaker1

def topic_analysis(segments, similarity_threshold = 0.3):
    item = namedtuple('item', ['index', 'speaker', 'text'])
    model = SentenceTransformer('efederici/sentence-BERTino', tokenizer_kwargs={ "clean_up_tokenization_spaces" : True})
    embeddings = [[embedding] for embedding in model.encode([segment["text"] for segment in segments])]
    similarity = lambda x, y : cosine_similarity(x, y)
    condition = lambda current, others : current >= similarity_threshold or any([cosine >= similarity_threshold for cosine in others])
    list_iterator = ((index, segment['speaker'], segment['text']) for index, segment in enumerate(segments))
    list_similarity = lambda lst, i: (similarity(curr_embedding, embeddings[index])[0][0].item() 
                        for index, speaker, argument in lst[i:])

    last_topic = list_iterator.__next__()
    topics = {item(*last_topic) : []}
    
    for curr_index, curr_segment_speaker, curr_segment_text in list_iterator:
        last_topic_sentences, (lst_index, lst_topic_initiator, lst_topic_key) = topics[last_topic], last_topic
        curr_embedding = embeddings[curr_index]
        last_topic_embedding = embeddings[lst_index]

        sim_last_topic = similarity(curr_embedding, last_topic_embedding)[0][0].item()        
        sim_previous = list(list_similarity(last_topic_sentences, -1))
        sim_other_topics = (((index, speaker, argument), similarity(curr_embedding, embeddings[index]), list_similarity(lst, -1)) 
                            for (index, speaker, argument), lst in topics.items())
    
        #Caso 1: la frase corrente ha a che fare con l'ultimo argomento
        if condition(sim_last_topic, sim_previous):
            topics[last_topic].append(item(curr_index, curr_segment_speaker, curr_segment_text))
        #Caso 2: La frase corrente ha a che fare con un argomento precedente
        elif len(sim_another_topic := {key : [similarity] + list(similarities) 
                                       for key, similarity, similarities in sim_other_topics 
                                       if condition(similarity, similarities)}) > 0:
            
            #prendere l'argomento con più elevata similarità
            last_topic = max(sim_another_topic, key=lambda k: max(sim_another_topic[k]))
            topics[last_topic].append(item(curr_index, curr_segment_speaker, curr_segment_text))
        #Caso 3: La frase non ha a che fare con nessuno degli argomenti discussi
        else:
            last_topic = item(curr_index, curr_segment_speaker, curr_segment_text)
            topics[last_topic] = [] 

    return topics

def sentence_sentiment_analysis(sentence)->str:
    tokenizer = AutoTokenizer.from_pretrained("neuraly/bert-base-italian-cased-sentiment")
    model = AutoModelForSequenceClassification.from_pretrained("neuraly/bert-base-italian-cased-sentiment")
    input_ids = tokenizer.encode(sentence, add_special_tokens=True)
            
    tensor_val = tensor(input_ids).long()
    tensor_val = tensor_val.unsqueeze(0)
    logits = model(tensor_val).logits
    proba = nn.functional.softmax(logits, dim=1)
    negative, neutral, positive = proba[0]

    sentiment_scores = {'Negative': negative.item(), 'Neutral': neutral.item(), 'Positive': positive.item()}
    result = max(sentiment_scores, key=sentiment_scores.get)

    return result