from flask import Flask, request, Response
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_cors import CORS
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app,resources={
    r"/*":{
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# SETUP LOGGING

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'chatbox_usage.log'),
    maxBytes=10_000_000,
    backupCount=5
)

file_handler.setFormatter(
    logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
)

logger = logging.getLogger('chatbox')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

# GROQ AI SETUP


GROQ_API_KEY = #your api key here
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq AI client initialized successfully")
    print("Groq AI client initialized successfully")
except Exception as e:
    logger.error(f"Groq initialization failed: {e}")
    print(f"Groq initialization failed: {e}")
    groq_client = None

# SESSION STORAGE (RAM only)

active_sessions = {}

# PROVINCE DATA

PROVINCES = {
    '1': 'Mashonaland',
    '2': 'Matabeleland',
    '3': 'Manicaland',
    '4': 'Masvingo',
    '5': 'Midlands',
    '6': 'Mashonaland Central',
    '7': 'Mashonaland East',
    '8': 'Mashonaland West'
}

# CROP DATA

CROP_CATEGORIES = {
    '1': 'cereal',
    '2': 'cash',
    '3': 'legume',
    '4': 'vegetable'
}

CROPS = {
    'cereal': {
        '1': 'Maize',
        '2': 'Sorghum',
        '3': 'Wheat',
        '4': 'Millet'
    },
    'cash': {
        '1': 'Tobacco',
        '2': 'Cotton',
        '3': 'Soybean',
        '4': 'Sunflower'
    },
    'legume': {
        '1': 'Groundnuts',
        '2': 'Cowpeas',
        '3': 'Sugar Beans'
    },
    'vegetable': {
        '1': 'Tomato',
        '2': 'Cabbage',
        '3': 'Onion',
        '4': 'Rape'
    }
}

CROP_SERVICES = {
    '1': 'pest_disease',
    '2': 'soil_fertility',
    '3': 'planting_calendar',
    '4': 'post_harvest'
}

# LIVESTOCK DATA

ANIMAL_CATEGORIES = {
    '1': 'cattle',
    '2': 'small_ruminants',
    '3': 'poultry',
    '4': 'pigs'
}

ANIMALS = {
    'cattle': {
        '1': 'Beef Cattle',
        '2': 'Dairy Cattle'
    },
    'small_ruminants': {
        '1': 'Goats',
        '2': 'Sheep'
    },
    'poultry': {
        '1': 'Layers',
        '2': 'Broilers',
        '3': 'Indigenous Chickens'
    },
    'pigs': {
        '1': 'Pigs'
    }
}

LIVESTOCK_SERVICES = {
    '1': 'disease_management',
    '2': 'nutrition_feed',
    '3': 'breeding',
    '4': 'housing'
}

# MENUS

LANGUAGE_MENUS = {
    'en': " Select your language\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. English\n2. Shona\n3. Ndebele\n",
    'sn': " Sarudza mutauro wako\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. English\n2. Shona\n3. Ndebele\n",
    'nd': " Khetha ulimi lwakho\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. English\n2. Shona\n3. Ndebele\n:"
}

PROVINCE_MENUS = {
    'en': " Select your province\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mashonaland\n2. Matabeleland\n3. Manicaland\n4. Masvingo\n5. Midlands\n6. Mashonaland Central\n7. Mashonaland East\n8. Mashonaland West\n",
    'sn': " Sarudza dunhu rako\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mashonaland\n2. Matabeleland\n3. Manicaland\n4. Masvingo\n5. Midlands\n6. Mashonaland Central\n7. Mashonaland East\n8. Mashonaland West\n",
    'nd': " Khetha isifunda sakho\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mashonaland\n2. Matabeleland\n3. Manicaland\n4. Masvingo\n5. Midlands\n6. Mashonaland Central\n7. Mashonaland East\n8. Mashonaland West\n"
}

SERVICE_MENUS = {
    'en': " SELECT SERVICE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Crop Production\n2. Livestock\n",
    'sn': " SARUDZA SERVICE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Kurima (Crop)\n2. Zvipfuyo (Livestock)\n",
    'nd': " KHETHA SERVICE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Izitshalo (Crop)\n2. Imfuyo (Livestock)\n"
}

CROP_CATEGORY_MENUS = {
    'en': " CROP CATEGORY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Cereal Crops (Maize, Sorghum, Wheat)\n2. Cash Crops (Tobacco, Cotton, Soybean)\n3. Legumes (Groundnuts, Cowpeas)\n4. Vegetables\n",
    'sn': " MAPATO EZVIRIMWA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Zviyo (Chibage, Mapfunde, Gorosi)\n2. Zvirimwa zveMari (Fodya, Donje, Soya)\n3. Nyemba (Nzungu, Nyemba)\n4. Muriwo\n",
    'nd': " IZIGABA ZEZITSHALO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Okusanhla (Umbila, Amabele, Ukolweni)\n2. Ezemali (Ifuba, Ugabho, Sobho)\n3. Imbotshana (Amantongomane, Izimbotshana)\n4. Imifino\n"
}

def get_crop_menu(language, category):
    """Get crop selection menu based on category"""
    menus = {
        'cereal': {
            'en': " SELECT CROP\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Maize\n2. Sorghum\n3. Wheat\n4. Millet\n",
            'sn': " SARUDZA CHIRIMWA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Chibage\n2. Mapfunde\n3. Gorosi\n4. Zviyo\n",
            'nd': " KHETHA ISITSHALO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Umbila\n2. Amabele\n3. Ukolweni\n4. Inyawuthi\n"
        },
        'cash': {
            'en': " SELECT CASH CROP\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Tobacco\n2. Cotton\n3. Soybean\n4. Sunflower\n",
            'sn': " SARUDZA CHIRIMWA CHEMARI\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Fodya\n2. Donje\n3. Soya\n4. Sunflower\n",
            'nd': " KHETHA ISITSHALO SEMALI\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Ifuba\n2. Ugabho\n3. Sobho\n4. Unwabu\n"
        },
        'legume': {
            'en': " SELECT LEGUME\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Groundnuts\n2. Cowpeas\n3. Sugar Beans\n",
            'sn': " SARUDZA NYEMBA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Nzungu\n2. Nyemba\n3. Bhinzi\n",
            'nd': " KHETHA IMBOTSHANA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Amantongomane\n2. Izimbotshana\n3. Ubhontshisi\n"
        },
        'vegetable': {
            'en': " SELECT VEGETABLE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Tomato\n2. Cabbage\n3. Onion\n4. Rape\n",
            'sn': " SARUDZA MURIWO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Tomato\n2. Kabbage\n3. Anyanisi\n4. Rape\n",
            'nd': " KHETHA UMIFINO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Utamatisi\n2. Iklabishi\n3. U-anyanisi\n4. Irape\n"
        }
    }
    return menus.get(category, menus['cereal']).get(language, menus['cereal']['en'])

CROP_SERVICE_MENUS = {
    'en': " SERVICE TYPE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Pest & Disease Management (IPM)\n2. Soil Fertility & Nutrient Management\n3. Planting Calendar\n4. Post-Harvest Handling\n",
    'sn': " RUDZI RWEBASA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Kudzora Zvipembenene neZvirwere\n2. Kugadzirisa Ivhu neZvirimwa\n3. Karenda Yekudyara\n4. Kuchengeta Mushure meKukohwa\n",
    'nd': " UHLOBO LWENSIZA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Ukuphatha Izinambuzane Nezifo\n2. Ukuphatha Umhlabathi Nokuvundisa\n3. Ikhalenda Yokutshala\n4. Ukuphatha Emva Kokuvuna\n"
}

ANIMAL_CATEGORY_MENUS = {
    'en': " ANIMAL CATEGORY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Cattle\n2. Goats & Sheep\n3. Poultry\n4. Pigs\n",
    'sn': " MAPATO EZVIPFUYO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mombe\n2. Mbudzi neHwayi\n3. Huku\n4. Nguruve\n",
    'nd': " IZIGABA ZEMFUYO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Izinkomo\n2. Izimbuzi Nezimvu\n3. Izinkukhu\n4. Izingulube\n"
}

def get_animal_menu(language, category):
    """Get animal selection menu based on category"""
    menus = {
        'cattle': {
            'en': " SELECT ANIMAL\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Beef Cattle\n2. Dairy Cattle\n",
            'sn': " SARUDZA MOMBE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mombe dzeNyama\n2. Mombe dzeMukaka\n",
            'nd': " KHETHA INKOMO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Ezinyama\n2. Ezobisi\n"
        },
        'small_ruminants': {
            'en': " SELECT ANIMAL\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Goats\n2. Sheep\n",
            'sn': " SARUDZA MHUKO\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Mbudzi\n2. Hwayi\n",
            'nd': " KHETHA ISILWANA\n━━━━━━━━━━━━═════════════════════════════\n\n1. Izimbuzi\n2. Izimvu\n"
        },
        'poultry': {
            'en': " SELECT POULTRY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Layers (Eggs)\n2. Broilers (Meat)\n3. Indigenous Chickens\n",
            'sn': " SARUDZA HUKU\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Huku dzeMazai\n2. Huku dzeNyama\n3. Huku dzeChivanhu\n",
            'nd': " KHETHA IZINKUKHU\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Emaqanda\n2. Eminyama\n3. Endabuko\n"
        },
        'pigs': {
            'en': " SELECT ANIMAL\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Pigs\n",
            'sn': " SARUDZA NGURUVE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Nguruve\n",
            'nd': " KHETHA INGULUBE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Izingulube\n"
        }
    }
    return menus.get(category, menus['cattle']).get(language, menus['cattle']['en'])

LIVESTOCK_SERVICE_MENUS = {
    'en': " SERVICE TYPE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Disease Management & Health\n2. Nutrition & Feed Management\n3. Breeding & Reproduction\n4. Housing & Shelter\n",
    'sn': " RUDZI RWEBASA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Kutarisira Zvirwere neUtano\n2. Kudya neKudyiwa\n3. Kuberekesa\n4. Danga neKugara\n",
    'nd': " UHLOBO LWENSIZA\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n1. Ukuphatha Izifo Nezempilo\n2. Ukondla Nokuphatha Ukudla\n3. Ukuzalanisa\n4. Izindlu Nezindawo Zokuhlala\n"
}

EXIT_MESSAGES = {
    'en': "Thank you for using ChatBox ZW! \nCall again for farming advice.",
    'sn': "Tatenda kushandisa ChatBox ZW! \nDzokai zvakare.",
    'nd': "Ngiyabonga ngokusebenzisa ChatBox ZW! \nPhindani futhi."
}
# GROQ AI RESPONSE FUNCTION
def get_ai_response_groq(language, province, category, sub_category=None, service_type=None):
    """Generate AI response using Groq"""
    
    if groq_client is None:
        logger.warning("Groq client not available, using mock response")
        return get_mock_response(language, province, category)
    
    # Build detailed prompt based on selections
    if category == 'crop':
        crop_name = sub_category if sub_category else "crops"
        service_map = {
            'pest_disease': "pest and disease management (IPM)",
            'soil_fertility': "soil fertility and nutrient management",
            'planting_calendar': "planting calendar and optimal timing",
            'post_harvest': "post-harvest handling and storage"
        }
        service_text = service_map.get(service_type, "general advice")
        query_text = f"Provide {service_text} for {crop_name} farming in {province}, Zimbabwe."
    elif category == 'livestock':
        animal_name = sub_category if sub_category else "livestock"
        service_map = {
            'disease_management': "disease management and health",
            'nutrition_feed': "nutrition and feed management",
            'breeding': "breeding and reproduction",
            'housing': "housing and shelter management"
        }
        service_text = service_map.get(service_type, "general advice")
        query_text = f"Provide {service_text} for {animal_name} production in {province}, Zimbabwe."
    else:
        query_text = f"Provide agricultural advice for {category} in {province}, Zimbabwe."
    
    # Language mapping
    language_map = {
        'en': 'English',
        'sn': 'Shona',
        'nd': 'Ndebele'
    }
    target_language = language_map.get(language, 'English')
    
    # System prompt
    system_prompt = """You are ChatBox ZW, a trusted agricultural extension assistant for Zimbabwean farmers. 
Provide accurate, practical, and locally relevant farming advice. 
Keep responses brief and actionable for USSD (under 400 characters).
Focus on Zimbabwe-specific conditions, seasons, and practices."""
    
    # User prompt with language instruction
    user_prompt = f"""{query_text}

IMPORTANT: Respond in {target_language} language.
Keep response under 400 characters.
Be practical and specific to {province}, Zimbabwe.

Response:"""
    
    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=400,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Trim for USSD
        if len(response_text) > 160:
            response_text = response_text[:157] + "..."
        
        logger.info(f"Groq response generated for {category} in {province}")
        return f"{response_text}\n\nPress 0 to exit"
        
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return get_mock_response(language, province, category)

def get_mock_response(language, province, category):
    """Fallback mock responses when AI is unavailable"""
    
    if category == 'crop':
        responses = {
            'en': f"CROP PRODUCTION ADVICE for {province}\n\nRecommended: Maize, Soybean, Groundnuts\nPlanting: November - December\nSeed rate: 25kg per hectare\n\nPress 0 to exit",
            'sn': f"ZANO REKURIMA mu {province}\n\nZvirimwa: Chibage, Soya, Nzungu\nKudyara: Mbudzi - Zvita\nMbeu: 25kg pahekita\n\nDzvanya 0 kuti ubude",
            'nd': f"ISELULEKO SEZOLIMO e {province}\n\nIzitshalo: Umbila, Sobho, Amantongomane\nUkutshala: Lwezi - Zibandlela\nImbewu: 25kg ngehekitha\n\nCindezela 0 ukuphuma"
        }
    elif category == 'livestock':
        responses = {
            'en': f"LIVESTOCK ADVICE for {province}\n\nRecommended: Cattle, Goats, Poultry\nVaccination: Every 6 months\nPasture: Rotational grazing\n\nPress 0 to exit",
            'sn': f"ZANO REZVIPFUYO mu {province}\n\nZvipfuyo: Mombe, Mbudzi, Huku\nMajekiseni: Pamwedzi mitanhatu\nMafuro: Kutenderera\n\nDzvanya 0 kuti ubude",
            'nd': f"ISELULEKO SEMFUYO e {province}\n\nImfuyo: Izinkomo, Izimbuzi, Izinkukhu\nImijovo: Njalo ezinyangeni eziyisithupha\nAmadlelo: Ukutshintshintsha\n\nCindezela 0 ukuphuma"
        }
    else:
        responses = {
            'en': f"ADVICE for {province}\nPress 0 to exit",
            'sn': f"ZANO mu {province}\nDzvanya 0 kuti ubude",
            'nd': f"ISELULEKO e {province}\nCindezela 0 ukuphuma"
        }
    
    return responses.get(language, responses['en'])

# For backward compatibility
get_ai_response = get_ai_response_groq

# USSD CALLBACK HANDLER

@app.route('/ussd', methods=['POST'])
def ussd_callback():
    session_id = request.form.get('sessionId')
    phone = request.form.get('phoneNumber', 'unknown')
    text = request.form.get('text', '')
    service_code = request.form.get('serviceCode', '')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    #=====VALIDATE USSD CODE =======
    if service_code and service_code != "*384#":
        logger.warning(f"REJECTED | Invalid USSD code: {service_code} | Phone: {phone}")
        error_response = "END UNKNOWN APPLICATION\n\nThis service is only available on *384#"
        return Response(
            f'{error_response}',
            mimetype='application/json'
        )
    session_display = session_id[:8] if session_id else 'None'
    logger.info(f"INCOMING | Phone: {phone} | Input: '{text}' | Session: {session_id[:8] if session_id else 'None'}")    
    # Initialize new session
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'language': None,
            'province': None,
            'service_category': None,
            'crop_category': None,
            'crop': None,
            'crop_service': None,
            'animal_category': None,
            'animal': None,
            'livestock_service': None,
            'state': 'awaiting_language',
            'start_time': datetime.now()
        }
        logger.info(f"NEW SESSION | Phone: {phone}")
    
    session = active_sessions[session_id]
    
    # Parse navigation path
    parts = text.split('*') if text else []
    current_level = len(parts)
    current_choice = parts[-1] if parts else ''
    
    logger.info(f"State: {session['state']} | Level: {current_level} | Choice: {current_choice}")
    
    # ========== EXIT SESSION (Always check first) ==========
    if current_choice == '0':
        duration = datetime.now() - session['start_time']
        logger.info(f"SESSION END | Phone: {phone} | Duration: {duration.total_seconds():.1f}s")
        del active_sessions[session_id]
        lang = session.get('language', 'en')
        response_text = EXIT_MESSAGES[lang]
        return Response(
            f'{"END {response_text}"}',
            mimetype='application/json'
        )
    
    # ========== STEP 1: LANGUAGE SELECTION ==========
    if session['state'] == 'awaiting_language':
        if not text:
            response_text = LANGUAGE_MENUS['en']
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        
        if current_choice == '1':
            session['language'] = 'en'
            session['state'] = 'awaiting_province'
            logger.info(f"Language: English | Phone: {phone}")
            response_text = PROVINCE_MENUS['en']
            return Response(
                f' {response_text}',
                mimetype='application/json'
            )
        elif current_choice == '2':
            session['language'] = 'sn'
            session['state'] = 'awaiting_province'
            logger.info(f"Language: Shona | Phone: {phone}")
            response_text = PROVINCE_MENUS['sn']
            return Response(
                f' {response_text}',
                mimetype='application/json'
            )
        elif current_choice == '3':
            session['language'] = 'nd'
            session['state'] = 'awaiting_province'
            logger.info(f"Language: Ndebele | Phone: {phone}")
            response_text = PROVINCE_MENUS['nd']
            return Response(
                f' {response_text}',
                mimetype='application/json'
            )
        else:
            response_text = LANGUAGE_MENUS['en']
            return Response(
                f'{{"response": "CON {response_text}", "sessionId": "{session_id}"}}',
                mimetype='application/json'
            )
    
    # ========== STEP 2: PROVINCE SELECTION ==========
    if session['state'] == 'awaiting_province':
        if current_choice in PROVINCES:
            session['province'] = PROVINCES[current_choice]
            session['state'] = 'awaiting_service'
            logger.info(f"Province: {session['province']} | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = PROVINCE_MENUS[lang]
            return Response(
                f'{{"response": "CON {response_text}", "sessionId": "{session_id}"}}',
                mimetype='application/json'
            )
    
    # ========== STEP 3: SERVICE CATEGORY SELECTION ==========
    if session['state'] == 'awaiting_service':
        if current_choice == '1':  # Crop Production
            session['service_category'] = 'crop'
            session['state'] = 'awaiting_crop_category'
            logger.info(f"Service: Crop Production | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = CROP_CATEGORY_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        elif current_choice == '2':  # Livestock
            session['service_category'] = 'livestock'
            session['state'] = 'awaiting_animal_category'
            logger.info(f"Service: Livestock | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = ANIMAL_CATEGORY_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 4a: CROP CATEGORY SELECTION ==========
    if session['state'] == 'awaiting_crop_category':
        if current_choice in CROP_CATEGORIES:
            session['crop_category'] = CROP_CATEGORIES[current_choice]
            session['state'] = 'awaiting_specific_crop'
            logger.info(f"Crop Category: {session['crop_category']} | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = get_crop_menu(lang, session['crop_category'])
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = CROP_CATEGORY_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 5a: SPECIFIC CROP SELECTION ==========
    if session['state'] == 'awaiting_specific_crop':
        crop_category = session.get('crop_category', 'cereal')
        if crop_category in CROPS and current_choice in CROPS[crop_category]:
            session['crop'] = CROPS[crop_category][current_choice]
            session['state'] = 'awaiting_crop_service'
            logger.info(f"Crop: {session['crop']} | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = CROP_SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = get_crop_menu(lang, crop_category)
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 6a: CROP SERVICE TYPE SELECTION ==========
    if session['state'] == 'awaiting_crop_service':
        if current_choice in CROP_SERVICES:
            session['crop_service'] = CROP_SERVICES[current_choice]
            session['state'] = 'completed'
            logger.info(f"Crop Service: {session['crop_service']} | Crop: {session['crop']} | Phone: {phone}")
            
            # Generate AI response
            ai_response = get_ai_response_groq(
                session['language'],
                session['province'],
                'crop',
                session['crop'],
                session['crop_service']
            )
            
            # Add exit instruction
            final_response = f"{ai_response}\n\nPress 0 to exit"
            
            return Response(
                f'{final_response}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = CROP_SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 4b: ANIMAL CATEGORY SELECTION ==========
    if session['state'] == 'awaiting_animal_category':
        if current_choice in ANIMAL_CATEGORIES:
            session['animal_category'] = ANIMAL_CATEGORIES[current_choice]
            session['state'] = 'awaiting_specific_animal'
            logger.info(f"Animal Category: {session['animal_category']} | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = get_animal_menu(lang, session['animal_category'])
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = ANIMAL_CATEGORY_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 5b: SPECIFIC ANIMAL SELECTION ==========
    if session['state'] == 'awaiting_specific_animal':
        animal_category = session.get('animal_category', 'cattle')
        if animal_category in ANIMALS and current_choice in ANIMALS[animal_category]:
            session['animal'] = ANIMALS[animal_category][current_choice]
            session['state'] = 'awaiting_livestock_service'
            logger.info(f"Animal: {session['animal']} | Phone: {phone}")
            lang = session.get('language', 'en')
            response_text = LIVESTOCK_SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = get_animal_menu(lang, animal_category)
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== STEP 6b: LIVESTOCK SERVICE TYPE SELECTION ==========
    if session['state'] == 'awaiting_livestock_service':
        if current_choice in LIVESTOCK_SERVICES:
            session['livestock_service'] = LIVESTOCK_SERVICES[current_choice]
            session['state'] = 'completed'
            logger.info(f"Livestock Service: {session['livestock_service']} | Animal: {session['animal']} | Phone: {phone}")
            
            # Generate AI response
            ai_response = get_ai_response_groq(
                session['language'],
                session['province'],
                'livestock',
                session['animal'],
                session['livestock_service']
            )
            
            # Add exit instruction
            final_response = f"{ai_response}\n\nPress 0 to exit"
            
            return Response(
                f'{final_response}',
                mimetype='application/json'
            )
        else:
            lang = session.get('language', 'en')
            response_text = LIVESTOCK_SERVICE_MENUS[lang]
            return Response(
                f'{response_text}',
                mimetype='application/json'
            )
    
    # ========== COMPLETED STATE (Show AI response again if needed) ==========
    if session['state'] == 'completed':
        response_text = "Your session has ended. Dial *384# to start a new session."
        return Response(
            f'{response_text}',
            mimetype='application/json'
        )
    
    # ========== DEFAULT FALLBACK ==========
    lang = session.get('language', 'en')
    response_text = f"Press 0 to exit"
    return Response(
        f'{response_text}',
        mimetype='application/json'
    )

# HEALTH CHECK ENDPOINT

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "active_sessions": len(active_sessions)}

if __name__ == '__main__':
    logger.info("ChatBox ZW Starting with Groq AI...")
    logger.info("Server: http://localhost:9007")
    logger.info("Health: http://localhost:9007/health")
    logger.info("USSD: http://localhost:9007/ussd")
    app.run(host='0.0.0.0', port=9007, debug=True)
