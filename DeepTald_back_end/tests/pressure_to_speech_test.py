from scale_items import PressureToSpeech
from pytest import fixture, raises
from json import load

#################### CATEGORY PARTITION PARAMETERS #########################
# segments - Whisper transcription segments
# min_num_per_min - minimum word per minute registered (non severe) 
# max_num_per_min - maximum word per minute registered (severe case)
###################### CATEGORY PARTITION CHOICES ##########################
#
# segments -> 
#   average:
#       - less than 200 words per minute (A)
#       - more than 200 words per minute (B)
# min_num_per_min: negative (error), [0 - 150], more than 150
# max_num_per_min: negative (error), [0 - 150], more than 150
# 
# property for max_num_per_min.[0 - 150] -> checkMax
# constraint for min_num_per_min.more_than_150 -> if checkMax == True
############################ TEST FRAMES ####################################
# TF1 : A, negative, more than 150
# TF2 : B, [0 - 150], negative
# TF3 : A, [0 - 150], [0 - 150]
# TF4 : A, [0 - 150], more than 150
# TF5 : A, more than 150, [0 - 150]
# TF6 : B, [0 - 150], [0 - 150]
# TF7 : B, [0 - 150], more than 150

@fixture
def transcription_1():
    with open("tests/resources/pressure_to_speech/test_transcription_1.json", "r") as fp:
        return load(fp)
    
@fixture
def transcription_2():
    with open("tests/resources/pressure_to_speech/test_transcription_2.json", "r") as fp:
        return load(fp)

def test_01():
    with raises(ValueError):
        PressureToSpeech(-200, 200)

def test_02():
    with raises(ValueError):
        PressureToSpeech(200, -200)

def test_03(transcription_1):
    scale_item = PressureToSpeech(80, 150)
    score, byproduct = scale_item.execute(transcription_1, "CLINICIAN", "PATIENT")

    assert score == 3
    assert byproduct["avg_speaker_time"] in range(132, 136)
 
def test_04(transcription_1):
    scale_item = PressureToSpeech(80, 250)
    score, byproduct = scale_item.execute(transcription_1, "CLINICIAN", "PATIENT")

    assert score == 1
    assert byproduct["avg_speaker_time"] in range(132, 136)

def test_05():
    with raises(ValueError):
        PressureToSpeech(250, 100)

def test_06(transcription_2):
    scale_item = PressureToSpeech(80, 150)
    score, byproduct = scale_item.execute(transcription_2, "CLINICIAN", "PATIENT")

    assert score == 4
    assert byproduct["avg_speaker_time"] in range(240, 242)

def test_07(transcription_2):
    scale_item = PressureToSpeech(80, 250)
    score, byproduct = scale_item.execute(transcription_2, "CLINICIAN", "PATIENT")

    assert score == 4
    assert byproduct["avg_speaker_time"] in range(240, 242)