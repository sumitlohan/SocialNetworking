import os
import binascii

from social_networking.apps.commons import constants as common_constants


def generate_key():
    # hex return here will be twice the length we pass in urandom
    return binascii.hexlify(os.urandom(int(common_constants.TOKEN_LENGTH/2))).decode()
