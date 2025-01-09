from scale_items import Perseverance
from pytest import raises, fixture
from json import load

#################### CATEGORY PARTITION PARAMETERS #########################
# segments - Whisper transcription segments
###################### CATEGORY PARTITION CHOICES ##########################
#
# segments -> 
# fill: empty (errore), not empty
# return: 0 returns, +1 return
#
############################ TEST FRAMES ####################################
# TF1 : empty, 0 returns
# TF2 : not empty, 0 returns
# TF3 : not empty, +1 returns

@fixture
def transcription_1():
    with open("tests/resources/perseveranza/test_transcription_1.json", "r") as fp:
        return load(fp)
    
@fixture
def transcription_2():
    with open("tests/resources/perseveranza/test_transcription_2.json", "r") as fp:
        return load(fp)

def test_01():
    scale_item = Perseverance(0)

    with raises(ValueError):
        scale_item.execute(None, "CLINICIAN", "PATIENT")
        
    with raises(ValueError):
        scale_item.execute([], "CLINICIAN", "PATIENT")

def test_02(transcription_1):
    scale_item = Perseverance(0)

    score, byproduct = scale_item.execute(transcription_1, "CLINICIAN", "PATIENT")
    assert score == 0

def test_03(transcription_2):
    scale_item = Perseverance(0)

    score, byproduct = scale_item.execute(transcription_2, "CLINICIAN", "PATIENT")
    assert score == 4
    assert sum([len(values) for key, values in byproduct["occurences"].items()]) == 2