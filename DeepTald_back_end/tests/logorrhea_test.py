from scale_items import Logorrhea
from pytest import mark, fixture, raises
from json import load

#################### CATEGORY PARTITION PARAMETERS #########################
# segments - Whisper transcription segments (constant)
# weights - R^2 space parameter containing all possible combinations of (interruptions_weight, response_length_weight)
# min_value_avg_response_length - minimum average of the patient spoken time
# max_value_avg_response_length - maximum average of the patient spoken time
###################### CATEGORY PARTITION CHOICES ##########################
# 
# segments ->
#   interruptions: 
#       - 0 interruptions
#       - more than 1 interruption
#   average length response:
#       - less than 15 words
#       - more than 15 words
#
# min_value_avg_response_length -> ranges: negative (error), [10 - 20] words, [0 - 10] words
# max_value_avg_response_length -> ranges: negative (error), [0 - 10] words, [10 - 20] words
# weights -> sum_of_weights: w1 + w2 = 1, w1 + w2 != 1 (error) 
#
# property for min_value_avg_response_length.[10 - 20] -> range_check and only once
# constraint for max_value_avg_response_length.[0 - 10]: if range_check == True
############################ TEST FRAMES ####################################
# TF1 : negative, [0-10], sum = 1
# TF2 : [0-10], negative, sum = 1
# TF3 : [0-10], [10-20], sum != 1
# TF4 : [10-20], [0-10], sum = 1
# TF5 : 0, 10-, [0-10], [10-20], sum = 1
# TF6 : 0, 10+, [0-10], [10-20], sum = 1
# TF7 : 1+, 10-, [0-10], [10-20], sum = 1
# TF8 : 1+, 10+, [0-10], [10-20], sum = 1


@fixture
def transcription_1():
    path = "tests/resources/logorrhea/test_transcription_1.json"
    with open(path, "r") as fp: return load(fp)
    
@fixture
def transcription_2():
    path = "tests/resources/logorrhea/test_transcription_2.json"
    with open(path, "r") as fp: return load(fp)
    
@fixture
def transcription_3():
    path = "tests/resources/logorrhea/test_transcription_3.json"
    with open(path, "r") as fp: return load(fp)

@fixture
def transcription_4():
    path = "tests/resources/logorrhea/test_transcription_4.json"
    with open(path, "r") as fp: return load(fp)

def test_01 ():
    with raises(ValueError):
        Logorrhea(0.5, 0.5, -1, 10)

def test_02 ():
    with raises(ValueError):
        Logorrhea(0.5, 0.5, 5, -5)

def test_03 ():
    with raises(ValueError):
        Logorrhea(0.5, 0.4, 10, 20)

def test_04 ():
    with raises(ValueError):
        Logorrhea(0.5, 0.5, 10, 5)

def test_05 (transcription_1):
    segments = transcription_1
    scale_item = Logorrhea(0.5, 0.5, 10, 20)

    result = scale_item.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 1

def test_06 (transcription_2):
    segments = transcription_2
    scale_item = Logorrhea(0.5, 0.5, 10, 20)

    result = scale_item.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 3

def test_07 (transcription_3):
    segments = transcription_3
    scale_item = Logorrhea(0.5, 0.5, 0, 20)

    result = scale_item.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 4

def test_08 (transcription_4):
    segments = transcription_4
    scale_item = Logorrhea(0.5, 0.5, 0, 20)

    result = scale_item.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 4