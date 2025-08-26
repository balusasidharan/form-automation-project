import random
import json
import logging
from datetime import datetime, timedelta
from faker import Faker

# Set up logging for the random values generator
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomValuesGenerator:
    def __init__(self):
        self.fake = Faker('en_US')
        # Store generated data for reuse across pages
        self.generated_data_cache = {}
        
        # State-based zip codes mapping for all 50 US states
        self.state_zip_codes = {
            'AL': ['35201', '35202', '36101', '36102', '35801', '35802', '36801', '36802', '35401', '35402'],
            'AK': ['99501', '99502', '99503', '99504', '99701', '99702', '99801', '99802', '99901', '99902'],
            'AZ': ['85001', '85002', '85003', '85004', '85301', '85302', '85701', '85702', '86001', '86002'],
            'AR': ['72201', '72202', '72701', '72702', '71801', '71802', '72301', '72302', '71901', '71902'],
            'CA': ['90210', '90211', '94102', '94103', '94104', '91201', '90401', '92101', '95014', '94301'],
            'CO': ['80201', '80202', '80301', '80302', '80901', '80902', '81501', '81502', '80601', '80602'],
            'CT': ['06101', '06102', '06103', '06511', '06512', '06701', '06702', '06801', '06802', '06901'],
            'DE': ['19901', '19902', '19701', '19702', '19801', '19802', '19803', '19804', '19805', '19806'],
            'FL': ['33101', '33102', '32801', '32802', '33301', '34101', '33401', '32701', '33701', '33801'],
            'GA': ['30301', '30302', '30303', '31401', '31501', '30901', '31201', '30501', '39901', '31701'],
            'HI': ['96801', '96802', '96803', '96701', '96702', '96801', '96813', '96814', '96815', '96816'],
            'ID': ['83701', '83702', '83201', '83202', '83301', '83302', '83401', '83402', '83501', '83502'],
            'IL': ['60601', '60602', '60603', '60604', '60605', '60201', '61801', '62701', '61101', '60901'],
            'IN': ['46201', '46202', '46801', '46802', '47701', '47702', '46901', '46902', '47601', '47602'],
            'IA': ['50301', '50302', '52401', '52402', '51501', '51502', '50701', '50702', '52801', '52802'],
            'KS': ['66101', '66102', '67201', '67202', '67501', '67502', '66801', '66802', '67401', '67402'],
            'KY': ['40201', '40202', '40501', '40502', '42101', '42102', '41001', '41002', '42301', '42302'],
            'LA': ['70112', '70113', '70801', '70802', '71101', '71102', '70501', '70502', '71201', '71202'],
            'ME': ['04101', '04102', '04401', '04402', '04730', '04731', '04901', '04902', '04330', '04331'],
            'MD': ['21201', '21202', '20701', '20702', '21801', '21802', '20901', '20902', '21401', '21402'],
            'MA': ['02101', '02102', '01201', '01202', '01501', '01502', '02301', '02302', '01701', '01702'],
            'MI': ['48201', '48202', '49503', '49504', '48601', '48701', '49001', '48801', '49401', '48901'],
            'MN': ['55101', '55102', '55401', '55402', '55801', '55802', '56001', '56002', '55701', '55702'],
            'MS': ['39201', '39202', '38601', '38602', '39501', '39502', '38801', '38802', '39701', '39702'],
            'MO': ['63101', '63102', '64101', '64102', '65201', '65202', '63701', '63702', '65801', '65802'],
            'MT': ['59101', '59102', '59701', '59702', '59801', '59802', '59901', '59902', '59401', '59402'],
            'NE': ['68101', '68102', '68501', '68502', '69101', '69102', '68801', '68802', '68701', '68702'],
            'NV': ['89101', '89102', '89501', '89502', '89701', '89702', '89801', '89802', '89901', '89902'],
            'NH': ['03101', '03102', '03301', '03302', '03801', '03802', '03431', '03432', '03561', '03562'],
            'NJ': ['07101', '07102', '08901', '08902', '07001', '07002', '08701', '08702', '07601', '07602'],
            'NM': ['87101', '87102', '87501', '87502', '88001', '88002', '87401', '87402', '87301', '87302'],
            'NY': ['10001', '10002', '10003', '10004', '10005', '11201', '11202', '12201', '14201', '13201'],
            'NC': ['27601', '27602', '28201', '28202', '27101', '27401', '28801', '27701', '28501', '27301'],
            'ND': ['58101', '58102', '58501', '58502', '58201', '58202', '58701', '58702', '58801', '58802'],
            'OH': ['44101', '44102', '43201', '43202', '45201', '45202', '44301', '43701', '45801', '44501'],
            'OK': ['73101', '73102', '74101', '74102', '73701', '73702', '74601', '74602', '73401', '73402'],
            'OR': ['97201', '97202', '97301', '97302', '97401', '97402', '97501', '97502', '97701', '97702'],
            'PA': ['19101', '19102', '19103', '15201', '15202', '17101', '18001', '16501', '19401', '19601'],
            'RI': ['02901', '02902', '02840', '02841', '02806', '02807', '02908', '02909', '02919', '02920'],
            'SC': ['29201', '29202', '29401', '29402', '29601', '29602', '29801', '29802', '29501', '29502'],
            'SD': ['57101', '57102', '57701', '57702', '57401', '57402', '57501', '57502', '57601', '57602'],
            'TN': ['37201', '37202', '38101', '38102', '37401', '37402', '37601', '37602', '37801', '37802'],
            'TX': ['75201', '75202', '77001', '77002', '78701', '73301', '79901', '76101', '77401', '75001'],
            'UT': ['84101', '84102', '84601', '84602', '84401', '84402', '84701', '84702', '84501', '84502'],
            'VT': ['05401', '05402', '05601', '05602', '05701', '05702', '05801', '05802', '05901', '05902'],
            'VA': ['23219', '23220', '23501', '23502', '22201', '22202', '24001', '24002', '23101', '23102'],
            'WA': ['98101', '98102', '99201', '99202', '98401', '98402', '98501', '98502', '98601', '98602'],
            'WV': ['25301', '25302', '26101', '26102', '24701', '24702', '25401', '25402', '25801', '25802'],
            'WI': ['53201', '53202', '53701', '53702', '54901', '54902', '53401', '53402', '54301', '54302'],
            'WY': ['82001', '82002', '82601', '82602', '82801', '82802', '82901', '82902', '83001', '83002']
        }
        
        # Default zip codes if state not found
        self.default_zip_codes = ['90210', '10001', '60601', '30301', '80202']
    
    def generate_random_zip_code(self, state_code=None):
        """Generate a random zip code from available options for a specific state"""
        if state_code and state_code.upper() in self.state_zip_codes:
            zip_code = random.choice(self.state_zip_codes[state_code.upper()])
            logger.info(f"Generated zip code for state {state_code.upper()}: {zip_code}")
        else:
            zip_code = random.choice(self.default_zip_codes)
            logger.info(f"Generated default zip code: {zip_code}")
        return zip_code
    
    def generate_random_ssn(self):
        """Generate a random SSN in XXX-XX-XXXX format"""
        # Generate SSN with proper format but not real SSN
        area = random.randint(100, 899)  # First 3 digits (avoid 000, 666, 900+)
        group = random.randint(10, 99)   # Middle 2 digits (avoid 00)
        serial = random.randint(1000, 9999)  # Last 4 digits (avoid 0000)
        ssn = f"{area:03d}-{group:02d}-{serial:04d}"
        logger.info(f"Generated SSN: {ssn}")
        return ssn
    
    def generate_random_name(self):
        """Generate random first and last name"""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        logger.info(f"Generated name: {first_name} {last_name}")
        return first_name, last_name
    
    def generate_random_address(self):
        """Generate a random address"""
        address = self.fake.street_address()
        logger.info(f"Generated address: {address}")
        return address
    
    def generate_dob_for_65_year_old(self):
        """Generate date of birth for a person who is 65 years old and return components"""
        current_date = datetime.now()
        birth_year = current_date.year - 65
        
        # Random month and day
        birth_month = random.randint(1, 12)
        
        # Handle February and leap years
        if birth_month == 2:
            if self._is_leap_year(birth_year):
                birth_day = random.randint(1, 29)
            else:
                birth_day = random.randint(1, 28)
        elif birth_month in [4, 6, 9, 11]:  # April, June, Sept, Nov have 30 days
            birth_day = random.randint(1, 30)
        else:  # All other months have 31 days
            birth_day = random.randint(1, 31)
        
        # Format full date
        dob_full = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"
        
        # Create individual components
        dob_components = {
            'dateOfBirth': dob_full,
            'dobMonth': f"{birth_month:02d}",
            'dobDay': f"{birth_day:02d}",
            'dobYear': str(birth_year),
            'dobMonthNum': birth_month,
            'dobDayNum': birth_day,
            'dobYearNum': birth_year
        }
        
        logger.info(f"Generated date of birth (age 65): {dob_full}")
        logger.info(f"DOB components - Month: {birth_month:02d}, Day: {birth_day:02d}, Year: {birth_year}")
        
        return dob_components
    
    def _is_leap_year(self, year):
        """Check if a year is a leap year"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    
    def generate_complete_random_person(self, state_code=None):
        """Generate a complete set of random values for a 65-year-old person"""
        logger.info(f"=== STARTING RANDOM DATA GENERATION ===")
        logger.info(f"Target state: {state_code.upper() if state_code else 'None (using defaults)'}")
        
        first_name, last_name = self.generate_random_name()
        ssn = self.generate_random_ssn()
        address = self.generate_random_address()
        zip_code = self.generate_random_zip_code(state_code)
        dob_components = self.generate_dob_for_65_year_old()
        
        person_data = {
            'firstName': first_name,
            'lastName': last_name,
            'ssn': ssn,
            'address': address,
            'zipCode': zip_code,
            'state': state_code.upper() if state_code else None
        }
        
        # Add all DOB components to person data
        person_data.update(dob_components)
        
        # Store in cache for reuse across pages
        self.generated_data_cache = person_data.copy()
        
        logger.info(f"=== COMPLETE GENERATED PERSON DATA ===")
        for key, value in person_data.items():
            logger.info(f"  {key}: {value}")
        logger.info(f"=== END GENERATED DATA ===")
        
        return person_data
    
    def get_cached_data(self):
        """Return the cached generated data for reuse across pages"""
        if self.generated_data_cache:
            logger.info("=== RETRIEVING CACHED DATA FOR REUSE ===")
            for key, value in self.generated_data_cache.items():
                logger.info(f"  {key}: {value}")
            logger.info("=== END CACHED DATA ===")
            return self.generated_data_cache.copy()
        else:
            logger.warning("No cached data available - generate data first")
            return {}
    
    def get_specific_field(self, field_name):
        """Get a specific field from cached data"""
        if field_name in self.generated_data_cache:
            value = self.generated_data_cache[field_name]
            logger.info(f"Retrieved cached field '{field_name}': {value}")
            return value
        else:
            logger.warning(f"Field '{field_name}' not found in cached data")
            return None
    
    def print_random_person(self, state_code=None):
        """Print a randomly generated person's information"""
        person = self.generate_complete_random_person(state_code)
        
        print("=== Random Person Data (Age: 65) ===")
        print(f"First Name: {person['firstName']}")
        print(f"Last Name: {person['lastName']}")
        print(f"SSN: {person['ssn']}")
        print(f"Address: {person['address']}")
        print(f"Zip Code: {person['zipCode']}")
        print(f"Date of Birth: {person['dateOfBirth']}")
        print(f"DOB Month: {person['dobMonth']}")
        print(f"DOB Day: {person['dobDay']}")
        print(f"DOB Year: {person['dobYear']}")
        if state_code:
            print(f"State: {state_code.upper()}")
        print("=" * 40)
        
        return person


def generate_test_data_for_state(state_code, **kwargs):
    """
    Generate test data for a specific state (compatible with form_automation.py)
    Returns data in the format expected by the form automation script
    """
    generator = RandomValuesGenerator()
    person_data = generator.generate_complete_random_person(state_code)
    
    # Return in the format expected by form automation
    return person_data

if __name__ == "__main__":
    import sys
    generator = RandomValuesGenerator()
    
    # Check if state code is provided as command line argument
    state_code = sys.argv[1] if len(sys.argv) > 1 else None
    
    if state_code:
        print(f"Generating 3 random 65-year-old people for state {state_code.upper()}:\n")
    else:
        print("Generating 3 random 65-year-old people (no state specified):\n")
    
    for i in range(3):
        print(f"Person #{i+1}:")
        generator.print_random_person(state_code)
        print()