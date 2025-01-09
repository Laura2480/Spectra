from source.scale_items import LossOfThought
from pytest import fixture, raises
from json import load

#DA MODIFICARE GLI ESITI

#################### CATEGORY PARTITION PARAMETERS #########################
# segments - Whisper transcription segments
# threshold - range of the pause between PATIENT spoken words
###################### CATEGORY PARTITION CHOICES ##########################
#
# segments
#   fill: 
#       - empty (error)
#       - not empty
#   pauses:
#      - patient words with less than 3 sec pause (A)
#      - patient words with more than 3 sec pause (B)
# threshold -> ranges: negative (error), [0 - 3] sec, more than 3 sec
#
############################ TEST FRAMES ####################################
# TF1 : empty, A, [0 - 3] 
# TF2 : not empty, A, negative
# TF3 : not empty, A, [0 - 3]
# TF4 : not empty, A, more than 3 sec
# TF5 : not empty, B, [0 - 3]
# TF6 : not empty, B, more than 3 sec

@fixture
def transcription_1():
    with open("tests/resources/loss_of_thought/test_transcription_1.json", "r") as fp:
        return load(fp)

@fixture
def transcription_2():
    with open("tests/resources/loss_of_thought/test_transcription_2.json", "r") as fp:
        return load(fp)

def test_01():
    scale_item = LossOfThought()
    with raises(ValueError):
        scale_item.execute([], "CLINICIAN", "PATIENT")
    
    with raises(ValueError):
        scale_item.execute(None, "CLINICIAN", "PATIENT")
    

def test_02():
    pass

def test_03(transcription_1):
    scale_item = LossOfThought()
    result, byproduct = scale_item.execute(transcription_1, "CLINICIAN", "PATIENT")

    assert result == 0

def test_04(transcription_1):
    scale_item = LossOfThought()
    result, byproduct = scale_item.execute(transcription_1, "CLINICIAN", "PATIENT")

    assert result == 0

def test_05(transcription_2):
    scale_item = LossOfThought()
    result, byproduct = scale_item.execute(transcription_2, "CLINICIAN", "PATIENT")

    assert result == 0

def test_06(transcription_2):
    scale_item = LossOfThought()
    result, byproduct = scale_item.execute(transcription_2, "CLINICIAN", "PATIENT")

    assert result == 0