import random
import string
import logging
import re
from init_unit import config


async def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.choice(letters_and_digits) for i in range(length))
    return rand_string


def delete_smiles_emoji(text):
    """This function deletes smiles and emojis from the text message but saves all Cyrillic letters"""
    # Define a regular expression pattern to match smiles and emojis
    jls_extract_var = r"[^\\\w\\\s\\p{Cyrillic}]"
    pattern = jls_extract_var
    
    # Use the re.sub() function to replace all matches with an empty string
    cleaned_text = re.sub(pattern, "", text)
    
    return cleaned_text

async def dict_user_fields(**kwargs):
    user_fields = {}
    bitrix_config = config.get("bitrix")
    user_fields = bitrix_config.get("user_fields")
    user_prefix = bitrix_config.get("user_fields_prefix")
    fields = {}
    for key, value in kwargs.items():
        if key in user_fields:
            fields[user_prefix + key] = value
            
    return fields
