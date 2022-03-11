import pandas as pd
import json
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    AnalyzeSentimentAction,
)

credential = AzureKeyCredential("2b696be1f05941e08e836bd3cb35401d")
endpoint="https://genexcognitive.cognitiveservices.azure.com/"
text_analytics_client = TextAnalyticsClient(endpoint, credential)

speech_config = speechsdk.SpeechConfig(subscription='dd0ca7de2f5148b4a16f9a08b74623b0',
                                       region='southafricanorth')
speech_config.speech_recognition_language="en-US"
# audio_config = speechsdk.audio.AudioConfig(filename=True)
audio_config = speechsdk.audio.AudioConfig(filename="Refund.wav")

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

speech_recognition_result = speech_recognizer.recognize_once_async().get()

if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(speech_recognition_result.text))
elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
elif speechsdk.ResultReason.Canceled == speech_recognition_result.reasno:
    cancellation_details = speech_recognition_result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
outputList = [speech_recognition_result.text]
poller = text_analytics_client.begin_analyze_actions(
    outputList,
    display_name="Sample Text Analysis",
    actions=[
        RecognizeEntitiesAction(),
        AnalyzeSentimentAction()
    ]
)

document_results = poller.result()
df = pd.DataFrame()
df1 = pd.DataFrame()
sentimentDict = []
entityDict = []
for doc, action_results in zip(outputList, document_results):
    recognize_entities_result, analyze_sentiment_result = action_results
    if recognize_entities_result.is_error:
        print("......Is an error with code '{}' and message '{}'".format(
            recognize_entities_result.code, recognize_entities_result.message
        ))
    else:
        for entity in recognize_entities_result.entities:
            entityDict.append(
                {   'Text': doc,
                    'Entity': entity.text,
                    'EntityCategory': entity.category,
                    'EntityVConfidenceScore': entity.confidence_score,
                    'OverallEntityRecognition': recognize_entities_result.entities
                }
            )

    if analyze_sentiment_result.is_error:
        print("......Is an error with code '{}' and message '{}'".format(
            analyze_sentiment_result.code, analyze_sentiment_result.message
        ))
    else:
        sentimentDict.append(
            {
             'Text': doc,
             'TextSentiment': analyze_sentiment_result.sentiment,
             'SentimentScores': "......Scores: positive={}; neutral={}; negative={} \n".format(
                 analyze_sentiment_result.confidence_scores.positive,
                 analyze_sentiment_result.confidence_scores.neutral,
                 analyze_sentiment_result.confidence_scores.negative)
             }
        )

print("------------------------------------------")
# print(sentimentDict)
# print(entityDict)
# save sentiment
sentimentdf = df.append(sentimentDict, ignore_index=True, sort=False)
file_name1 = 'sentimentTextOutput.xlsx'
sentimentdf.to_excel(file_name1)

# save entity
entitydf = df1.append(entityDict, ignore_index=True, sort=False)
file_name = 'entityTextOutput.xlsx'
entitydf.to_excel(file_name)
