from scale_items import SlowedThinking
from pytest import fixture, raises
from json import load

#################### CATEGORY PARTITION PARAMETERS #########################
# segments - Whisper transcription segments (constant)
# weights - R^2 space parameter containing all possible combinations of (pause_time_weight, response_time_weight)
# min_value_response_time - minimum response time of the patient that is registered
# max_value_response_time - maximum response time of the patient that is registered
###################### CATEGORY PARTITION CHOICES ##########################
# 
# segments ->
#   average response time
#       - less than 1 sec
#       - more than 1 sec
#   time between words
#       - less than 5% of total patient time
#       - more than 5% of total patient time
#
# min_value_response_time -> ranges: negative (error), [2 - 5], [0 - 1]
# max_value_response_time -> ranges: negative (error), [0 - 1], [2 - 5]
# weights -> sum_of_weights: w1 + w2 = 1, w1 + w2 != 1 (error) 
#
# property for min_value_response_time.[2 - 5] -> range_check and unique
# constraint for max_value_response_time.[0 - 1]: if range_check == True
############################ TEST FRAMES ####################################
# TF1 : negative, [0 - 1], sum = 1
# TF2 : [0 - 1], negative, sum = 1
# TF3 : [0 - 1], [2 - 5], sum != 1
# TF4 : [2 - 5], [0 - 1], sum = 1
# TF5 : 1-, 5%-, [0 - 1], [2 - 5], sum = 1
# TF6 : 1-, 5%+, [0 - 1], [2 - 5], sum = 1
# TF7 : 1+, 5%-, [0 - 1], [2 - 5], sum = 1
# TF8 : 1+, 5%+, [0 - 1], [2 - 5], sum = 1

@fixture
def transcription_1():
    with open("tests/resources/slowed_thinking/test_transcription_1.json", "r") as fp:
        return load(fp)

@fixture
def transcription_2():
    with open("tests/resources/slowed_thinking/test_transcription_2.json", "r") as fp:
        return load(fp)

@fixture
def transcription_3():
    with open("tests/resources/slowed_thinking/test_transcription_3.json", "r") as fp:
        return load(fp)

@fixture
def transcription_4():
    with open("tests/resources/slowed_thinking/test_transcription_4.json", "r") as fp:
        return load(fp)

    
def test_01 ():
    with raises(ValueError):
        SlowedThinking(0.5, 0.5, -1, 1)

def test_02 ():
    with raises(ValueError):
        SlowedThinking(0.5, 0.5, 0, -1)

def test_03 ():
    with raises(ValueError):
        SlowedThinking(0.5, 0.6, 0, 2)

def test_04 ():
    with raises(ValueError):
        SlowedThinking(0.5, 0.5, 2, 0)

def test_05 (transcription_1):    
    segments = transcription_1
    item_scale = SlowedThinking(0.5, 0.5, 0, 2)
    
    result = item_scale.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 0

def test_06 (transcription_2):
    segments = transcription_2
    item_scale = SlowedThinking(0.5, 0.5, 0, 2)
    
    result = item_scale.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 1

def test_07 (transcription_3):
    segments = transcription_3
    item_scale = SlowedThinking(0.5, 0.5, 0, 2)
    
    result = item_scale.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 3

def test_08 (transcription_4):
    segments = transcription_4
    item_scale = SlowedThinking(0.5, 0.5, 0, 2)
    
    result = item_scale.execute(segments, "CLINICIAN", "PATIENT")
    assert result[0] == 3