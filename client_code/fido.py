# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil.js
import anvil.server
import anvil.users

__version__ = "0.0.1"

SimpleWebAuth = anvil.js.import_from("https://esm.sh/@simplewebauthn/browser@7.1.0")
startRegistration = SimpleWebAuth.startRegistration
startAuthentication = SimpleWebAuth.startAuthentication


def generate_registration():
    return anvil.server.call("fido.webauthn.generate_registration")


def verify_registration(response):
    return anvil.server.call("fido.webauthn.verify_registration", response)


def register_device():
    """a logged in user is required to register a device. The user table must have a 'fido' simple object column"""
    public_key = generate_registration()
    try:
        resposne = startRegistration(public_key)
    except anvil.js.ExternalError as e:
        print(repr(e))
        return None
    verify_registration(resposne)


def generate_authentication_options(email):
    return anvil.server.call("fido.webauthn.generate_authentication", email)


def verify_authentication_options(authentication_options):
    try:
        return startAuthentication(authentication_options)
    except anvil.js.ExternalError as e:
        print(repr(e))
        return None


def login_with_fido(email: str):
    """provide an email address to login with fido - this email might be stored in indexed db or local storage or similar"""
    authentication_options = generate_authentication_options(email)
    result = verify_authentication_options(authentication_options)
    if result is None:
        return
    user = anvil.server.call("fido.webauthn.login_with_fido", email, result)
    return user
