import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# The VerifyAuthChallengeResponse Lambda function evaluates the response and returns a Boolean to indicate if the response was valid.


def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    if event["triggerSource"] == "VerifyAuthChallengeResponse_Authentication":
        if event["request"]["challengeAnswer"] == event["request"]["privateChallengeParameters"]["answer"]:
            event["response"]["answerCorrect"] = True
    return event
