Fido
====

This module provides an interface for FIDO WebAuthn integration in Anvil applications.
It enables device registration and authentication using FIDO devices, such as security keys or biometric authenticators.


Demo App
--------

| `Clone Link <https://anvil.works/build#clone:KGKU6EOKG42TRABV=SY6TYYLCYD4VDECDMMWX54G4>`_
| `Live Demo <https://fido-example.anvil.app>`_


Requirements
------------

`webauthn <https://pypi.org/project/webauthn/>` must be installed on the server.



Functions
---------

.. function:: register_device()

This function registers a FIDO device for the currently logged-in user. The user table must have a 'fido' simple object column.

.. function:: login_with_fido(email: str)

This function attempts to authenticate the user with the provided email address using their registered FIDO device.
The email might be stored in IndexedDB, local storage, or a similar client-side storage system.

:param email: The email address of the user attempting to authenticate.
:returns: The authenticated user object, or None if authentication fails.


Internal Functions
------------------

.. function:: generate_registration()

This function generates a registration request for a FIDO device.

:returns: A public key for device registration.

.. function:: verify_registration(response)

This function verifies the registration response for a FIDO device.

:param response: The response from the FIDO device registration process.
:returns: The result of the verification process.

.. function:: generate_authentication_options(email)

This function generates authentication options for a FIDO device.

:param email: The email address of the user attempting to authenticate.
:returns: The authentication options for the FIDO device.

.. function:: verify_authentication_options(authentication_options)

This function verifies the authentication options for a FIDO device.

:param authentication_options: The authentication options for the FIDO device.
:returns: The result of the verification process, or None if an error occurs.
