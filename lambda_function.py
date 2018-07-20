from __future__ import print_function
import os
import boto3
import json

alexa_skill_id = os.environ.get('AWS_ALEXA_SKILL_KIT_ID')


#####################################
# bahaviors
#####################################
def publish_power_state(power_state):
    client = boto3.client('iot-data', region_name='us-east-1')
    response = client.publish(
        topic='SmartCurtain',
        qos=1,
        payload=json.dumps({
            "PowerState": power_state
        }))
    return response


def get_help_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_out = "Welcome to use smart curtain."
    reprompt_text = "Now, please tell me what you want."
    should_end_session = True
    return build_response(
        session_attributes,
        build_speechlet_response(card_title, speech_out, reprompt_text,
                                 should_end_session))


def set_smart_curtain_power_state(intent, session):
    """ set power state """
    print("*** Smart Curtain Power State ***")
    should_end_session = False
    power_state = intent['slots']['PowerState']['value']
    print("PowerState: " + power_state)
    if power_state and (power_state.upper() == 'ON'
                        or power_state.upper() == 'OFF'):
        card_title = "SmartCurtain " + power_state
        speech_out = "Ok, my lord, smart curtain now is " + power_state + "."
        reprompt_text = "Ok, my lord, smart curtain is " + power_state + "."
        # publish power state
        publish_power_state(power_state)
    else:
        card_title = "SmartCurtain "
        speech_out = "I didn't understand that. Please repeat your request."
    return build_response(
        power_state,
        build_speechlet_response(card_title, speech_out, reprompt_text,
                                 should_end_session))


#####################################
# response builder
#####################################
def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output,
        },
        "card": {
            "type": "Simple",
            "title": "SmartCurtain - " + title,
            "content": "SmartCurtain - " + output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


#####################################
# session started & ended
#####################################
def on_session_started(session_started_request, session):
    """Called when the session starts"""
    print("on_session_started requestId=" +
          session_started_request['requestId'] + ", sessionId=" +
          session['sessionId'])


def on_session_ended(session_ended_request, session):
    """
    Call when user ends the session
    Not be called when the skill returns should_end_session=true
    """
    print("on_session_ended sessionId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """
    Called when the user launchers the skill 
    without specifying what they want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_help_response()


def on_intent(intent_request, session):
    """Called when the user specifies for this skill"""
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to skill's intent handler
    if intent_name == "powerStateIntent":
        return set_smart_curtain_power_state(intent, session)


def lambda_handler(event, context):
    """
    Route the incoming request:
        1. LaunchRequest,
        2. IntentRequest
    """
    print("event.session.application.applicatinId=" +
          event['session']['application']['applicationId'])

    if (alexa_skill_id != event['session']['application']['applicationId']):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({
            "requestId": event["request"]["requestId"]
        }, event["session"])

    request_type = event['request']['type']
    if request_type == 'LaunchRequest':
        return on_launch(event['request'], event['session'])
    elif request_type == 'IntentRequest':
        return on_intent(event['request'], event['session'])
    elif request_type == 'SessionEndedRequest':
        return on_session_ended(event['request'], event['session'])
