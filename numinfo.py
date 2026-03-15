#!/data/data/com.termux/files/usr/bin/python

##   NumInfo   :      Advanced Phone Number Intelligence Tool
##   Author    :      Alienkrishn [Anon4You]

import re
import requests
import json
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import argparse
import os
from dotenv import load_dotenv
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from rich.syntax import Syntax
from rich import box

# Load environment variables
load_dotenv()

# ASCII Art Logo (will be displayed inside a panel)
LOGO = r"""
888b    888                        8888888           .d888         
8888b   888                          888            d88P"          
88888b  888                          888            888            
888Y88b 888 888  888 88888b.d88b.    888   88888b.  888888 .d88b.  
888 Y88b888 888  888 888 "888 "88b   888   888 "88b 888   d88""88b 
888  Y88888 888  888 888  888  888   888   888  888 888   888  888 
888   Y8888 Y88b 888 888  888  888   888   888  888 888   Y88..88P 
888    Y888  "Y88888 888  888  888 8888888 888  888 888    "Y88P"  
                                            ~created by Alienkrishn
                                            Github: Anon4You
"""

class PhoneNumberInfoGatherer:
    def __init__(self, phone_number, console, verbose=False, no_color=False):
        self.phone_number = phone_number
        self.console = console
        self.verbose = verbose
        self.no_color = no_color
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

    def log_debug(self, msg):
        if self.verbose:
            self.console.log(f"[dim][DEBUG] {msg}[/dim]")

    def validate_and_parse(self):
        """Validate and parse the phone number using phonenumbers library"""
        try:
            parsed_number = phonenumbers.parse(self.phone_number, None)
            self.valid = phonenumbers.is_valid_number(parsed_number)
            self.formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164)
            self.country_code = parsed_number.country_code
            self.national_number = parsed_number.national_number
            country_name = geocoder.country_name_for_number(parsed_number, "en")
            self.results['basic_info'] = {
                'raw_input': self.phone_number,
                'formatted_e164': self.formatted_number,
                'country_code': self.country_code,
                'country_name': country_name,
                'national_number': self.national_number,
                'is_valid': self.valid
            }
            self.log_debug(f"Parsed successfully: {self.formatted_number}")
            return True
        except phonenumbers.phonenumberutil.NumberParseException as e:
            self.console.print(f"[red]Error parsing phone number: {e}[/red]")
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
            self.log_debug(f"Carrier from phonenumbers: {carrier_name}")

            # NumVerify API (requires API key in .env)
            numverify_api_key = os.getenv('NUMVERIFY_API_KEY')
            if numverify_api_key:
                try:
                    url = f"http://apilayer.net/api/validate?access_key={numverify_api_key}&number={self.formatted_number}"
                    self.log_debug(f"Calling NumVerify API: {url.replace(numverify_api_key, '***')}")
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        numverify_data = {
                            'valid': data.get('valid'),
                            'number': data.get('number'),
                            'local_format': data.get('local_format'),
                            'international_format': data.get('international_format'),
                            'country_prefix': data.get('country_prefix'),
                            'country_code': data.get('country_code'),
                            'country_name': data.get('country_name'),
                            'location': data.get('location'),
                            'carrier': data.get('carrier'),
                            'line_type': data.get('line_type')
                        }
                        numverify_data = {k: v for k, v in numverify_data.items() if v is not None}
                        self.results['carrier_info']['numverify'] = numverify_data
                        self.log_debug("NumVerify API call successful")
                    else:
                        self.log_debug(f"NumVerify API error {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_debug(f"NumVerify API error: {e}")

        except Exception as e:
            self.log_debug(f"Error getting carrier info: {e}")

    def get_geolocation(self):
        """Get geolocation information from phonenumbers and AbstractAPI"""
        if not self.valid:
            return

        try:
            parsed_number = phonenumbers.parse(self.formatted_number)
            region = geocoder.description_for_number(parsed_number, "en")
            self.results['geolocation']['phonenumbers_lib'] = {
                'region': region
            }
            self.log_debug(f"Region from phonenumbers: {region}")

            # AbstractAPI Phone Intelligence (requires API key in .env)
            abstract_api_key = os.getenv('ABSTRACT_API_KEY')
            if abstract_api_key:
                try:
                    phone_digits = self.formatted_number.lstrip('+')
                    url = f"https://phoneintelligence.abstractapi.com/v1/?api_key={abstract_api_key}&phone={phone_digits}"
                    self.log_debug(f"Calling AbstractAPI: {url.replace(abstract_api_key, '***')}")
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        abstract_data = {
                            'carrier_name': data.get('phone_carrier', {}).get('name'),
                            'line_type': data.get('phone_carrier', {}).get('line_type'),
                            'mcc': data.get('phone_carrier', {}).get('mcc'),
                            'mnc': data.get('phone_carrier', {}).get('mnc'),
                            'country': data.get('phone_location', {}).get('country_name'),
                            'country_code': data.get('phone_location', {}).get('country_code'),
                            'region': data.get('phone_location', {}).get('region'),
                            'city': data.get('phone_location', {}).get('city'),
                            'timezone': data.get('phone_location', {}).get('timezone'),
                            'validation_valid': data.get('phone_validation', {}).get('is_valid'),
                            'line_status': data.get('phone_validation', {}).get('line_status'),
                            'is_voip': data.get('phone_validation', {}).get('is_voip'),
                            'risk_level': data.get('phone_risk', {}).get('risk_level'),
                            'is_disposable': data.get('phone_risk', {}).get('is_disposable'),
                            'is_abuse_detected': data.get('phone_risk', {}).get('is_abuse_detected'),
                            'sms_email': data.get('phone_messaging', {}).get('sms_email'),
                            'breaches_total': data.get('phone_breaches', {}).get('total_breaches'),
                        }
                        abstract_data = {k: v for k, v in abstract_data.items() if v is not None}
                        self.results['geolocation']['abstractapi'] = abstract_data
                        self.log_debug("AbstractAPI call successful")
                    else:
                        self.log_debug(f"AbstractAPI error {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_debug(f"AbstractAPI error: {e}")

        except Exception as e:
            self.log_debug(f"Error getting geolocation: {e}")

    def get_timezone(self):
        """Get timezone information from phonenumbers"""
        if not self.valid:
            return

        try:
            parsed_number = phonenumbers.parse(self.formatted_number)
            time_zones = timezone.time_zones_for_number(parsed_number)
            self.results['timezone_info'] = {
                'time_zones': list(time_zones)
            }
            self.log_debug(f"Time zones: {time_zones}")
        except Exception as e:
            self.log_debug(f"Error getting timezone: {e}")

    def get_additional_data(self):
        """Get additional data from other sources"""
        if not self.valid:
            return

        try:
            # Placeholder for future reputation API
            self.results['additional_data']['reputation_check'] = {
                'reported_as_spam': False,
                'reported_as_scam': False,
                'notes': 'Integration with reputation API needed'
            }
            self.log_debug("Added placeholder reputation data")
        except Exception as e:
            self.log_debug(f"Error checking number reputation: {e}")

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
        """Print the gathered information using rich tables and panels"""
        if not self.valid:
            self.console.print("[red]Invalid phone number. Could not gather information.[/red]")
            return

        # Helper to create a table from a dictionary (handles nested dicts)
        def dict_to_table(title, data):
            table = Table(title=title, title_style="bold cyan", box=box.ROUNDED, header_style="bold")
            table.add_column("Key", style="yellow")
            table.add_column("Value", style="white")
            for key, value in data.items():
                if isinstance(value, dict):
                    # For nested dicts, create a sub-table (but we'll handle separately in the main flow)
                    # For simplicity, we just show the key and indicate it's nested.
                    # We'll expand nested data in the calling code.
                    table.add_row(key.replace('_', ' ').title(), "[italic]<nested>[/italic]")
                else:
                    table.add_row(key.replace('_', ' ').title(), str(value))
            return table

        # Main information panel
        self.console.print(Panel(f"[bold green]Phone Number: {self.phone_number}[/bold green]", expand=False))

        # Basic Information (simple table)
        basic_table = dict_to_table("Basic Information", self.results['basic_info'])
        self.console.print(basic_table)

        # Carrier Information (multiple sources grouped in a panel)
        if self.results['carrier_info']:
            carrier_tables = []
            for source, data in self.results['carrier_info'].items():
                table = dict_to_table(f"Source: {source}", data)
                carrier_tables.append(table)
            group = Group(*carrier_tables)
            self.console.print(Panel(group, title="Carrier Information", border_style="blue"))

        # Geolocation Information (multiple sources grouped)
        if self.results['geolocation']:
            geo_tables = []
            for source, data in self.results['geolocation'].items():
                table = dict_to_table(f"Source: {source}", data)
                geo_tables.append(table)
            group = Group(*geo_tables)
            self.console.print(Panel(group, title="Geolocation Information", border_style="green"))

        # Timezone Information (simple table)
        tz_table = dict_to_table("Timezone Information", self.results['timezone_info'])
        self.console.print(tz_table)

        # Additional Data (expand nested dicts)
        if self.results['additional_data']:
            add_tables = []
            for key, value in self.results['additional_data'].items():
                if isinstance(value, dict):
                    # Create a table for this nested dict with the key as title
                    nested_table = dict_to_table(key.replace('_', ' ').title(), value)
                    add_tables.append(nested_table)
                else:
                    # For non-dict, just show as a simple key-value? Not expected here.
                    pass
            if add_tables:
                group = Group(*add_tables)
                self.console.print(Panel(group, title="Additional Data", border_style="magenta"))

    def save_to_file(self, filename="phone_info.json"):
        """Save the results to a JSON file and optionally preview with syntax highlighting"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        self.console.print(f"\n[green]Results saved to {filename}[/green]")
        if self.verbose:
            # Show a preview of the JSON with syntax highlighting
            with open(filename, 'r') as f:
                json_content = f.read()
            syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, title="JSON Preview", border_style="green"))

def read_numbers_from_file(filepath):
    """Read phone numbers from a file, one per line."""
    numbers = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    numbers.append(line)
    except Exception as e:
        print(f"Error reading file: {e}")
    return numbers

def main():
    parser = argparse.ArgumentParser(description="Advanced Phone Number Information Gathering Tool")
    parser.add_argument("phone_number", nargs="*", help="Phone number(s) to investigate (include country code)")
    parser.add_argument("-f", "--file", help="File containing phone numbers (one per line)")
    parser.add_argument("-o", "--output", help="Output file name (JSON format)", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    # Initialize Rich console with no_color if requested
    console = Console(no_color=args.no_color, color_system=None if args.no_color else "auto")

    # Display logo inside a panel
    console.print(Panel(LOGO, title="NumInfo", subtitle="Advanced Phone Number Intelligence", border_style="green"))

    # Collect numbers from command line and file
    numbers = []
    if args.file:
        numbers.extend(read_numbers_from_file(args.file))
    if args.phone_number:
        numbers.extend(args.phone_number)

    if not numbers:
        console.print("[yellow]No phone numbers provided. Use -h for help.[/yellow]")
        return

    all_results = []

    # Process numbers with a progress bar if there are many
    if len(numbers) > 1 and not args.verbose:
        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Processing numbers...", total=len(numbers))
            for num in numbers:
                progress.update(task, description=f"[cyan]Processing: {num}")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=True) as spinner:
                    spinner.add_task("", total=None)
                    gatherer = PhoneNumberInfoGatherer(num, console, verbose=args.verbose, no_color=args.no_color)
                    if gatherer.gather_all_info():
                        gatherer.print_results()
                        all_results.append(gatherer.results)
                    else:
                        console.print(f"[red]Failed to gather information for {num}[/red]")
                progress.advance(task)
    else:
        # Single number or verbose mode: show individual results without progress bar
        for idx, num in enumerate(numbers):
            console.rule(f"[bold blue]Processing {idx+1}/{len(numbers)}: {num}[/bold blue]")
            gatherer = PhoneNumberInfoGatherer(num, console, verbose=args.verbose, no_color=args.no_color)
            if gatherer.gather_all_info():
                gatherer.print_results()
                all_results.append(gatherer.results)
            else:
                console.print(f"[red]Failed to gather information for {num}[/red]")

    # Save all results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_results if len(all_results) > 1 else all_results[0] if all_results else {}, f, indent=4)
        console.print(f"\n[green]Results saved to {args.output}[/green]")
        if args.verbose:
            with open(args.output, 'r') as f:
                json_content = f.read()
            syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="JSON Preview", border_style="green"))

if __name__ == "__main__":
    main()
