---
layout: post
title: "Python and the Magical OAuth Token"
categories: Python
---

A [recent post by Colin](https://colinsent.me/The-Magical-Self-Rotating-Self-Getting-OAuth-Token-aa8e8a840e9643fd9f4ca8f9e97e53e9) demonstrated a utility class they'd written to handle fetching and refreshing OAuth bearer tokens for APIs and services that are secured that way, to stop you having to worry about it in the majority of your code. For years, I've used a similar class at work that I wrote to simplify this, and Colin's post prompted me to share it here too.

The main difference from Colin's solution is that the class I use is a subclass of the [Requests](https://docs.python-requests.org/en/latest/) `Session` object, rather than a stand-alone object. It handles not only fetching and refreshing the bearer token where necessary, but also inserting the correct headers to the requests you make. Here's the entire class (and a couple of helper exception classes):

```python
import requests
import datetime

class OAuthResponseError(Exception):
    pass

class OAuthInvalidGrant(OAuthResponseError):
    pass

class OAuthInvalidScope(OAuthResponseError):
    pass

  
class TokenRefreshSession(requests.Session):

    ERROR_MAPPING = {
        "invalid_grant": OAuthInvalidGrant,
        "invalid_scope": OAuthInvalidScope,
    }

    def __init__(self, client_id, client_secret, scope, token_url, *args, **kwargs):
        self.oauth_client_id = client_id
        self.oauth_client_secret = client_secret
        self.oauth_scope = scope
        self.oauth_token_url = token_url
        super().__init__(*args, **kwargs)

    def prepare_request(self, request):
        '''Add the access token to the headers'''
        self.headers["Authorization"] = f"Bearer {self.oauth_access_token}"
        return super().prepare_request(request)

    @property
    def oauth_access_token(self):
        '''Return a valid Access Token. Renews the token if it has expired'''
        if not self.oauth_access_token_valid():

            data = {
                "client_id": self.oauth_client_id,
                "client_secret": self.oauth_client_secret,
                "grant_type": "client_credentials",
                "scope": self.oauth_scope,
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            response = requests.post(
                self.oauth_token_url,
                data = data,
                headers = headers,
            )

            response.raise_for_status()
            response_data = response.json()

            if "error" in response_data:
                raise self.ERROR_MAPPING.get(
                    response_data["error"],
                    OAuthResponseError)(response_data["error_description"]
                )

            self._oauth_access_token = response_data["access_token"]
            self._oauth_access_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=response_data["expires_in"])

        return self._oauth_access_token

    def oauth_access_token_valid(self):
        '''Check the validity of the current access token'''

        now = datetime.datetime.now()
        fudged_time = now + datetime.timedelta(minutes=5)

        access_token = getattr(self, "_oauth_access_token", None)
        access_token_expiry = getattr(self, "_oauth_access_token_expiry", now)

        if not access_token or access_token_expiry <= fudged_time:
            return False

        return True

```

The code is relatively simple. As a subclass of `requests.Session`, it accepts all the usual arguments, but also requires the OAuth client ID, client secret, scope, and token endpoint. This could be hardcoded, or a default provided in the class definition as we do internally, to avoid having to specify it each time.

The `prepare_request` method is part of the `requests.Session` mechanism for generating the HTTP call when the library is used. The overriden method in the `TokenRefreshSession` object inserts the correct `Authorization: Bearer` header and token into the request on behalf of the user.

As with Colin's solution, the `oauth_access_token` property is computed when accessed, and performs the necessary update or refresh should the currently stored token have expired, by posting the client credentials data to the token endpoint provided.

Here's an example of the class in action:

```python
session = TokenRefreshSession(
    client_id="123456",
    client_secret="shh",
    scope=["read", "write", "etc"],
    token_url="https://api.my-great-app.com/v1.0/auth",
)

user = session.get("https://api.my-great-app.com/v1.0/users/23")
```

The first API call will fetch the token and store it, and subsequent calls (using the same session object) will either use the stored token or fetch a new one as necessary. You never need worry about including the `Bearer` header yourself. And, to quote Colin's post:

> Your token will magically manage itself, leaving you free to write good code against your favorite API.
