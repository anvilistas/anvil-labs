# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import base64
import json
import urllib.parse
from base64 import b64decode
from functools import wraps

import anvil.server
import anvil.users
from anvil.tables import app_tables

__version__ = "0.0.1"

webauthn = None
structs = None


def lazily_import_webauthn():
    global webauthn, structs
    if webauthn is None:
        import webauthn
        import webauthn.helpers.structs as structs


def webauthn_callable(name, require_user=False):
    callable_wrapper = anvil.server.callable(name, require_user=require_user)

    def outer(fn):
        @wraps(fn)
        def inner(*args, **kws):
            lazily_import_webauthn()
            return fn(*args, **kws)

        return callable_wrapper(inner)

    return outer


def get_rp():
    app_origin = anvil.server.get_app_origin()
    url = urllib.parse.urlparse(app_origin)
    return {"rp_id": url.netloc, "rp_name": app_origin}


def get_challenge(type):
    challenge = anvil.server.session.get(f"{type}-challenge")
    if challenge is None:
        return None

    return bytes(challenge)


@webauthn_callable("fido.webauthn.generate_registration", require_user=True)
def generate_registration():
    user = anvil.users.get_user()
    email = user["email"]
    rp = get_rp()
    challenge = get_challenge("reg")
    fido = user["fido"] or {}

    opts = webauthn.generate_registration_options(
        user_id=email,
        user_name=email,
        challenge=challenge,
        timeout=60000,
        exclude_credentials=[
            structs.PublicKeyCredentialDescriptor(id=webauthn.base64url_to_bytes(cred))
            for cred in fido.keys()
        ],
        **rp,
    )
    anvil.server.session["reg-challenge"] = list(opts.challenge)

    opts = webauthn.options_to_json(opts)
    return json.loads(opts)


@webauthn_callable("fido.webauthn.verify_registration", require_user=True)
def verify_webauth_credentials(registration_data):
    rp_id = get_rp()["rp_id"]
    registration_data = json.dumps(registration_data)
    challenge = bytes(anvil.server.session["reg-challenge"])

    registration_verification = webauthn.verify_registration_response(
        credential=structs.RegistrationCredential.parse_raw(registration_data),
        expected_challenge=challenge,
        expected_origin=f"https://{rp_id}",
        expected_rp_id=rp_id,
        require_user_verification=True,
    )

    registered_cred_id = (
        base64.urlsafe_b64encode(registration_verification.credential_id)
        .decode()
        .strip("=")
    )
    registered_cred_pk = (
        base64.urlsafe_b64encode(registration_verification.credential_public_key)
        .decode()
        .strip("=")
    )

    user = anvil.users.get_user()
    fido = user["fido"] or {}
    fido[registered_cred_id] = {
        "pk": registered_cred_pk,
        "count": registration_verification.sign_count,
    }
    user["fido"] = fido


@webauthn_callable("fido.webauthn.generate_authentication")
def generate_autentication_options(email):
    user = app_tables.users.get(email=email)
    rp_id = get_rp()["rp_id"]
    fido = user["fido"] or {}
    allow_credentials = [
        structs.PublicKeyCredentialDescriptor(id=webauthn.base64url_to_bytes(cred))
        for cred in fido.keys()
    ]
    challenge = get_challenge("auth")

    authentication_options = webauthn.generate_authentication_options(
        rp_id=rp_id,
        timeout=60000,
        allow_credentials=allow_credentials,
        challenge=challenge,
        user_verification=structs.UserVerificationRequirement.REQUIRED,
    )
    anvil.server.session["auth-challenge"] = list(authentication_options.challenge)

    opts = webauthn.options_to_json(authentication_options)
    return json.loads(opts)


@webauthn_callable("fido.webauthn.login_with_fido")
def login_with_fido(email, authentication_data):
    user = app_tables.users.get(email=email)

    id = authentication_data["rawId"]
    fido = user["fido"] or {}
    credential = fido.get(id)
    if credential is None:
        return None
    rp_id = get_rp()["rp_id"]

    authentication_verification = webauthn.verify_authentication_response(
        credential=structs.AuthenticationCredential.parse_raw(
            json.dumps(authentication_data)
        ),
        expected_challenge=bytes(anvil.server.session["auth-challenge"]),
        expected_rp_id=rp_id,
        expected_origin=f"https://{rp_id}",
        credential_public_key=webauthn.base64url_to_bytes(credential["pk"]),
        credential_current_sign_count=credential["count"],
        require_user_verification=True,
    )

    credential["count"] = authentication_verification.new_sign_count
    user["fido"] = fido

    return anvil.users.force_login(user)
