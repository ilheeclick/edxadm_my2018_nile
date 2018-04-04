# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'u0-$j2v%)u-w52*spjq7)i@8rv*=!el9ua+@j9j-i_h_$u-bmb'
DEBUG = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'b930208'
EMAIL_HOST_PASSWORD = 'aldzltbfl5842!'
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'tracking_control',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.core.mail.backends.smtp.EmailBackend',
)

ROOT_URLCONF = 'management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'djangomako.backends.MakoBackend',
        'NAME': 'mako',
        'DIRS': [
            #BASE_DIR + '/home/templates/<app>/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'management.wsgi.application'

#database_id = '172.17.101.117'
database_id = '127.0.0.1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'edxapp',
        'USER': 'edxapp001',
        'PASSWORD': 'password',
        'HOST': database_id,
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

APPEND_SLASH = True
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'

STATIC_URL = '/home/static/'

STATICFILES_DIRS = (
    ("css", os.path.join(BASE_DIR, 'static/css')),
    ("image", os.path.join(BASE_DIR, 'static/image')),
    ("js", os.path.join(BASE_DIR, 'static/js')),
    ("font", os.path.join(BASE_DIR, 'static/font')),
    ("excel", os.path.join(BASE_DIR, 'home/static/excel')),
)

# ============================================================================================================
# global variables ===========================================================================================
# ============================================================================================================

EXCEL_PATH = '/home/project/management/home/static/excel/'
UPLOAD_DIR = '/home/project/management/home/static/upload/'
EXCEL_PATH = BASE_DIR + '/home/static/excel/'
UPLOAD_DIR = BASE_DIR + '/home/static/uploads/'
LOGZIP_DIR = '/home/ubuntu/project/management/tracking_control/static/uploads/'
# LOGZIP_DIR = '/Users/kotech/workspace/management2/management/static/uploads/'
WEB1_HOST = '172.17.101.116'
WEB2_HOST = '172.17.101.116'
WEB1_LOG = '/edx/var/log/tracking/'
WEB2_LOG = '/edx/var/log/tracking/'
LOCAL1_DIR = '/home/ubuntu/project/management/tracking_control/static/tracking_w1/'
LOCAL2_DIR = '/home/ubuntu/project/management/tracking_control/static/tracking_w2/'
CHANGE_DIR = '/home/ubuntu/project/management/tracking_control/static/ch_tracking/'
# LOG_COMPLETE_DIR = '/home/ubuntu/project/management/tracking_control/static/zip_tracking/'
# LOCAL1_DIR = '/Users/kotech/workspace/scpTest/tracking_w1/'
# LOCAL2_DIR = '/Users/kotech/workspace/scpTest/tracking_w2/'
# CHANGE_DIR = '/Users/kotech/workspace/scpTest/ch_tracking/'
# LOG_COMPLETE_DIR = '/Users/kotech/workspace/scpTest/zip_tracking/'

REAL_WEB1_HOST = '172.17.101.116'
REAL_WEB1_ID = 'ubuntu'
REAL_WEB1_PW = '?kmooc'

debug = True

USER_NAME = 'ubuntu'

dic_univ = {
    'KYUNGNAMUNIVk': u'경남대학교',
    'KHUk': u'경희대학교',
    'KoreaUnivK': u'고려대학교',
    'DGUk': u'대구대학교',
    'PNUk': u'부산대학교',
    'SMUCk': u'상명대학교(천안)',
    'SMUk': u'상명대학교(서울)',
    'SNUk': u'서울대학교',
    'SKKUk': u'성균관대학교',
    'KKUk': u'건국대학교(글로컬)',
    'SSUk': u'성신여자대학교',
    'SejonguniversityK': u'세종대학교',
    'SookmyungK': u'숙명여자대학교',
    'YSUk': u'연세대학교',
    'YeungnamUnivK': u'영남대학교',
    'UOUk': u'울산대학교',
    'EwhaK': u'이화여자대학교',
    'INHAuniversityK': u'인하대학교',
    'CBNUk': u'전북대학교',
    'KonkukK': u'건국대학교',
    'KSUk': u'경성대학교',
    'SOGANGk': u'서강대학교',
    'POSTECHk': u'포항공과대학교',
    'KAISTk': u'한국과학기술원',
    'HYUk': u'한양대학교',
    'HongikUnivK': u'홍익대학교',
    'CAUk': u'중앙대학교',
    'GachonUnivK': u'가천대학교',
    'DonggukK': u'동국대학교',
    'DSUk': u'동신대학교',
    'DAUk': u'동아대학교',
    'TUk': u'동명대학교',
    'MokwonK': u'목원대학교',
    'PCUk': u'배재대학교',
    'PKNUk': u'부경대학교',
    'SunMoonK': u'선문대학교',
    'SCHk': u'순천향대학교',
    'WSUK': u'우송대학교',
    'WKUk': u'원광대학교',
    'InhatcK': u'인하공업전문대학',
    'ChosunK': u'조선대학교',
    'CNUk': u'충남대학교',
    'ChungbukK': u'충북대학교',
    'KonYangK': u'건양대학교',
    'UOSk': u'서울시립대학교',
    'SoongsilUnivK': u'숭실대학교',
    'JNUk': u'전남대학교',
    'CKUk': u'가톨릭관동대학교',
    'HallymK': u'한림대학교',
    'KONGJUk': u'공주대학교',
    'SEOULTECHk': u'서울과학기술대학교',
    'SKUk': u'성결대학교',
    'AYUk': u'안양대학교',
    'YonseiWK': u'연세대학교(원주)',
    'HansungK': u'한성대학교',
    'KUMOHk': u'금오공과대학교',
    'DKUK': u'단국대학교',
    'BUFSk': u'부산외국어대학교',
    'SWUk': u'서울여자대학교',
    'SWUK': u'서울여자대학교',
    'SYUk': u'삼육대학교',
    'KNUk': u'경북대학교',
    'KIUk': u'경일대학교',
    'KMUk': u'국민대학교',
    'KMUK': u'국민대학교',
    'SWUK': u'서울여자대학교',
    'PTUk': u'평택대학교',
    'DCUk': u'대구가톨릭대학교',
    'DHUk': u'대구한의대학교',
    'DJUk': u'대전대학교',
    'CUKk': u'가톨릭대학교',
    'JEJUk': u'제주대학교',
    'HGUk': u'한동대학교',
    'PTUk': u'평택대학교',
    'SKP.KAISTk': u'서울대, 한국과학기술원, 포항공대',
    'SKP.SNUk': u'서울대, 한국과학기술원, 포항공대',
    'SKP.POSTECHk': u'서울대, 한국과학기술원, 포항공대',
    'SKP_KAISTk': u'서울대, 한국과학기술원, 포항공대',
    'SKP_SNUk': u'서울대, 한국과학기술원, 포항공대',
    'SKP_POSTECHk': u'서울대, 한국과학기술원, 포항공대'
}

classfy = {
    'hum': u'인문',
    'social': u'사회',
    'edu': u'교육',
    'eng': u'공학',
    'nat': u'자연',
    'med': u'의약',
    'art': u'예체능'
}

middle_classfy = {
    'metr': u'의료',
    'nurs': u'간호',
    'phar': u'약학',
    'heal': u'치료ㆍ보건',
    'dsgn': u'디자인',
    'appl': u'응용예술',
    'danc': u'무용ㆍ체육',
    'form': u'미술ㆍ조형',
    'play': u'연극ㆍ영화',
    'musc': u'음악',
    'cons': u'건축',
    'civi': u'토목ㆍ도시',
    'traf': u'교통ㆍ운송',
    'mach': u'기계ㆍ금속',
    'elec': u'전기ㆍ전자',
    'deta': u'정밀ㆍ에너지',
    'matr': u'소재ㆍ재료',
    'comp': u'컴퓨터ㆍ통신',
    'indu': u'산업',
    'cami': u'화공',
    'other': u'기타',
    'lang': u'언어ㆍ문학',
    'husc': u'인문과학',
    'busn': u'경영ㆍ경제',
    'law': u'법률',
    'scsc': u'사회과학',
    'agri': u'농림ㆍ수산',
    'bio': u'생물ㆍ화학ㆍ환경',
    'life': u'생활과학',
    'math': u'수학ㆍ물리ㆍ천문ㆍ지리',
    'enor': u'교육일반',
    'ekid': u'유아교육',
    'espc': u'특수교육',
    'elmt': u'초등교육',
    'emdd': u'중등교육',
}

countries = {
    "AF": "Afghanistan",
    "AX": "Åland Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "CV": "Cabo Verde",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia",
    "KM": "Comoros",
    "CD": "Congo (the Democratic Republic of the)",
    "CG": "Congo",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "CI": "Côte d'Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FK": "Falkland Islands  [Malvinas]",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran (Islamic Republic of)",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (the Democratic People's Republic of)",
    "KR": "Korea (the Republic of)",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MK": "Macedonia (the former Yugoslav Republic of)",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia (Federated States of)",
    "MD": "Moldova (the Republic of)",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RU": "Russian Federation",
    "RW": "Rwanda",
    "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SZ": "Swaziland",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic",
    "TW": "Taiwan (Province of China)",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom of Great Britain and Northern Ireland",
    "UM": "United States Minor Outlying Islands",
    "US": "United States of America",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela (Bolivarian Republic of)",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}

LOGIN_URL = '/accounts/login/'
