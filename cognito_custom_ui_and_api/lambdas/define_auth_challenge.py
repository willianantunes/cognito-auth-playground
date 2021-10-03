import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Interesting links to look at:
# - https://stackoverflow.com/a/65570565/3899136
# - https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html#Custom-authentication-flow-and-challenges

# The DefineAuthChallenge Lambda trigger takes as input a session array of previous challenges and responses.
# It then outputs the next challenge name and Booleans that indicate whether the user is authenticated (and should be granted tokens) or not.
# This Lambda trigger is a state machine that controls the user’s path through the challenges.


def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    if event["triggerSource"] == "DefineAuthChallenge_Authentication":
        event["response"]["challengeName"] = "CUSTOM_CHALLENGE"
        event["response"]["issueTokens"] = False
        event["response"]["failAuthentication"] = False

        if event["request"]["session"]:  # Needed for step 4.
            # If all of the challenges are answered, issue tokens.
            event["response"]["issueTokens"] = all(
                answered_challenge["challengeResult"] for answered_challenge in event["request"]["session"]
            )
    return event
