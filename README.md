# Cognito Auth Playground

Just playing a bit around with Cognito.

I'm exploring, so do not consider this project as a real one (if you look at the code, you're going to laugh, haha).
This is far to be considered a production-ready one.

## Notes

### OpenID Configuration Request

You can get your [OpenID Configuration Request](https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfigurationRequest)
through the following URL:

    https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/openid-configuration

Giving how this project is configured:

    https://cognito-idp.us-east-1.amazonaws.com/us-east-1_0NMM172Uh/.well-known/openid-configuration

Sample output:

```json
{
  "authorization_endpoint": "https://situation-auth-playground.auth.us-east-1.amazoncognito.com/oauth2/authorize",
  "id_token_signing_alg_values_supported": [
    "RS256"
  ],
  "issuer": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_0NMM172Uh",
  "jwks_uri": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_0NMM172Uh/.well-known/jwks.json",
  "response_types_supported": [
    "code",
    "token"
  ],
  "scopes_supported": [
    "openid",
    "email",
    "phone",
    "profile"
  ],
  "subject_types_supported": [
    "public"
  ],
  "token_endpoint": "https://situation-auth-playground.auth.us-east-1.amazoncognito.com/oauth2/token",
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic",
    "client_secret_post"
  ],
  "userinfo_endpoint": "https://situation-auth-playground.auth.us-east-1.amazoncognito.com/oauth2/userInfo"
}
```

### Terrible things I noticed

- English in the only supported language for the Cognito UI. [No i18n still](https://forums.aws.amazon.com/thread.jspa?threadID=301920&start=25&tstart=0). 
- Once you create an attribute, you aren't able to delete it. You should create another user pool, and then migrate.
- There is no standard way to implement [Authorization Code flow without using the hosted UI](https://forums.aws.amazon.com/thread.jspa?messageID=832982#832982). It seems this is an open requirement since the beginning of 2018. There is also a [post on StackOverflow](https://stackoverflow.com/questions/59760537/aws-cognito-authorization-code-grant-flow-without-using-the-hosted-ui-in-2020) about it.

### Configuring your Django App

In order to run your application, you must configure `AWS_COGNITO_USER_POOL_ID`, `AWS_COGNITO_APP_CLIENT_ID`, `AWS_COGNITO_APP_CLIENT_SECRET`, `AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_KEY`, and `AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_SECRET` in your `settings.py`. After you create your environment with Terraform, you can run the following command to get the necessary values to configure them:

```shell
terraform output -json cognito_user_pool | jq '.user_pool.id' && \
terraform output -json cognito_clients | jq '.["poc-djangoclient-appclientcognito-tmp"].id' && \
terraform output -json cognito_client_secrets | jq '.["poc-djangoclient-appclientcognito-tmp"]' && \
terraform output -json iam_encrypted_access_keys | jq '.["poc-cognito-custom-ui-api"].access_key' && \
terraform output -json iam_encrypted_access_keys | jq '.["poc-cognito-custom-ui-api"].encrypted_secret' | sed 's/ //g' | sed 's/"//g' | base64 -d | gpg -d
```

Sample output:

```
"us-east-1_i8wbmVkhK"
"47302u6uq1g71ocb5dgq1bmbng"
"1lcqfd577c838s9n534lc6l5uggu27gtcat3617oi6dl0ge5pkll"
"AKIAXAQEEUDOLC3JLH3W"
gpg: encrypted with 3072-bit RSA key, ID BA9D0B22FE40F77D, created 2021-10-02
      "gandalf"
d0nySO5HPDRGTb+Bc4+Nt/d5qxQkXFHBfoluVgV1
```

## Links

Projects:

- [terraform-aws-cognito-user-pool](https://github.com/mineiros-io/terraform-aws-cognito-user-pool)

Articles:

- [How can I decode and verify the signature of an Amazon Cognito JSON Web Token?](https://aws.amazon.com/premiumsupport/knowledge-center/decode-verify-cognito-json-token/)
- [Machine to Machine Authentication with Cognito and Serverless](https://aws-blog.de/2020/01/machine-to-machine-authentication-with-cognito-and-serverless.html)
- [Decode and verify Amazon Cognito JWT tokens](https://github.com/awslabs/aws-support-tools/blob/f8aba4d90a14301c639859877b85e6335d51dbad/Cognito/decode-verify-jwt/README.md)
- [Cognito: User Pool; authenticating with username and password](https://cloudbyexample.io/part-2-aws-cognito-user-pool-authenticating-with-username-and-password/)
