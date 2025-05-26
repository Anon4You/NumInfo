import re
import requests
import json
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import argparse
from colorama import init, Fore
import os
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)
load_dotenv()

# ASCII Art Logo
LOGO = f"""{Fore.GREEN}
888b    888                        8888888           .d888         
8888b   888                          888            d88P"          
88888b  888                          888            888            
888Y88b 888 888  888 88888b.d88b.    888   88888b.  888888 .d88b.  
888 Y88b888 888  888 888 "888 "88b   888   888 "88b 888   d88""88b 
888  Y88888 888  888 888  888  888   888   888  888 888   888  888 
888   Y8888 Y88b 888 888  888  888   888   888  888 888   Y88..88P 
888    Y888  "Y88888 888  888  888 8888888 888  888 888    "Y88P"                             
                                            {Fore.MAGENTA}~created by Alienkrishn
                                            {Fore.RESET}Github:Anon4You
"""

class PhoneNumberInfoGatherer:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.valid = False
        self.formatted_number = None
        self.country_code = None
        self.national_number = None
        self.results = {
            'basic_info': {},
            'carrier_info': {},
            'geolocation': {},
            'timezone_info': {},
            'additional_data': {}
        }

    def validate_and_parse(self):
        """Validate and parse the phone number using phonenumbers library"""
        try:
            parsed_number = phonenumbers.parse(self.phone_number, None)
            self.valid = phonenumbers.is_valid_number(parsed_number)
            self.formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164)
            self.country_code = parsed_number.country_code
            self.national_number = parsed_number.national_number
            self.results['basic_info'] = {
                'raw_input': self.phone_number,
                'formatted_e164': self.formatted_number,
                'country_code': self.country_code,
                'national_number': self.national_number,
                'is_valid': self.valid
            }
            return True
        except phonenumbers.phonenumberutil.NumberParseException as e:
            print(Fore.RED + f"Error parsing phone number: {e}")
            return False

    def get_carrier_info(self):
        """Get carrier information using phonenumbers and NumVerify API"""
        if not self.valid:
            return

        try:
            parsed_number = phonenumbers.parse(self.formatted_number)
            carrier_name = carrier.name_for_number(parsed_number, "en")
            self.results['carrier_info']['phonenumbers_lib'] = {
                'carrier': carrier_name
            }

            # NumVerify API (requires API key in .env)
            numverify_api_key = os.getenv('NUMVERIFY_API_KEY')
            if numverify_api_key:
                try:
                    url = f"http://apilayer.net/api/validate?access_key={numverify_api_key}&number={self.formatted_number}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        self.results['carrier_info']['numverify'] = {
                            'carrier': data.get('carrier'),
                            'line_type': data.get('line_type'),
                            'ported': data.get('ported')
                        }
                except Exception as e:
                    print(Fore.YELLOW + f"NumVerify API error: {e}")

        except Exception as e:
            print(Fore.RED + f"Error getting carrier info: {e}")

    def get_geolocation(self):
        """Get geolocation information"""
        if not self.valid:
            return

        try:
            parsed_number = phonenumbers.parse(self.formatted_number)
            region = geocoder.description_for_number(parsed_number, "en")
            self.results['geolocation']['phonenumbers_lib'] = {
                'region': region
            }

            # AbstractAPI (requires API key in .env)
            abstract_api_key = os.getenv('ABSTRACT_API_KEY')
            if abstract_api_key:
                try:
                    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={abstract_api_key}&phone={self.formatted_number}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        self.results['geolocation']['abstractapi'] = {
                            'country': data.get('country'),
                            'country_code': data.get('country_code'),
                            'location': data.get('location')
                        }
                except Exception as e:
                    print(Fore.YELLOW + f"AbstractAPI error: {e}")

        except Exception as e:
            print(Fore.RED + f"Error getting geolocation: {e}")

    def get_timezone(self):
        """Get timezone information"""
        if not self.valid:
            return

        try:
            parsed_number = phonenumbers.parse(self.formatted_number)
            time_zones = timezone.time_zones_for_number(parsed_number)
            self.results['timezone_info'] = {
                'time_zones': time_zones
            }
        except Exception as e:
            print(Fore.RED + f"Error getting timezone: {e}")

    def get_additional_data(self):
        """Get additional data from other sources"""
        if not self.valid:
            return

        try:
            self.results['additional_data']['reputation_check'] = {
                'reported_as_spam': False,
                'reported_as_scam': False,
                'notes': 'This would require integration with a reputation API'
            }
        except Exception as e:
            print(Fore.YELLOW + f"Error checking number reputation: {e}")

    def gather_all_info(self):
        """Run all information gathering methods"""
        if not self.validate_and_parse():
            return False

        self.get_carrier_info()
        self.get_geolocation()
        self.get_timezone()
        self.get_additional_data()
        return True

    def print_results(self):
        """Print the gathered information in a readable format"""
        if not self.valid:
            print(Fore.RED + "Invalid phone number. Could not gather information.")
            return

        print(Fore.GREEN + "\n=== Phone Number Information ===")
        print(Fore.CYAN + f"\n[Basic Information]")
        for key, value in self.results['basic_info'].items():
            print(f"{key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")

        print(Fore.CYAN + "\n[Carrier Information]")
        for source, data in self.results['carrier_info'].items():
            print(f"\nSource: {Fore.MAGENTA}{source}")
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")

        print(Fore.CYAN + "\n[Geolocation Information]")
        for source, data in self.results['geolocation'].items():
            print(f"\nSource: {Fore.MAGENTA}{source}")
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")

        print(Fore.CYAN + "\n[Timezone Information]")
        for key, value in self.results['timezone_info'].items():
            print(f"{key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")

        print(Fore.CYAN + "\n[Additional Data]")
        for category, data in self.results['additional_data'].items():
            print(f"\nCategory: {Fore.MAGENTA}{category.replace('_', ' ').title()}")
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")

    def save_to_file(self, filename="phone_info.json"):
        """Save the results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(Fore.GREEN + f"\nResults saved to {filename}")


def main():
    print(LOGO)
    parser = argparse.ArgumentParser(description="Advanced Phone Number Information Gathering Tool")
    parser.add_argument("phone_number", help="Phone number to investigate (include country code)")
    parser.add_argument("-o", "--output", help="Output file name (JSON format)", default=None)
    args = parser.parse_args()

    print(Fore.BLUE + "Starting phone number information gathering...")
    
    gatherer = PhoneNumberInfoGatherer(args.phone_number)
    if gatherer.gather_all_info():
        gatherer.print_results()
        if args.output:
            gatherer.save_to_file(args.output)
    else:
        print(Fore.RED + "Failed to gather information for the provided phone number.")

if __name__ == "__main__":
    main()
