#!/usr/bin/env python3
"""
Generator script for geo_hierarchy.py

Reads data.json and produces a complete geo_hierarchy.py with ALL cities,
water bodies, and helper functions.
"""

import json
import hashlib
import os
import re

# ---------------------------------------------------------------------------
# 1. CITY COORDINATES DICTIONARY
# ---------------------------------------------------------------------------
# Approximate (latitude, longitude) for Indian cities.
# For cities not listed here, we fall back to the state capital with a
# deterministic offset derived from the city name hash.

CITY_COORDS = {
    # --- Andhra Pradesh ---
    "Vijayawada": (16.51, 80.63),
    "Amaravati": (16.57, 80.36),
    "Guntur": (16.30, 80.44),
    "Kurnool": (15.83, 78.04),
    "Nellore": (14.44, 79.97),
    "Tirupati": (13.63, 79.42),
    "Rajahmundry": (17.00, 81.78),
    "Rajahmundry (Rajamahendravaram)": (17.00, 81.78),
    "Kakinada": (16.94, 82.24),
    "Srikakulam": (18.30, 83.90),
    "Kadapa": (14.47, 78.82),
    "Kadapa (Cuddapah)": (14.47, 78.82),
    "Anantapur": (14.68, 77.60),
    "Srisailam": (15.85, 78.87),
    "Eluru": (16.71, 81.10),
    "Bhimavaram": (16.54, 81.52),
    "Amalapuram": (16.58, 82.00),
    "Machilipatnam": (16.19, 81.14),
    "Ongole": (15.50, 80.05),
    "Nandyal": (15.48, 78.48),
    "Proddutur": (14.75, 78.55),
    "Tadepalligudem": (16.81, 81.53),
    "Tenali": (16.24, 80.64),
    "Narasaraopet": (16.24, 80.05),
    "Bapatla": (15.90, 80.47),
    "Vizianagaram": (18.12, 83.42),
    "Hindupur": (13.83, 77.49),
    "Dharmavaram": (14.41, 77.72),
    "Adoni": (15.63, 77.27),
    "Mantralayam": (15.67, 77.38),
    "Alampur": (15.88, 78.13),
    "Nagarjuna Sagar": (16.57, 79.31),
    "Dowleswaram": (16.95, 81.78),
    "Palakollu": (16.53, 81.73),
    "Kovvur": (17.01, 81.73),
    "Rajam": (18.45, 83.64),
    "Palasa": (18.77, 84.42),

    # --- Arunachal Pradesh ---
    "Itanagar": (27.08, 93.62),
    "Pasighat": (28.07, 95.33),
    "Tawang": (27.59, 91.87),
    "Tezu": (27.92, 96.17),
    "Along (Aalo)": (28.17, 94.80),
    "Ziro": (27.54, 93.83),
    "Bomdila": (27.26, 92.42),
    "Roing": (28.14, 95.84),
    "Changlang": (27.13, 95.73),
    "Namsai": (27.69, 95.87),
    "Daporijo": (27.99, 94.22),
    "Khonsa": (27.02, 95.50),
    "Yingkiong": (28.63, 95.02),
    "Anini": (28.80, 95.87),
    "Seppa": (27.33, 92.97),
    "Basar": (27.99, 94.69),
    "Koloriang": (27.90, 93.58),
    "Naharlagun": (27.10, 93.70),
    "Miao": (27.48, 96.27),

    # --- Assam ---
    "Guwahati": (26.14, 91.74),
    "Dibrugarh": (27.47, 94.91),
    "Silchar": (24.82, 92.80),
    "Tezpur": (26.63, 92.80),
    "Jorhat": (26.76, 94.22),
    "Nagaon": (26.35, 92.68),
    "Tinsukia": (27.49, 95.36),
    "Goalpara": (26.17, 90.63),
    "Dhubri": (26.02, 89.98),
    "Bongaigaon": (26.48, 90.56),
    "Karimganj": (24.87, 92.35),
    "Sivasagar": (26.98, 94.64),
    "North Lakhimpur": (27.24, 94.10),
    "Barpeta": (26.32, 91.00),
    "Nalbari": (26.44, 91.44),
    "Kokrajhar": (26.40, 90.27),
    "Haflong": (25.17, 93.02),
    "Diphu": (25.84, 93.43),
    "Hailakandi": (24.68, 92.57),
    "Mangaldoi": (26.44, 92.03),
    "Hojai": (26.00, 92.86),
    "Biswanath Chariali": (26.73, 93.15),
    "Majuli (island town)": (26.95, 94.17),
    "Sadiya": (27.83, 95.67),
    "Rangia": (26.45, 91.63),
    "Pathsala": (26.49, 91.18),

    # --- Bihar ---
    "Patna": (25.61, 85.14),
    "Gaya": (24.80, 85.00),
    "Bhagalpur": (25.24, 86.97),
    "Muzaffarpur": (26.12, 85.39),
    "Darbhanga": (26.15, 85.90),
    "Munger": (25.37, 86.47),
    "Begusarai": (25.42, 86.13),
    "Samastipur": (25.86, 85.78),
    "Purnia": (25.78, 87.47),
    "Arrah (Ara)": (25.56, 84.66),
    "Hajipur": (25.69, 85.21),
    "Chapra (Chhapra)": (25.78, 84.74),
    "Sasaram": (24.95, 84.03),
    "Buxar": (25.56, 83.98),
    "Bihar Sharif": (25.20, 85.52),
    "Rajgir": (25.03, 85.42),
    "Motihari": (26.66, 84.92),
    "Bettiah": (26.80, 84.52),
    "Katihar": (25.54, 87.57),
    "Saharsa": (25.88, 86.60),
    "Madhubani": (26.35, 86.07),
    "Sitamarhi": (26.59, 85.49),
    "Supaul": (26.12, 86.60),
    "Kishanganj": (26.10, 87.95),
    "Banka": (24.89, 86.92),
    "Aurangabad (Bihar)": (24.75, 84.37),
    "Nawada": (24.89, 85.54),
    "Bodh Gaya": (24.70, 84.99),
    "Sonepur": (25.70, 85.18),
    "Dehri": (24.91, 84.18),
    "Barh": (25.48, 85.71),
    "Mokama": (25.40, 85.92),
    "Sultanganj": (25.25, 86.74),
    "Kahalgaon": (25.26, 87.24),
    "Jamalpur": (25.31, 86.49),

    # --- Chhattisgarh ---
    "Raipur": (21.25, 81.63),
    "Bilaspur": (22.08, 82.15),
    "Jagdalpur": (19.08, 82.02),
    "Durg": (21.19, 81.28),
    "Bhilai": (21.21, 81.38),
    "Korba": (22.35, 82.68),
    "Rajnandgaon": (21.10, 81.03),
    "Raigarh": (21.90, 83.40),
    "Ambikapur": (23.12, 83.20),
    "Dhamtari": (20.71, 81.55),
    "Mahasamund": (21.11, 82.10),
    "Kanker": (20.27, 81.49),
    "Dantewada": (18.90, 81.35),
    "Bijapur (CG)": (18.83, 80.83),
    "Janjgir": (22.01, 82.57),
    "Mungeli": (22.07, 81.68),
    "Balod": (20.73, 81.20),
    "Bemetara": (21.72, 81.53),
    "Kondagaon": (19.60, 81.66),
    "Sukma": (18.39, 81.66),
    "Narayanpur": (19.73, 81.25),
    "Surajpur": (23.21, 82.87),
    "Balrampur (CG)": (23.10, 83.60),
    "Kawardha (Kabirdham)": (22.01, 81.23),
    "Gariaband": (20.63, 82.06),

    # --- Goa ---
    "Panaji": (15.49, 73.83),
    "Margao": (15.27, 73.96),
    "Vasco da Gama": (15.40, 73.81),
    "Mapusa": (15.59, 73.81),
    "Ponda": (15.40, 74.01),
    "Canacona": (15.01, 74.05),
    "Quepem": (15.21, 74.08),
    "Bicholim": (15.59, 73.95),
    "Pernem": (15.72, 73.80),
    "Sanguem": (15.23, 74.15),

    # --- Gujarat ---
    "Ahmedabad": (23.02, 72.57),
    "Surat": (21.17, 72.83),
    "Vadodara": (22.31, 73.19),
    "Rajkot": (22.30, 70.80),
    "Gandhinagar": (23.22, 72.64),
    "Bhavnagar": (21.76, 72.15),
    "Jamnagar": (22.47, 70.07),
    "Junagadh": (21.52, 70.46),
    "Anand": (22.56, 72.95),
    "Bharuch": (21.70, 73.00),
    "Morbi": (22.82, 70.83),
    "Nadiad": (22.69, 72.86),
    "Surendranagar": (22.73, 71.68),
    "Mehsana": (23.59, 72.38),
    "Palanpur": (24.17, 72.44),
    "Valsad": (20.63, 72.93),
    "Navsari": (20.95, 72.92),
    "Kutch (Bhuj)": (23.25, 69.67),
    "Porbandar": (21.64, 69.61),
    "Dwarka": (22.24, 68.97),
    "Godhra": (22.78, 73.62),
    "Dahod": (22.84, 74.25),
    "Veraval": (20.91, 70.37),
    "Gandhidham": (23.08, 70.13),
    "Bardoli": (21.12, 73.11),
    "Patan": (23.85, 72.13),
    "Narmada (Rajpipla)": (21.87, 73.50),

    # --- Haryana ---
    "Faridabad": (28.41, 77.31),
    "Gurugram": (28.46, 77.03),
    "Karnal": (29.69, 76.98),
    "Ambala": (30.38, 76.78),
    "Panipat": (29.39, 76.97),
    "Hisar": (29.15, 75.72),
    "Rohtak": (28.89, 76.59),
    "Sonipat": (28.99, 77.02),
    "Yamunanagar": (30.13, 77.27),
    "Panchkula": (30.69, 76.86),
    "Kurukshetra": (29.97, 76.84),
    "Sirsa": (29.53, 75.03),
    "Jind": (29.32, 76.32),
    "Bhiwani": (28.79, 76.13),
    "Rewari": (28.19, 76.62),
    "Palwal": (28.14, 77.33),
    "Kaithal": (29.80, 76.40),
    "Fatehabad": (29.51, 75.45),
    "Narnaul": (28.04, 76.11),
    "Bahadurgarh": (28.69, 76.93),
    "Thanesar": (29.97, 76.82),

    # --- Himachal Pradesh ---
    "Shimla": (31.10, 77.17),
    "Manali": (32.24, 77.19),
    "Kullu": (31.96, 77.11),
    "Dharamshala": (32.22, 76.32),
    "Mandi": (31.71, 76.93),
    "Solan": (30.91, 77.10),
    "Bilaspur (HP)": (31.34, 76.76),
    "Una": (31.47, 76.27),
    "Hamirpur (HP)": (31.68, 76.52),
    "Nahan": (30.56, 77.30),
    "Chamba": (32.56, 76.13),
    "Kangra": (32.10, 76.27),
    "Palampur": (32.11, 76.54),
    "Rampur Bushahr": (31.45, 77.63),
    "Keylong": (32.57, 77.04),
    "Kinnaur (Reckong Peo)": (31.54, 78.27),
    "Sundernagar": (31.53, 76.90),
    "Parwanoo": (30.84, 76.96),

    # --- Jharkhand ---
    "Ranchi": (23.34, 85.31),
    "Jamshedpur": (22.80, 86.20),
    "Dhanbad": (23.79, 86.43),
    "Bokaro": (23.67, 86.15),
    "Hazaribagh": (23.99, 85.36),
    "Deoghar": (24.49, 86.70),
    "Giridih": (24.19, 86.30),
    "Dumka": (24.27, 87.25),
    "Chaibasa": (22.55, 85.80),
    "Palamu (Daltonganj)": (24.03, 84.07),
    "Ramgarh": (23.63, 85.56),
    "Pakur": (24.63, 87.84),
    "Gumla": (23.04, 84.54),
    "Lohardaga": (23.44, 84.68),
    "Koderma": (24.47, 85.59),
    "Simdega": (22.62, 84.50),
    "Godda": (24.83, 87.21),
    "Sahebganj": (25.25, 87.64),
    "Chatra": (24.21, 84.87),
    "Latehar": (23.74, 84.50),
    "Khunti": (23.07, 85.28),
    "Seraikela": (22.70, 86.09),

    # --- Karnataka ---
    "Bengaluru": (12.97, 77.59),
    "Mysuru": (12.30, 76.66),
    "Mangaluru": (12.87, 74.88),
    "Hubli": (15.36, 75.12),
    "Dharwad": (15.46, 75.01),
    "Davangere": (14.47, 75.92),
    "Raichur": (16.21, 77.36),
    "Shivamogga": (13.93, 75.57),
    "Bellary (Ballari)": (15.14, 76.93),
    "Tumkur": (13.34, 77.10),
    "Bijapur (Vijayapura)": (16.83, 75.71),
    "Gulbarga (Kalaburagi)": (17.33, 76.83),
    "Belgaum (Belagavi)": (15.85, 74.50),
    "Udupi": (13.34, 74.75),
    "Hassan": (13.01, 76.10),
    "Mandya": (12.52, 76.90),
    "Chitradurga": (14.23, 76.40),
    "Chikmagalur": (13.32, 75.77),
    "Kolar": (13.14, 78.13),
    "Bidar": (17.91, 77.52),
    "Bagalkot": (16.18, 75.70),
    "Yadgir": (16.77, 77.14),
    "Haveri": (14.79, 75.40),
    "Gadag": (15.43, 75.63),
    "Ramanagara": (12.72, 77.28),
    "Chamarajanagar": (11.92, 76.94),
    "Koppal": (15.35, 76.15),
    "Kodagu (Madikeri)": (12.42, 75.74),
    "Chikkaballapur": (13.44, 77.73),

    # --- Kerala ---
    "Kochi": (9.93, 76.26),
    "Thiruvananthapuram": (8.52, 76.94),
    "Kozhikode": (11.25, 75.77),
    "Thrissur": (10.53, 76.21),
    "Kollam": (8.89, 76.60),
    "Alappuzha": (9.49, 76.34),
    "Palakkad": (10.78, 76.65),
    "Kannur": (11.87, 75.37),
    "Kottayam": (9.59, 76.52),
    "Malappuram": (11.04, 76.07),
    "Idukki": (9.85, 76.97),
    "Pathanamthitta": (9.27, 76.79),
    "Wayanad (Kalpetta)": (11.61, 76.08),
    "Kasaragod": (12.50, 75.00),
    "Munnar": (10.09, 77.06),
    "Kumarakom": (9.62, 76.43),
    "Periyar (Thekkady)": (9.60, 77.16),
    "Ashtamudi": (8.94, 76.58),

    # --- Madhya Pradesh ---
    "Bhopal": (23.26, 77.41),
    "Indore": (22.72, 75.86),
    "Jabalpur": (23.18, 79.95),
    "Ujjain": (23.18, 75.77),
    "Gwalior": (26.22, 78.18),
    "Sagar": (23.84, 78.74),
    "Rewa": (24.53, 81.30),
    "Satna": (24.58, 80.83),
    "Hoshangabad (Narmadapuram)": (22.75, 77.73),
    "Khandwa": (21.82, 76.35),
    "Dewas": (22.97, 76.05),
    "Chhindwara": (22.06, 78.94),
    "Vidisha": (23.53, 77.81),
    "Mandsaur": (24.07, 75.07),
    "Neemuch": (24.47, 74.87),
    "Mandla": (22.60, 80.38),
    "Burhanpur": (21.31, 76.23),
    "Betul": (21.91, 77.90),
    "Seoni": (22.09, 79.54),
    "Damoh": (23.84, 79.44),
    "Shivpuri": (25.43, 77.66),
    "Datia": (25.67, 78.46),
    "Khargone": (21.83, 75.62),
    "Dhar": (22.60, 75.30),
    "Balaghat": (21.81, 80.19),
    "Tikamgarh": (24.74, 78.83),
    "Panna": (24.72, 80.19),
    "Chhatarpur": (24.91, 79.59),
    "Raisen": (23.33, 77.79),
    "Shajapur": (23.43, 76.27),
    "Rajgarh": (24.00, 76.62),
    "Narsinghpur": (22.95, 79.19),
    "Katni": (23.83, 80.39),
    "Singrauli": (24.20, 82.67),
    "Barwani": (22.04, 74.90),
    "Alirajpur": (22.31, 74.36),
    "Harda": (22.34, 77.10),
    "Anuppur": (23.10, 81.69),
    "Maihar": (24.26, 80.76),
    "Orchha": (25.35, 78.64),
    "Maheshwar": (22.18, 75.59),
    "Omkareshwar": (22.24, 76.15),

    # --- Maharashtra ---
    "Mumbai": (19.08, 72.88),
    "Pune": (18.52, 73.86),
    "Nagpur": (21.15, 79.09),
    "Nashik": (19.99, 73.79),
    "Kolhapur": (16.70, 74.24),
    "Solapur": (17.68, 75.91),
    "Satara": (17.68, 74.00),
    "Sangli": (16.85, 74.57),
    "Nanded": (19.16, 77.31),
    "Thane": (19.22, 72.98),
    "Aurangabad (MH)": (19.88, 75.32),
    "Ratnagiri": (16.99, 73.30),
    "Sindhudurg (Malvan)": (16.06, 73.46),
    "Chandrapur": (19.95, 79.30),
    "Amravati": (20.93, 77.75),
    "Wardha": (20.74, 78.60),
    "Jalgaon": (21.01, 75.56),
    "Dhule": (20.90, 74.78),
    "Parbhani": (19.27, 76.78),
    "Osmanabad (Dharashiv)": (18.18, 76.04),
    "Latur": (18.40, 76.57),
    "Beed": (18.99, 75.76),
    "Ahmednagar": (19.09, 74.74),
    "Akola": (20.71, 77.00),
    "Buldhana": (20.53, 76.18),
    "Washim": (20.11, 77.13),
    "Yavatmal": (20.39, 78.12),
    "Gondia": (21.46, 80.20),
    "Bhandara": (21.17, 79.65),
    "Gadchiroli": (20.18, 80.00),
    "Hingoli": (19.72, 77.15),
    "Lonavala": (18.75, 73.41),
    "Mahabaleshwar": (17.93, 73.66),
    "Panchgani": (17.93, 73.80),
    "Bhandardara": (19.52, 73.76),
    "Mulshi": (18.55, 73.50),
    "Shirdi": (19.77, 74.48),
    "Pandharpur": (17.68, 75.33),
    "Trimbakeshwar": (19.94, 73.53),

    # --- Manipur ---
    "Imphal": (24.81, 93.94),
    "Bishnupur": (24.63, 93.78),
    "Thoubal": (24.63, 94.01),
    "Churachandpur": (24.33, 93.68),
    "Ukhrul": (25.12, 94.37),
    "Senapati": (25.27, 94.02),
    "Chandel": (24.32, 94.04),
    "Tamenglong": (24.98, 93.51),
    "Jiribam": (24.79, 93.12),
    "Moreh": (24.25, 94.30),
    "Kakching": (24.50, 94.05),
    "Moirang": (24.49, 93.77),

    # --- Meghalaya ---
    "Shillong": (25.57, 91.88),
    "Tura": (25.51, 90.22),
    "Jowai": (25.45, 92.20),
    "Nongpoh": (25.90, 91.88),
    "Nongstoin": (25.52, 91.26),
    "Williamnagar": (25.50, 90.62),
    "Cherrapunji (Sohra)": (25.30, 91.70),
    "Mawsynram": (25.30, 91.58),
    "Dawki": (25.19, 92.02),
    "Baghmara": (25.22, 90.63),
    "Resubelpara": (25.87, 90.62),
    "Mairang": (25.55, 91.56),

    # --- Mizoram ---
    "Aizawl": (23.73, 92.72),
    "Lunglei": (22.88, 92.75),
    "Champhai": (23.46, 93.33),
    "Serchhip": (23.30, 92.85),
    "Kolasib": (24.22, 92.68),
    "Lawngtlai": (22.53, 92.90),
    "Saiha": (22.49, 92.98),
    "Mamit": (23.92, 92.49),
    "Khawzawl": (23.35, 93.15),
    "Hnahthial": (22.63, 92.76),
    "Saitual": (23.79, 92.92),

    # --- Nagaland ---
    "Kohima": (25.67, 94.11),
    "Dimapur": (25.90, 93.73),
    "Mokokchung": (26.32, 94.52),
    "Tuensang": (26.27, 94.83),
    "Wokha": (26.10, 94.27),
    "Mon": (26.75, 94.92),
    "Zunheboto": (25.97, 94.52),
    "Phek": (25.67, 94.47),
    "Peren": (25.52, 93.74),
    "Kiphire": (25.88, 94.97),
    "Longleng": (26.42, 94.87),
    "Tseminyu": (25.80, 94.15),

    # --- Odisha ---
    "Bhubaneswar": (20.30, 85.82),
    "Cuttack": (20.46, 85.88),
    "Sambalpur": (21.47, 83.97),
    "Rourkela": (22.26, 84.85),
    "Balasore": (21.49, 86.93),
    "Puri": (19.81, 85.83),
    "Berhampur": (19.31, 84.79),
    "Baripada": (21.93, 86.73),
    "Angul": (20.84, 85.10),
    "Jeypore": (18.86, 82.57),
    "Jharsuguda": (21.86, 84.01),
    "Sundargarh": (22.12, 84.04),
    "Paradip": (20.32, 86.61),
    "Konark": (19.89, 86.10),
    "Bhitarkanika": (20.73, 86.87),
    "Chilika": (19.72, 85.32),
    "Hirakud": (21.52, 83.87),
    "Dhenkanal": (20.66, 85.60),
    "Kendrapara": (20.50, 86.42),
    "Koraput": (18.81, 82.71),
    "Kalahandi (Bhawanipatna)": (19.90, 83.17),
    "Balangir": (20.72, 83.49),
    "Boudh": (20.84, 84.32),
    "Nayagarh": (20.13, 85.10),
    "Rayagada": (19.17, 83.42),
    "Nabarangpur": (19.23, 82.55),
    "Malkangiri": (18.35, 81.88),
    "Subarnapur (Sonepur)": (20.83, 83.90),
    "Bargarh": (21.33, 83.62),
    "Jagatsinghpur": (20.26, 86.17),

    # --- Punjab ---
    "Amritsar": (31.63, 74.87),
    "Ludhiana": (30.90, 75.86),
    "Jalandhar": (31.33, 75.58),
    "Patiala": (30.34, 76.39),
    "Bathinda": (30.21, 74.95),
    "Hoshiarpur": (31.53, 75.91),
    "Ferozepur": (30.93, 74.61),
    "Mohali": (30.70, 76.72),
    "Pathankot": (32.27, 75.65),
    "Ropar (Rupnagar)": (30.97, 76.53),
    "Moga": (30.82, 75.17),
    "Sangrur": (30.25, 75.84),
    "Barnala": (30.38, 75.55),
    "Muktsar": (30.48, 74.52),
    "Kapurthala": (31.38, 75.38),
    "Faridkot": (30.68, 74.76),
    "Nawanshahr": (31.13, 76.12),
    "Fazilka": (30.40, 74.03),
    "Tarn Taran": (31.45, 74.93),
    "Mansa": (29.99, 75.40),
    "Gurdaspur": (32.04, 75.40),
    "Sultanpur Lodhi": (31.22, 75.19),
    "Anandpur Sahib": (31.24, 76.50),
    "Kiratpur Sahib": (31.18, 76.58),
    "Harike": (31.17, 74.94),

    # --- Rajasthan ---
    "Jaipur": (26.91, 75.79),
    "Udaipur": (24.59, 73.71),
    "Jodhpur": (26.29, 73.02),
    "Kota": (25.18, 75.86),
    "Bikaner": (28.02, 73.31),
    "Alwar": (27.56, 76.61),
    "Bharatpur": (27.22, 77.50),
    "Ajmer": (26.45, 74.64),
    "Pushkar": (26.49, 74.55),
    "Jaisalmer": (26.91, 70.92),
    "Mount Abu": (24.59, 72.71),
    "Chittorgarh": (24.88, 74.63),
    "Bundi": (25.44, 75.64),
    "Sawai Madhopur": (26.02, 76.35),
    "Tonk": (26.17, 75.79),
    "Sikar": (27.62, 75.14),
    "Nagaur": (27.20, 73.74),
    "Pali": (25.77, 73.33),
    "Barmer": (25.75, 71.39),
    "Jhalawar": (24.60, 76.17),
    "Dungarpur": (23.84, 73.71),
    "Banswara": (23.55, 74.44),
    "Pratapgarh (RJ)": (24.03, 74.78),
    "Jhunjhunu": (28.13, 75.40),
    "Churu": (28.30, 74.97),
    "Sri Ganganagar": (29.91, 73.88),
    "Hanumangarh": (29.58, 74.33),
    "Sirohi": (24.89, 72.86),
    "Baran": (25.10, 76.51),
    "Dholpur": (26.70, 77.90),
    "Karauli": (26.50, 77.02),
    "Dausa": (26.88, 76.34),
    "Bhilwara": (25.35, 74.64),
    "Rajsamand": (25.07, 73.88),

    # --- Sikkim ---
    "Gangtok": (27.33, 88.62),
    "Namchi": (27.17, 88.35),
    "Mangan": (27.51, 88.53),
    "Gyalshing (Geyzing)": (27.29, 88.26),
    "Rangpo": (27.18, 88.53),
    "Singtam": (27.24, 88.51),
    "Jorethang": (27.10, 88.32),
    "Ravangla": (27.31, 88.37),
    "Pelling": (27.30, 88.24),
    "Lachung": (27.69, 88.75),
    "Yuksom": (27.37, 88.22),
    "Tsomgo (Changu)": (27.37, 88.77),

    # --- Tamil Nadu ---
    "Chennai": (13.08, 80.27),
    "Madurai": (9.93, 78.12),
    "Coimbatore": (11.02, 76.96),
    "Tiruchirappalli": (10.79, 78.69),
    "Salem": (11.66, 78.15),
    "Erode": (11.34, 77.73),
    "Tirunelveli": (8.73, 77.70),
    "Thanjavur": (10.79, 79.14),
    "Vellore": (12.92, 79.13),
    "Dindigul": (10.37, 77.98),
    "Kanchipuram": (12.83, 79.70),
    "Cuddalore": (11.75, 79.77),
    "Nagapattinam": (10.77, 79.84),
    "Ramanathapuram": (9.37, 78.83),
    "Sivaganga": (10.14, 78.48),
    "Virudhunagar": (9.59, 77.96),
    "Theni": (10.01, 77.48),
    "Tiruvannamalai": (12.23, 79.07),
    "Villupuram": (11.94, 79.49),
    "Ariyalur": (11.14, 79.08),
    "Perambalur": (11.23, 78.88),
    "Karur": (10.96, 78.08),
    "Namakkal": (11.22, 78.17),
    "Krishnagiri": (12.53, 78.21),
    "Dharmapuri": (12.13, 78.16),
    "Nilgiris (Ooty)": (11.41, 76.69),
    "Thoothukudi (Tuticorin)": (8.76, 78.13),
    "Kanniyakumari": (8.08, 77.57),
    "Pudukkottai": (10.38, 78.82),
    "Mamallapuram": (12.62, 80.19),
    "Hogenakkal": (12.12, 77.78),
    "Mettur": (11.78, 77.80),
    "Kodaikanal": (10.24, 77.49),
    "Srirangam": (10.86, 78.69),
    "Kumbakonam": (10.96, 79.38),
    "Tiruvarur": (10.77, 79.64),
    "Chidambaram": (11.40, 79.69),
    "Mayiladuthurai": (11.10, 79.65),
    "Tenkasi": (8.96, 77.31),
    "Ranipet": (12.93, 79.33),
    "Tirupattur": (12.50, 78.57),
    "Kallakurichi": (11.74, 78.96),

    # --- Telangana ---
    "Hyderabad": (17.38, 78.47),
    "Warangal": (17.98, 79.59),
    "Karimnagar": (18.44, 79.13),
    "Nizamabad": (18.67, 78.09),
    "Khammam": (17.25, 80.15),
    "Nalgonda": (17.05, 79.27),
    "Mahbubnagar": (16.74, 77.99),
    "Adilabad": (19.67, 78.53),
    "Mancherial": (18.87, 79.44),
    "Siddipet": (18.10, 78.85),
    "Suryapet": (17.14, 79.62),
    "Medak": (18.05, 78.26),
    "Bhadrachalam": (17.67, 80.88),
    "Nagarjunasagar (TS)": (16.57, 79.24),
    "Ramagundam": (18.76, 79.47),
    "Gadwal": (16.24, 77.81),
    "Kamareddy": (18.32, 78.34),
    "Sangareddy": (17.62, 78.09),
    "Vikarabad": (17.34, 77.90),
    "Wanaparthy": (16.36, 78.06),
    "Nagarkurnool": (16.48, 78.31),
    "Jagtial": (18.79, 78.91),
    "Peddapalli": (18.62, 79.38),
    "Koratla": (18.82, 78.71),
    "Nirmal": (19.10, 78.35),
    "Bhainsa": (19.10, 77.97),
    "Medchal": (17.63, 78.48),
    "Rajanna Sircilla": (18.39, 78.83),
    "Jangaon": (17.73, 79.15),
    "Mulugu": (18.19, 79.94),
    "Mahabubabad": (17.60, 80.00),
    "Jayashankar Bhupalpally": (18.43, 79.97),

    # --- Tripura ---
    "Agartala": (23.83, 91.28),
    "Udaipur (Tripura)": (23.53, 91.49),
    "Dharmanagar": (24.37, 92.17),
    "Kailashahar": (24.33, 92.00),
    "Ambassa": (23.92, 91.85),
    "Khowai": (24.07, 91.60),
    "Belonia": (23.25, 91.45),
    "Sabroom": (23.00, 91.72),
    "Sonamura": (23.70, 91.32),
    "Kamalpur": (24.20, 91.82),
    "Bishalgarh": (23.63, 91.38),

    # --- Uttar Pradesh ---
    "Lucknow": (26.85, 80.95),
    "Varanasi": (25.32, 83.01),
    "Agra": (27.18, 78.02),
    "Kanpur": (26.45, 80.35),
    "Prayagraj": (25.43, 81.85),
    "Meerut": (28.98, 77.71),
    "Ghaziabad": (28.67, 77.42),
    "Noida": (28.54, 77.39),
    "Mathura": (27.49, 77.67),
    "Gorakhpur": (26.76, 83.37),
    "Ayodhya": (26.80, 82.20),
    "Jhansi": (25.45, 78.57),
    "Bareilly": (28.37, 79.42),
    "Aligarh": (27.88, 78.08),
    "Moradabad": (28.83, 78.78),
    "Saharanpur": (29.97, 77.54),
    "Firozabad": (27.15, 78.39),
    "Vrindavan": (27.58, 77.70),
    "Mirzapur": (25.15, 82.57),
    "Sultanpur": (26.26, 82.07),
    "Faizabad": (26.77, 82.14),
    "Rae Bareli": (26.23, 81.23),
    "Unnao": (26.55, 80.49),
    "Hardoi": (27.40, 80.13),
    "Sitapur": (27.57, 80.68),
    "Lakhimpur Kheri": (27.95, 80.78),
    "Shahjahanpur": (27.88, 79.91),
    "Budaun": (28.04, 79.12),
    "Etawah": (26.78, 79.02),
    "Mainpuri": (27.23, 79.02),
    "Fatehpur": (25.93, 80.81),
    "Hamirpur (UP)": (25.95, 80.15),
    "Banda": (25.47, 80.34),
    "Chitrakoot": (25.20, 80.90),
    "Jaunpur": (25.75, 82.68),
    "Ghazipur": (25.58, 83.58),
    "Ballia": (25.76, 84.15),
    "Azamgarh": (26.07, 83.19),
    "Basti": (26.80, 82.76),
    "Deoria": (26.50, 83.79),
    "Mau": (25.94, 83.56),
    "Kushinagar": (26.74, 83.89),
    "Sambhal": (28.59, 78.57),
    "Amroha": (28.90, 78.47),
    "Rampur": (28.81, 79.02),
    "Bijnor": (29.37, 78.14),
    "Muzaffarnagar": (29.47, 77.71),
    "Shamli": (29.45, 77.31),
    "Baghpat": (28.95, 77.22),
    "Bulandshahr": (28.41, 77.85),
    "Hathras": (27.60, 78.05),
    "Kasganj": (27.81, 78.65),
    "Etah": (27.63, 78.67),
    "Farrukhabad": (27.39, 79.58),
    "Kannauj": (27.05, 79.92),
    "Auraiya": (26.47, 79.51),
    "Pratapgarh (UP)": (25.90, 81.94),
    "Ambedkar Nagar": (26.40, 82.42),
    "Bahraich": (27.57, 81.60),
    "Shravasti": (27.50, 82.05),
    "Sonbhadra": (24.69, 83.07),
    "Chandauli": (25.26, 83.27),
    "Mahoba": (25.29, 79.87),
    "Lalitpur": (24.69, 78.42),
    "Pilibhit": (28.63, 79.81),

    # --- Uttarakhand ---
    "Dehradun": (30.32, 78.03),
    "Haridwar": (29.95, 78.16),
    "Rishikesh": (30.09, 78.27),
    "Nainital": (29.38, 79.46),
    "Mussoorie": (30.45, 78.07),
    "Almora": (29.60, 79.66),
    "Rudraprayag": (30.28, 78.98),
    "Chamoli (Gopeshwar)": (30.41, 79.32),
    "Uttarkashi": (30.73, 78.44),
    "Pithoragarh": (29.58, 80.22),
    "Champawat": (29.33, 80.09),
    "Bageshwar": (29.84, 79.77),
    "Tehri": (30.39, 78.48),
    "Pauri": (30.15, 78.78),
    "Roorkee": (29.87, 77.89),
    "Haldwani": (29.22, 79.52),
    "Kashipur": (29.21, 78.96),
    "Devprayag": (30.15, 78.60),
    "Srinagar (UK)": (30.22, 78.78),
    "Kotdwar": (29.75, 78.53),
    "Badrinath": (30.74, 79.49),
    "Kedarnath": (30.73, 79.07),
    "Gangotri": (30.99, 78.94),
    "Yamunotri": (31.01, 78.45),
    "Tanakpur": (29.07, 80.11),
    "Ramnagar": (29.39, 79.13),
    "Corbett area": (29.53, 78.77),

    # --- West Bengal ---
    "Kolkata": (22.57, 88.36),
    "Siliguri": (26.71, 88.43),
    "Darjeeling": (27.04, 88.26),
    "Howrah": (22.59, 88.26),
    "Asansol": (23.69, 86.95),
    "Durgapur": (23.55, 87.32),
    "Malda": (25.00, 88.14),
    "Haldia": (22.06, 88.06),
    "Baharampur": (24.10, 88.25),
    "Krishnanagar": (23.40, 88.50),
    "Burdwan (Bardhaman)": (23.24, 87.86),
    "Bankura": (23.23, 87.07),
    "Purulia": (23.33, 86.36),
    "Midnapore": (22.42, 87.32),
    "Sundarbans (Gosaba)": (22.17, 88.81),
    "Cooch Behar": (26.32, 89.45),
    "Jalpaiguri": (26.52, 88.73),
    "Alipurduar": (26.49, 89.52),
    "Balurghat": (25.22, 88.77),
    "Raiganj": (25.62, 88.12),
    "Diamond Harbour": (22.19, 88.19),
    "Barrackpore": (22.76, 88.37),
    "Serampore": (22.75, 88.34),
    "Chandannagar": (22.87, 88.36),
    "Nabadwip": (23.41, 88.37),
    "Shantiniketan": (23.68, 87.69),
    "Tarakeswar": (22.89, 88.02),
    "Sagar Island": (21.65, 88.06),
    "Bakkhali": (21.56, 88.25),
    "Digha": (21.63, 87.55),

    # --- Andaman & Nicobar Islands ---
    "Port Blair": (11.67, 92.74),
    "Havelock Island (Swaraj Dweep)": (11.98, 93.00),
    "Neil Island (Shaheed Dweep)": (11.83, 93.05),
    "Diglipur": (13.27, 93.00),
    "Rangat": (12.50, 92.92),
    "Mayabunder": (12.85, 92.90),
    "Car Nicobar": (9.15, 92.80),
    "Campbell Bay": (7.00, 93.93),
    "Baratang": (12.10, 92.80),

    # --- Chandigarh ---
    "Chandigarh": (30.73, 76.78),

    # --- Dadra & Nagar Haveli and Daman & Diu ---
    "Silvassa": (20.27, 73.01),
    "Daman": (20.41, 72.85),
    "Diu": (20.71, 70.98),

    # --- Delhi (NCT) ---
    "Delhi": (28.61, 77.23),
    "New Delhi": (28.61, 77.21),
    "Old Delhi": (28.66, 77.23),
    "Dwarka (Delhi)": (28.57, 77.04),
    "Okhla": (28.53, 77.27),
    "Wazirabad": (28.72, 77.23),
    "Najafgarh": (28.61, 76.98),
    "Narela": (28.85, 77.09),

    # --- Jammu & Kashmir ---
    "Srinagar": (34.08, 74.80),
    "Jammu": (32.73, 74.87),
    "Anantnag": (33.73, 75.15),
    "Baramulla": (34.20, 74.34),
    "Sopore": (34.30, 74.47),
    "Pulwama": (33.87, 74.89),
    "Kupwara": (34.53, 74.26),
    "Pahalgam": (34.01, 75.31),
    "Gulmarg": (34.05, 74.38),
    "Udhampur": (32.92, 75.14),
    "Rajouri": (33.38, 74.31),
    "Poonch": (33.77, 74.09),
    "Kathua": (32.39, 75.51),
    "Kishtwar": (33.31, 75.77),
    "Doda": (33.15, 75.55),
    "Ramban": (33.24, 75.24),
    "Reasi": (33.08, 74.83),
    "Samba": (32.55, 75.12),
    "Bandipore": (34.42, 74.65),
    "Ganderbal": (34.23, 74.78),
    "Budgam": (33.93, 74.73),
    "Shopian": (33.72, 74.83),
    "Kulgam": (33.63, 75.02),

    # --- Ladakh ---
    "Leh": (34.16, 77.58),
    "Kargil": (34.55, 76.13),
    "Nubra (Diskit)": (34.53, 77.56),
    "Pangong area": (33.76, 78.65),
    "Hanle": (32.78, 78.97),
    "Nyoma": (33.24, 78.65),
    "Zanskar (Padum)": (33.46, 76.89),
    "Tso Kar": (33.30, 78.02),
    "Drass": (34.43, 75.76),

    # --- Lakshadweep ---
    "Kavaratti": (10.57, 72.64),
    "Minicoy": (8.27, 73.05),
    "Agatti": (10.86, 72.19),
    "Andrott": (10.82, 73.69),
    "Amini": (11.12, 72.73),
    "Kadmat": (11.23, 72.78),
    "Kalpeni": (10.08, 73.65),
    "Bangaram": (10.94, 72.28),

    # --- Puducherry ---
    "Puducherry": (11.93, 79.83),
    "Karaikal": (10.92, 79.84),
    "Mahe": (11.70, 75.54),
    "Yanam": (16.73, 82.22),
}

# State capitals (for fallback coordinates)
STATE_CAPITALS = {
    "Andhra Pradesh": "Vijayawada",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Guwahati",
    "Bihar": "Patna",
    "Chhattisgarh": "Raipur",
    "Goa": "Panaji",
    "Gujarat": "Gandhinagar",
    "Haryana": "Chandigarh",
    "Himachal Pradesh": "Shimla",
    "Jharkhand": "Ranchi",
    "Karnataka": "Bengaluru",
    "Kerala": "Thiruvananthapuram",
    "Madhya Pradesh": "Bhopal",
    "Maharashtra": "Mumbai",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Odisha": "Bhubaneswar",
    "Punjab": "Chandigarh",
    "Rajasthan": "Jaipur",
    "Sikkim": "Gangtok",
    "Tamil Nadu": "Chennai",
    "Telangana": "Hyderabad",
    "Tripura": "Agartala",
    "Uttar Pradesh": "Lucknow",
    "Uttarakhand": "Dehradun",
    "West Bengal": "Kolkata",
    "Andaman & Nicobar Islands": "Port Blair",
    "Chandigarh": "Chandigarh",
    "Dadra & Nagar Haveli and Daman & Diu": "Silvassa",
    "Delhi (NCT)": "Delhi",
    "Jammu & Kashmir": "Srinagar",
    "Ladakh": "Leh",
    "Lakshadweep": "Kavaratti",
    "Puducherry": "Puducherry",
}

# Lake-type keywords
LAKE_KEYWORDS = [
    "Lake", "Reservoir", "Dam", "Sarovar", "Tal", "Taal",
    "Beel", "Sagar", "Tank", "Wetland", "Lagoon", "Beel",
    "Jheel", "Tso", "Bil", "Pond"
]


def get_city_coords(city_name, state_name):
    """Get coordinates for a city, falling back to state capital + offset."""
    # Try exact match
    if city_name in CITY_COORDS:
        return CITY_COORDS[city_name]

    # Try cleaned name (remove parenthetical)
    clean = re.sub(r'\s*\(.*?\)', '', city_name).strip()
    if clean in CITY_COORDS:
        return CITY_COORDS[clean]

    # Try just the first word
    first_word = city_name.split()[0].rstrip(',')
    if first_word in CITY_COORDS:
        return CITY_COORDS[first_word]

    # Fallback: state capital + deterministic offset
    capital = STATE_CAPITALS.get(state_name, "Delhi")
    if capital in CITY_COORDS:
        base_lat, base_lon = CITY_COORDS[capital]
    else:
        base_lat, base_lon = 20.0, 78.0  # center of India

    # Create a deterministic but varied offset from city name hash
    h = int(hashlib.md5(city_name.encode()).hexdigest(), 16)
    lat_offset = ((h % 1000) - 500) / 5000.0  # range: -0.1 to +0.1
    lon_offset = (((h >> 10) % 1000) - 500) / 5000.0
    return (round(base_lat + lat_offset, 4), round(base_lon + lon_offset, 4))


def is_lake_type(text):
    """Check if a water body name/description indicates a lake type."""
    for kw in LAKE_KEYWORDS:
        if kw.lower() in text.lower():
            return True
    return False


def parse_water_bodies(water_bodies_str, city_lat, city_lon):
    """
    Parse the waterBodies string from data.json into a list of water body dicts.

    Handles formats like:
    - "Krishna River"
    - "Tungabhadra River/Handri River"
    - "Ganga River (Deepor Beel Lake)"
    - "Near Krishna River"
    - "Krishna River (Nagarjuna Sagar Dam/Reservoir)"
    """
    entries = []
    seen_names = set()

    # Split on / but not inside parentheses
    # First, handle the main text
    text = water_bodies_str.strip()
    if not text:
        return entries

    # Split by / to get individual water bodies
    # But be careful with parenthetical content
    parts = []
    depth = 0
    current = ""
    for ch in text:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == '/' and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Extract parenthetical content as separate water bodies
        paren_matches = re.findall(r'\(([^)]+)\)', part)
        main_part = re.sub(r'\s*\([^)]*\)', '', part).strip()

        # Process main part
        if main_part:
            # Clean up prefixes
            clean_name = main_part
            for prefix in ["Near ", "near ", "Along ", "On "]:
                if clean_name.startswith(prefix):
                    clean_name = clean_name[len(prefix):]
                    break

            clean_name = clean_name.strip()
            if clean_name and clean_name.lower() not in ("coast", "near coast", ""):
                wb_type = "lake" if is_lake_type(clean_name) else "river"
                if wb_type == "river":
                    bbox = (
                        round(city_lon - 0.06, 2),
                        round(city_lat - 0.04, 2),
                        round(city_lon + 0.06, 2),
                        round(city_lat + 0.04, 2),
                    )
                else:
                    bbox = (
                        round(city_lon - 0.03, 2),
                        round(city_lat - 0.02, 2),
                        round(city_lon + 0.03, 2),
                        round(city_lat + 0.02, 2),
                    )
                name_key = clean_name.lower()
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    entries.append({
                        "name": clean_name,
                        "type": wb_type,
                        "bbox": bbox,
                    })

        # Process parenthetical content
        for paren in paren_matches:
            paren = paren.strip()
            # Could contain multiple items separated by /
            sub_parts = paren.split('/')
            for sp in sub_parts:
                sp = sp.strip()
                if not sp or sp.lower() in ("seasonal", "barrage", "lower"):
                    continue
                # Clean
                for prefix in ["Near ", "near "]:
                    if sp.startswith(prefix):
                        sp = sp[len(prefix):]
                        break
                sp = sp.strip()
                if sp and sp.lower() not in ("seasonal", "barrage", "lower", ""):
                    wb_type = "lake" if is_lake_type(sp) else "river"
                    if wb_type == "river":
                        bbox = (
                            round(city_lon - 0.06, 2),
                            round(city_lat - 0.04, 2),
                            round(city_lon + 0.06, 2),
                            round(city_lat + 0.04, 2),
                        )
                    else:
                        bbox = (
                            round(city_lon - 0.03, 2),
                            round(city_lat - 0.02, 2),
                            round(city_lon + 0.03, 2),
                            round(city_lat + 0.02, 2),
                        )
                    name_key = sp.lower()
                    if name_key not in seen_names:
                        seen_names.add(name_key)
                        entries.append({
                            "name": sp,
                            "type": wb_type,
                            "bbox": bbox,
                        })

    return entries


def generate_geo_hierarchy():
    """Generate the complete geo_hierarchy.py file."""

    # Load data.json
    data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "india-rivers-lakes", "server", "data.json"
    )
    if not os.path.exists(data_path):
        # Try alternate path
        data_path = "c:/Users/adhit/Downloads/files (2)/india-rivers-lakes/server/data.json"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build the database dict
    database = {}
    for state_obj in data:
        state_name = state_obj["name"]
        cities_dict = {}
        for city_obj in state_obj.get("cities", []):
            city_name = city_obj["name"]
            water_bodies_str = city_obj.get("waterBodies", "")
            lat, lon = get_city_coords(city_name, state_name)
            water_bodies = parse_water_bodies(water_bodies_str, lat, lon)
            if water_bodies:
                cities_dict[city_name] = water_bodies
            else:
                # If parsing yielded nothing, create a generic entry from the text
                clean_text = water_bodies_str.strip()
                if clean_text:
                    for prefix in ["Near ", "near "]:
                        if clean_text.startswith(prefix):
                            clean_text = clean_text[len(prefix):]
                            break
                    wb_type = "lake" if is_lake_type(clean_text) else "river"
                    if wb_type == "river":
                        bbox = (
                            round(lon - 0.06, 2),
                            round(lat - 0.04, 2),
                            round(lon + 0.06, 2),
                            round(lat + 0.04, 2),
                        )
                    else:
                        bbox = (
                            round(lon - 0.03, 2),
                            round(lat - 0.02, 2),
                            round(lon + 0.03, 2),
                            round(lat + 0.02, 2),
                        )
                    cities_dict[city_name] = [{
                        "name": clean_text,
                        "type": wb_type,
                        "bbox": bbox,
                    }]

        database[state_name] = cities_dict

    # Now generate the Python file
    lines = []
    lines.append('"""')
    lines.append("Aqua-Sentinel AI - Module A: Hierarchical Spatial Navigation System")
    lines.append("")
    lines.append("This module provides a comprehensive geographic hierarchy database for India's")
    lines.append("water bodies, enabling structured spatial navigation from State -> City -> Water Body.")
    lines.append("It serves as the foundational geographic reference for the Aqua-Sentinel AI project's")
    lines.append("water quality monitoring and analysis pipeline.")
    lines.append("")
    lines.append("Covers all 36 Indian States and Union Territories with water bodies")
    lines.append("across 993 cities.")
    lines.append("")
    lines.append("Usage:")
    lines.append("    from geo_hierarchy import (")
    lines.append("        get_states, get_cities, get_water_bodies, get_roi,")
    lines.append("        search_water_body, get_nearest_location")
    lines.append("    )")
    lines.append('"""')
    lines.append("")
    lines.append("import math")
    lines.append("")
    lines.append("# =============================================================================")
    lines.append("# INDIA GEO DATABASE")
    lines.append("# =============================================================================")
    lines.append("# Hierarchical structure:")
    lines.append("#   State/UT -> City -> [Water Bodies]")
    lines.append("#")
    lines.append("# Each water body entry contains:")
    lines.append("#   - name: Common name of the water body")
    lines.append('#   - type: "river" or "lake"')
    lines.append("#   - bbox: (lon_min, lat_min, lon_max, lat_max) bounding box coordinates")
    lines.append("# =============================================================================")
    lines.append("")
    lines.append("INDIA_GEO_DATABASE = {")
    lines.append("")

    # Separate states and UTs
    states_list = [s for s in data if s.get("type") == "state"]
    uts_list = [s for s in data if s.get("type") != "state"]

    idx = 0
    # States
    lines.append("    # =========================================================================")
    lines.append(f"    # {len(states_list)} STATES")
    lines.append("    # =========================================================================")
    lines.append("")

    for state_obj in states_list:
        idx += 1
        state_name = state_obj["name"]
        lines.append("    # -------------------------------------------------------------------------")
        lines.append(f"    # {idx}. {state_name.upper()}")
        lines.append("    # -------------------------------------------------------------------------")
        lines.append(f'    "{state_name}": {{')

        cities_dict = database.get(state_name, {})
        city_items = list(cities_dict.items())
        for ci, (city_name, water_bodies) in enumerate(city_items):
            lines.append(f'        "{city_name}": [')
            for wi, wb in enumerate(water_bodies):
                bbox_str = f"({wb['bbox'][0]}, {wb['bbox'][1]}, {wb['bbox'][2]}, {wb['bbox'][3]})"
                comma = "," if wi < len(water_bodies) - 1 else ","
                lines.append(f'            {{"name": "{wb["name"]}", "type": "{wb["type"]}", "bbox": {bbox_str}}},')
            lines.append("        ],")

        lines.append("    },")
        lines.append("")

    # UTs
    if uts_list:
        lines.append("    # =========================================================================")
        lines.append(f"    # {len(uts_list)} UNION TERRITORIES")
        lines.append("    # =========================================================================")
        lines.append("")

        for state_obj in uts_list:
            idx += 1
            state_name = state_obj["name"]
            lines.append("    # -------------------------------------------------------------------------")
            lines.append(f"    # {idx}. {state_name.upper()}")
            lines.append("    # -------------------------------------------------------------------------")
            lines.append(f'    "{state_name}": {{')

            cities_dict = database.get(state_name, {})
            city_items = list(cities_dict.items())
            for ci, (city_name, water_bodies) in enumerate(city_items):
                lines.append(f'        "{city_name}": [')
                for wi, wb in enumerate(water_bodies):
                    bbox_str = f"({wb['bbox'][0]}, {wb['bbox'][1]}, {wb['bbox'][2]}, {wb['bbox'][3]})"
                    lines.append(f'            {{"name": "{wb["name"]}", "type": "{wb["type"]}", "bbox": {bbox_str}}},')
                lines.append("        ],")

            lines.append("    },")
            lines.append("")

    lines.append("}")
    lines.append("")
    lines.append("")

    # Now add ALL the helper functions - copied exactly from the original
    lines.append("# =============================================================================")
    lines.append("# NAVIGATION FUNCTIONS")
    lines.append("# =============================================================================")
    lines.append("")
    lines.append("def get_states():")
    lines.append('    """')
    lines.append("    Return a sorted list of all state/UT names in the geo database.")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        list[str]: Alphabetically sorted list of Indian state/UT names.")
    lines.append('    """')
    lines.append("    return sorted(INDIA_GEO_DATABASE.keys())")
    lines.append("")
    lines.append("")
    lines.append("def get_cities(state):")
    lines.append('    """')
    lines.append("    Return a sorted list of city names within a given state/UT.")
    lines.append("")
    lines.append("    Args:")
    lines.append("        state (str): Name of the Indian state or Union Territory.")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        list[str]: Alphabetically sorted list of city names.")
    lines.append("")
    lines.append("    Raises:")
    lines.append("        KeyError: If the state is not found in the database.")
    lines.append('    """')
    lines.append("    if state not in INDIA_GEO_DATABASE:")
    lines.append("        raise KeyError(")
    lines.append("            f\"State '{state}' not found in database. \"")
    lines.append("            f\"Available states: {', '.join(get_states())}\"")
    lines.append("        )")
    lines.append("    return sorted(INDIA_GEO_DATABASE[state].keys())")
    lines.append("")
    lines.append("")
    lines.append("def get_water_bodies(state, city):")
    lines.append('    """')
    lines.append("    Return a list of water body records for a given state and city.")
    lines.append("")
    lines.append("    Each record is a dict with keys: name, type, bbox.")
    lines.append("")
    lines.append("    Args:")
    lines.append("        state (str): Name of the Indian state or Union Territory.")
    lines.append("        city (str): Name of the city within that state.")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        list[dict]: List of water body dictionaries, each containing:")
    lines.append('            - name (str): Name of the water body')
    lines.append('            - type (str): "river" or "lake"')
    lines.append("            - bbox (tuple): (lon_min, lat_min, lon_max, lat_max)")
    lines.append("")
    lines.append("    Raises:")
    lines.append("        KeyError: If the state or city is not found in the database.")
    lines.append('    """')
    lines.append("    if state not in INDIA_GEO_DATABASE:")
    lines.append("        raise KeyError(")
    lines.append("            f\"State '{state}' not found in database. \"")
    lines.append("            f\"Available states: {', '.join(get_states())}\"")
    lines.append("        )")
    lines.append("    cities = INDIA_GEO_DATABASE[state]")
    lines.append("    if city not in cities:")
    lines.append("        raise KeyError(")
    lines.append("            f\"City '{city}' not found in state '{state}'. \"")
    lines.append("            f\"Available cities: {', '.join(sorted(cities.keys()))}\"")
    lines.append("        )")
    lines.append("    return list(cities[city])")
    lines.append("")
    lines.append("")
    lines.append("def get_roi(state, city, water_body_name):")
    lines.append('    """')
    lines.append("    Build and return a Region-of-Interest dictionary compatible with the")
    lines.append("    Aqua-Sentinel AI config.py ROI format.")
    lines.append("")
    lines.append("    Args:")
    lines.append("        state (str): Name of the Indian state or Union Territory.")
    lines.append("        city (str): Name of the city within that state.")
    lines.append("        water_body_name (str): Exact name of the water body.")
    lines.append("")
    lines.append("    Returns:")
    lines.append('        dict: ROI dictionary with keys:')
    lines.append('            - name (str): Composite label "<water_body>, <city>"')
    lines.append("            - state (str): State name")
    lines.append("            - city (str): City name")
    lines.append("            - water_body (str): Water body name")
    lines.append('            - water_type (str): "river" or "lake"')
    lines.append("            - lon_min (float): Western longitude boundary")
    lines.append("            - lat_min (float): Southern latitude boundary")
    lines.append("            - lon_max (float): Eastern longitude boundary")
    lines.append("            - lat_max (float): Northern latitude boundary")
    lines.append("")
    lines.append("    Raises:")
    lines.append("        KeyError: If the state, city, or water body is not found.")
    lines.append('    """')
    lines.append("    water_bodies = get_water_bodies(state, city)")
    lines.append("    for wb in water_bodies:")
    lines.append('        if wb["name"] == water_body_name:')
    lines.append('            lon_min, lat_min, lon_max, lat_max = wb["bbox"]')
    lines.append("            return {")
    lines.append('                "name": f"{water_body_name}, {city}",')
    lines.append('                "state": state,')
    lines.append('                "city": city,')
    lines.append('                "water_body": water_body_name,')
    lines.append('                "water_type": wb["type"],')
    lines.append('                "lon_min": lon_min,')
    lines.append('                "lat_min": lat_min,')
    lines.append('                "lon_max": lon_max,')
    lines.append('                "lat_max": lat_max,')
    lines.append("            }")
    lines.append('    available = [wb["name"] for wb in water_bodies]')
    lines.append("    raise KeyError(")
    lines.append("        f\"Water body '{water_body_name}' not found in {city}, {state}. \"")
    lines.append("        f\"Available water bodies: {', '.join(available)}\"")
    lines.append("    )")
    lines.append("")
    lines.append("")
    lines.append("def search_water_body(query):")
    lines.append('    """')
    lines.append("    Perform a fuzzy (case-insensitive substring) search across all water bodies")
    lines.append("    in the database.")
    lines.append("")
    lines.append("    Args:")
    lines.append("        query (str): Search string to match against water body names.")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        list[dict]: List of matching results, each containing:")
    lines.append("            - name (str): Water body name")
    lines.append('            - type (str): "river" or "lake"')
    lines.append("            - city (str): City where the water body is located")
    lines.append("            - state (str): State where the city is located")
    lines.append("            - bbox (tuple): Bounding box coordinates")
    lines.append("")
    lines.append("        Results are sorted alphabetically by water body name.")
    lines.append('    """')
    lines.append("    query_lower = query.lower().strip()")
    lines.append("    if not query_lower:")
    lines.append("        return []")
    lines.append("")
    lines.append("    matches = []")
    lines.append("    for state, cities in INDIA_GEO_DATABASE.items():")
    lines.append("        for city, water_bodies in cities.items():")
    lines.append("            for wb in water_bodies:")
    lines.append('                if query_lower in wb["name"].lower():')
    lines.append("                    matches.append({")
    lines.append('                        "name": wb["name"],')
    lines.append('                        "type": wb["type"],')
    lines.append('                        "city": city,')
    lines.append('                        "state": state,')
    lines.append('                        "bbox": wb["bbox"],')
    lines.append("                    })")
    lines.append("")
    lines.append('    matches.sort(key=lambda m: m["name"])')
    lines.append("    return matches")
    lines.append("")
    lines.append("")
    lines.append("def get_nearest_location(lat, lon):")
    lines.append('    """')
    lines.append("    Find the nearest known water body to a given latitude/longitude coordinate")
    lines.append("    using the Haversine formula for great-circle distance.")
    lines.append("")
    lines.append("    Loops through every water body in the database, computes the distance from")
    lines.append("    (lat, lon) to the centre of each water body's bounding box, and returns the")
    lines.append("    closest match.")
    lines.append("")
    lines.append("    Args:")
    lines.append("        lat (float): Latitude in decimal degrees (e.g. 28.61 for Delhi).")
    lines.append("        lon (float): Longitude in decimal degrees (e.g. 77.23 for Delhi).")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        dict: Dictionary with keys:")
    lines.append("            - state (str): State/UT name")
    lines.append("            - city (str): City name")
    lines.append("            - water_body (str): Name of the nearest water body")
    lines.append('            - water_type (str): "river" or "lake"')
    lines.append("            - distance_km (float): Distance in kilometres (rounded to 2 dp)")
    lines.append('            - locality_name (str): Formatted string')
    lines.append('              "Near <water_body>, <city>, <state>"')
    lines.append("")
    lines.append("        Returns None if the database is empty.")
    lines.append('    """')
    lines.append("")
    lines.append("    def _haversine(lat1, lon1, lat2, lon2):")
    lines.append('        """Return distance in km between two points on Earth."""')
    lines.append("        R = 6371.0  # Earth radius in kilometres")
    lines.append("        dlat = math.radians(lat2 - lat1)")
    lines.append("        dlon = math.radians(lon2 - lon1)")
    lines.append("        a = (")
    lines.append("            math.sin(dlat / 2.0) ** 2")
    lines.append("            + math.cos(math.radians(lat1))")
    lines.append("            * math.cos(math.radians(lat2))")
    lines.append("            * math.sin(dlon / 2.0) ** 2")
    lines.append("        )")
    lines.append("        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))")
    lines.append("        return R * c")
    lines.append("")
    lines.append("    best = None")
    lines.append('    best_dist = float("inf")')
    lines.append("")
    lines.append("    for state, cities in INDIA_GEO_DATABASE.items():")
    lines.append("        for city, water_bodies in cities.items():")
    lines.append("            for wb in water_bodies:")
    lines.append('                lon_min, lat_min, lon_max, lat_max = wb["bbox"]')
    lines.append("                centre_lat = (lat_min + lat_max) / 2.0")
    lines.append("                centre_lon = (lon_min + lon_max) / 2.0")
    lines.append("                dist = _haversine(lat, lon, centre_lat, centre_lon)")
    lines.append("                if dist < best_dist:")
    lines.append("                    best_dist = dist")
    lines.append("                    best = {")
    lines.append('                        "state": state,')
    lines.append('                        "city": city,')
    lines.append('                        "water_body": wb["name"],')
    lines.append('                        "water_type": wb["type"],')
    lines.append('                        "distance_km": round(dist, 2),')
    lines.append("                        \"locality_name\": f\"Near {wb['name']}, {city}, {state}\",")
    lines.append("                    }")
    lines.append("")
    lines.append("    return best")
    lines.append("")
    lines.append("")
    lines.append("# =============================================================================")
    lines.append("# UTILITY / SUMMARY FUNCTIONS")
    lines.append("# =============================================================================")
    lines.append("")
    lines.append("def summary():")
    lines.append('    """')
    lines.append("    Print a human-readable summary of the entire geo database.")
    lines.append("")
    lines.append("    Returns:")
    lines.append("        str: Formatted multi-line summary string.")
    lines.append('    """')
    lines.append("    lines = []")
    lines.append('    lines.append("=" * 70)')
    lines.append('    lines.append("  Aqua-Sentinel AI - Geographic Hierarchy Summary")')
    lines.append('    lines.append("=" * 70)')
    lines.append("")
    lines.append("    total_states = 0")
    lines.append("    total_cities = 0")
    lines.append("    total_water_bodies = 0")
    lines.append("")
    lines.append("    for state in sorted(INDIA_GEO_DATABASE.keys()):")
    lines.append("        cities = INDIA_GEO_DATABASE[state]")
    lines.append("        total_states += 1")
    lines.append('        lines.append(f"\\n  {state}")')
    lines.append('        lines.append("  " + "-" * (len(state)))')
    lines.append("        for city in sorted(cities.keys()):")
    lines.append("            total_cities += 1")
    lines.append("            water_bodies = cities[city]")
    lines.append('            wb_names = ", ".join(wb["name"] for wb in water_bodies)')
    lines.append("            total_water_bodies += len(water_bodies)")
    lines.append('            lines.append(f"    {city}: {wb_names}")')
    lines.append("")
    lines.append('    lines.append("\\n" + "=" * 70)')
    lines.append("    lines.append(")
    lines.append('        f"  Total: {total_states} states/UTs, {total_cities} cities, "')
    lines.append('        f"{total_water_bodies} water bodies"')
    lines.append("    )")
    lines.append('    lines.append("=" * 70)')
    lines.append("")
    lines.append('    output = "\\n".join(lines)')
    lines.append("    return output")
    lines.append("")
    lines.append("")
    lines.append("# =============================================================================")
    lines.append("# MODULE SELF-TEST")
    lines.append("# =============================================================================")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    print(summary())")
    lines.append("    print()")
    lines.append("")
    lines.append("    # Demonstrate core navigation functions")
    lines.append('    print("--- States/UTs ---")')
    lines.append("    for s in get_states():")
    lines.append('        print(f"  {s}")')
    lines.append("")
    lines.append('    print(f"\\n--- Total states/UTs: {len(get_states())} ---")')
    lines.append("")
    lines.append('    print("\\n--- Cities in Maharashtra ---")')
    lines.append('    for c in get_cities("Maharashtra"):')
    lines.append('        print(f"  {c}")')
    lines.append("")
    lines.append('    print("\\n--- Water Bodies in Mumbai, Maharashtra ---")')
    lines.append('    for wb in get_water_bodies("Maharashtra", "Mumbai"):')
    lines.append("        print(f\"  {wb['name']} ({wb['type']}) -> bbox: {wb['bbox']}\")")
    lines.append("")
    lines.append('    print("\\n--- Search: \'yamuna\' ---")')
    lines.append('    results = search_water_body("yamuna")')
    lines.append("    for r in results:")
    lines.append("        print(f\"  {r['name']} in {r['city']}, {r['state']} ({r['type']})\")")
    lines.append("")
    lines.append('    print("\\n--- Search: \'lake\' ---")')
    lines.append('    results = search_water_body("lake")')
    lines.append("    for r in results:")
    lines.append("        print(f\"  {r['name']} in {r['city']}, {r['state']} ({r['type']})\")")
    lines.append("")
    lines.append('    print("\\n--- Nearest location to (28.61, 77.23) [Delhi area] ---")')
    lines.append("    nearest = get_nearest_location(28.61, 77.23)")
    lines.append("    if nearest:")
    lines.append("        for k, v in nearest.items():")
    lines.append('            print(f"  {k}: {v}")')
    lines.append("")
    lines.append('    print("\\n--- Nearest location to (19.07, 72.87) [Mumbai area] ---")')
    lines.append("    nearest = get_nearest_location(19.07, 72.87)")
    lines.append("    if nearest:")
    lines.append("        for k, v in nearest.items():")
    lines.append('            print(f"  {k}: {v}")')
    lines.append("")
    lines.append('    print("\\n--- Nearest location to (34.08, 74.80) [Srinagar area] ---")')
    lines.append("    nearest = get_nearest_location(34.08, 74.80)")
    lines.append("    if nearest:")
    lines.append("        for k, v in nearest.items():")
    lines.append('            print(f"  {k}: {v}")')
    lines.append("")

    # Write the file
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "geo_hierarchy.py"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {output_path}")
    print(f"  States/UTs: {len(database)}")
    total_cities = sum(len(cities) for cities in database.values())
    total_wb = sum(
        len(wbs) for cities in database.values() for wbs in cities.values()
    )
    print(f"  Cities: {total_cities}")
    print(f"  Water bodies: {total_wb}")


if __name__ == "__main__":
    generate_geo_hierarchy()
