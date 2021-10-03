import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# The CreateAuthChallenge Lambda trigger takes a challenge name as input and generates the challenge and parameters to evaluate the response.
# CreateAuthChallenge is called when DefineAuthChallenge returns CUSTOM_CHALLENGE as the next challenge, and the next type of challenge is passed in the challenge metadata parameter.


def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    if event["triggerSource"] == "CreateAuthChallenge_Authentication":
        if event["request"]["challengeName"] == "CUSTOM_CHALLENGE":
            event["response"]["privateChallengeParameters"] = {}
            event["response"]["privateChallengeParameters"]["answer"] = "YOUR CHALLENGE ANSWER HERE"
            event["response"]["challengeMetadata"] = "AUTHENTICATE_AS_CHALLENGE"
    return event
