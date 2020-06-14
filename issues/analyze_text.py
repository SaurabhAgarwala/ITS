import requests
import json

# Key omitted for privacy reasons. Contact Saurabh Agarwala (saur.agarwala@gmail.com, +91 8415859101) for getting a temporary key for testing
API_KEY = '<replace with key>'


def keyPhraseExtraction(title, desc):
    url = 'https://westus2.api.cognitive.microsoft.com/text/analytics/v3.0-preview.1/keyPhrases'
    headers = {
        'content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': API_KEY
    }
    payload = {
        "documents": [
            {
                "language": "en",
                "id": "1",
                "text": title
            },
            {
                "language": "en",
                "id": "2",
                "text": desc
            }
        ]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    response_json = r.json()
    keyPhrases ={
        'title': response_json['documents'][0]['keyPhrases'],
        'desc': response_json['documents'][1]['keyPhrases']
    }
    print('Key Phrases:', keyPhrases)
    return keyPhrases


def namedEntityRecogntion(title, desc):
    url = 'https://westus2.api.cognitive.microsoft.com/text/analytics/v3.0-preview.1/entities/recognition/general'
    headers = {
        'content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': API_KEY
    }
    payload = {
        "documents": [
            {
                "language": "en",
                "id": "1",
                "text": title
            },
            {
                "language": "en",
                "id": "2",
                "text": desc
            }
        ]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    response_json = r.json()
    title_entities = response_json['documents'][0]['entities']
    desc_entities = response_json['documents'][1]['entities']
    entities = {
        'title': {},
        'desc': {}
    }
    entities['title']['entityText'], entities['title']['entityType'] = entityList(title_entities)
    entities['desc']['entityText'], entities['desc']['entityType'] = entityList(desc_entities)
    print('Entities', entities)
    return entities

def entityList(entities):
    entityText = []
    entityType = []
    for entity in entities:
        entityText.append(entity['text'])
        entityType.append(entity['type'])
    return entityText, entityType

# keyPhraseExtraction('Hello world. This is some input text that I love.', 'I work at Microsoft.')
# namedEntityRecogntion('I had a wonderful trip to Seattle last week', 'I work at Microsoft.')