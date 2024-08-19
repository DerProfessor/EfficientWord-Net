"""
Needs to be run directly in cli via
`python -m eff_word_net.ibm_cloud_generate {hotword} {output_location}`

Can be used to artificially synthesize audio samples for a given hotword
Uses IBM cloud, so you need to provide account credentials
"""

import argparse
import requests
from os import environ, mkdir
from os.path import isdir, join

from dotenv import load_dotenv
load_dotenv()

if environ.get("IBM_CLOUD_API_KEY") == None or environ.get("IBM_CLOUD_URL") == None:
    raise Exception("""
Enviroment variables for IBM_CLOUD_API_KEY and IBM_CLOUD_URL not found.
Please supply values in .env file or set them directly.
""")

GERMAN_VOICES = ["de-DE_BirgitV3Voice", "de-DE_DieterV3Voice", "de-DE_ErikaV3Voice"]
ENGLISH_UK_VOICES = ["en-GB_CharlotteV3Voice", "en-GB_JamesV3Voice", "en-GB_KateV3Voice"]
ENGLISH_US_VOICES = ["en-US_AllisonV3Voice",
                     "en-US_KevinV3Voice","en-US_MichaelV3Voice",
                     "en-US_OliviaV3Voice"]
FRENCH_VOICES = ["fr-CA_LouiseV3Voice","fr-FR_NicolasV3Voice","fr-FR_ReneeV3Voice"]

# Parse arguments
parser = argparse.ArgumentParser(
    description="Module synthesizes audio files for given words using the IBM Cloud API")
parser.add_argument("wakeword", help="Wakeword that should be synthesized")
parser.add_argument("location", help="Location where audio files will be saved")
args = parser.parse_args()

def synthesize_voice(word: str, voice: str, out_dir: str):
    out_dir = join(out_dir, word.replace(" ", "_"))
    session = requests.Session()

    headers = {
        "Accept": "audio/wav",
        "Content-Type": "application/json"
    }
    url = environ['IBM_CLOUD_URL'] + "/v1/synthesize"
    params = {
        "voice": voice,
        "rate_percentage": "-10"
    }
    json_data = {"text": word}
    auth = ("apikey", environ["IBM_CLOUD_API_KEY"])

    response = session.post(url, params=params, json=json_data, headers=headers, auth=auth)
    
    if response.status_code == 200:
        if(not isdir(out_dir)):
            mkdir(out_dir)
        with open(join(out_dir, f"{word}_{voice}.mp3"), 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Error during API access, code: {response.status_code}")

if __name__=="__main__":
    if(not isdir(args.location)):
        mkdir(args.location)

    for voice in [*GERMAN_VOICES, *ENGLISH_UK_VOICES, *ENGLISH_US_VOICES, *FRENCH_VOICES]:
        print(f"Synthesizing hotword \"{args.wakeword}\" with voice {voice}")
        synthesize_voice(args.wakeword, voice, args.location)
