"""
Aqua-Sentinel AI - Module A: Hierarchical Spatial Navigation System

This module provides a comprehensive geographic hierarchy database for India's
water bodies, enabling structured spatial navigation from State -> City -> Water Body.
It serves as the foundational geographic reference for the Aqua-Sentinel AI project's
water quality monitoring and analysis pipeline.

Covers all 36 Indian States and Union Territories with water bodies
across 993 cities.

Usage:
    from geo_hierarchy import (
        get_states, get_cities, get_water_bodies, get_roi,
        search_water_body, get_nearest_location
    )
"""

import math

# =============================================================================
# INDIA GEO DATABASE
# =============================================================================
# Hierarchical structure:
#   State/UT -> City -> [Water Bodies]
#
# Each water body entry contains:
#   - name: Common name of the water body
#   - type: "river" or "lake"
#   - bbox: (lon_min, lat_min, lon_max, lat_max) bounding box coordinates
# =============================================================================

INDIA_GEO_DATABASE = {

    # =========================================================================
    # 28 STATES
    # =========================================================================

    # -------------------------------------------------------------------------
    # 1. ANDHRA PRADESH
    # -------------------------------------------------------------------------
    "Andhra Pradesh": {
        "Vijayawada": [
            {"name": "Krishna River", "type": "river", "bbox": (80.57, 16.47, 80.69, 16.55)},
        ],
        "Rajahmundry (Rajamahendravaram)": [
            {"name": "Godavari River", "type": "river", "bbox": (81.72, 16.96, 81.84, 17.04)},
        ],
        "Amaravati": [
            {"name": "Krishna River", "type": "river", "bbox": (80.3, 16.53, 80.42, 16.61)},
        ],
        "Guntur": [
            {"name": "Krishna River", "type": "river", "bbox": (80.38, 16.26, 80.5, 16.34)},
        ],
        "Kurnool": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.98, 15.79, 78.1, 15.87)},
            {"name": "Handri River", "type": "river", "bbox": (77.98, 15.79, 78.1, 15.87)},
        ],
        "Nellore": [
            {"name": "Pennar River", "type": "river", "bbox": (79.91, 14.4, 80.03, 14.48)},
        ],
        "Tirupati": [
            {"name": "Swarnamukhi River", "type": "river", "bbox": (79.36, 13.59, 79.48, 13.67)},
        ],
        "Srisailam": [
            {"name": "Krishna River", "type": "river", "bbox": (78.81, 15.81, 78.93, 15.89)},
        ],
        "Kakinada": [
            {"name": "Godavari Delta", "type": "river", "bbox": (82.18, 16.9, 82.3, 16.98)},
        ],
        "Eluru": [
            {"name": "Tammileru River", "type": "river", "bbox": (81.04, 16.67, 81.16, 16.75)},
            {"name": "Kolleru Lake", "type": "lake", "bbox": (81.07, 16.69, 81.13, 16.73)},
        ],
        "Bhimavaram": [
            {"name": "Godavari", "type": "river", "bbox": (81.46, 16.5, 81.58, 16.58)},
            {"name": "Kolleru Lake nearby", "type": "lake", "bbox": (81.49, 16.52, 81.55, 16.56)},
        ],
        "Amalapuram": [
            {"name": "Godavari Delta", "type": "river", "bbox": (81.94, 16.54, 82.06, 16.62)},
        ],
        "Machilipatnam": [
            {"name": "Krishna Delta", "type": "river", "bbox": (81.08, 16.15, 81.2, 16.23)},
        ],
        "Ongole": [
            {"name": "Gundlakamma River", "type": "river", "bbox": (79.99, 15.46, 80.11, 15.54)},
        ],
        "Kadapa (Cuddapah)": [
            {"name": "Pennar River", "type": "river", "bbox": (78.76, 14.43, 78.88, 14.51)},
            {"name": "Cheyyeru River", "type": "river", "bbox": (78.76, 14.43, 78.88, 14.51)},
            {"name": "Papagni River", "type": "river", "bbox": (78.76, 14.43, 78.88, 14.51)},
        ],
        "Anantapur": [
            {"name": "Chitravatha River", "type": "river", "bbox": (77.54, 14.64, 77.66, 14.72)},
            {"name": "Handri River", "type": "river", "bbox": (77.54, 14.64, 77.66, 14.72)},
        ],
        "Nandyal": [
            {"name": "Kundu River", "type": "river", "bbox": (78.42, 15.44, 78.54, 15.52)},
        ],
        "Proddutur": [
            {"name": "Pennar River", "type": "river", "bbox": (78.49, 14.71, 78.61, 14.79)},
        ],
        "Tadepalligudem": [
            {"name": "Godavari", "type": "river", "bbox": (81.47, 16.77, 81.59, 16.85)},
        ],
        "Tenali": [
            {"name": "Krishna", "type": "river", "bbox": (80.58, 16.2, 80.7, 16.28)},
        ],
        "Narasaraopet": [
            {"name": "Krishna basin", "type": "river", "bbox": (79.99, 16.2, 80.11, 16.28)},
        ],
        "Bapatla": [
            {"name": "Krishna delta", "type": "river", "bbox": (80.41, 15.86, 80.53, 15.94)},
        ],
        "Srikakulam": [
            {"name": "Nagavali River", "type": "river", "bbox": (83.84, 18.26, 83.96, 18.34)},
        ],
        "Vizianagaram": [
            {"name": "Champavathi River", "type": "river", "bbox": (83.36, 18.08, 83.48, 18.16)},
        ],
        "Hindupur": [
            {"name": "Pennar tributaries", "type": "river", "bbox": (77.43, 13.79, 77.55, 13.87)},
        ],
        "Dharmavaram": [
            {"name": "Pennar basin", "type": "river", "bbox": (77.66, 14.37, 77.78, 14.45)},
        ],
        "Adoni": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.21, 15.59, 77.33, 15.67)},
        ],
        "Mantralayam": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.32, 15.63, 77.44, 15.71)},
        ],
        "Alampur": [
            {"name": "Tungabhadra-Krishna confluence", "type": "river", "bbox": (78.07, 15.84, 78.19, 15.92)},
        ],
        "Nagarjuna Sagar": [
            {"name": "Krishna River", "type": "river", "bbox": (79.25, 16.53, 79.37, 16.61)},
            {"name": "Nagarjuna Sagar Dam", "type": "lake", "bbox": (79.28, 16.55, 79.34, 16.59)},
            {"name": "Reservoir", "type": "lake", "bbox": (79.28, 16.55, 79.34, 16.59)},
        ],
        "Dowleswaram": [
            {"name": "Godavari River", "type": "river", "bbox": (81.72, 16.91, 81.84, 16.99)},
        ],
        "Palakollu": [
            {"name": "Godavari", "type": "river", "bbox": (81.67, 16.49, 81.79, 16.57)},
        ],
        "Kovvur": [
            {"name": "Godavari River", "type": "river", "bbox": (81.67, 16.97, 81.79, 17.05)},
        ],
        "Rajam": [
            {"name": "Nagavali", "type": "river", "bbox": (83.58, 18.41, 83.7, 18.49)},
        ],
        "Palasa": [
            {"name": "Mahendratanaya River", "type": "river", "bbox": (84.36, 18.73, 84.48, 18.81)},
        ],
    },

    # -------------------------------------------------------------------------
    # 2. ARUNACHAL PRADESH
    # -------------------------------------------------------------------------
    "Arunachal Pradesh": {
        "Itanagar": [
            {"name": "Dikrong River", "type": "river", "bbox": (93.56, 27.04, 93.68, 27.12)},
            {"name": "Pachin River", "type": "river", "bbox": (93.56, 27.04, 93.68, 27.12)},
        ],
        "Pasighat": [
            {"name": "Siang River", "type": "river", "bbox": (95.27, 28.03, 95.39, 28.11)},
        ],
        "Tezu": [
            {"name": "Lohit River", "type": "river", "bbox": (96.11, 27.88, 96.23, 27.96)},
        ],
        "Along (Aalo)": [
            {"name": "Siyom River", "type": "river", "bbox": (94.74, 28.13, 94.86, 28.21)},
        ],
        "Ziro": [
            {"name": "Subansiri basin", "type": "river", "bbox": (93.77, 27.5, 93.89, 27.58)},
        ],
        "Bomdila": [
            {"name": "Kameng River area", "type": "river", "bbox": (92.36, 27.22, 92.48, 27.3)},
        ],
        "Tawang": [
            {"name": "Tawang Chu River", "type": "river", "bbox": (91.81, 27.55, 91.93, 27.63)},
        ],
        "Roing": [
            {"name": "Dibang River", "type": "river", "bbox": (95.78, 28.1, 95.9, 28.18)},
        ],
        "Changlang": [
            {"name": "Noa-Dihing River area", "type": "river", "bbox": (95.67, 27.09, 95.79, 27.17)},
        ],
        "Namsai": [
            {"name": "Noa-Dihing River", "type": "river", "bbox": (95.81, 27.65, 95.93, 27.73)},
        ],
        "Daporijo": [
            {"name": "Subansiri River", "type": "river", "bbox": (94.16, 27.95, 94.28, 28.03)},
        ],
        "Khonsa": [
            {"name": "Tirap River", "type": "river", "bbox": (95.44, 26.98, 95.56, 27.06)},
        ],
        "Yingkiong": [
            {"name": "Siang River", "type": "river", "bbox": (94.96, 28.59, 95.08, 28.67)},
        ],
        "Anini": [
            {"name": "Dibang River", "type": "river", "bbox": (95.81, 28.76, 95.93, 28.84)},
        ],
        "Seppa": [
            {"name": "Kameng River", "type": "river", "bbox": (92.91, 27.29, 93.03, 27.37)},
        ],
        "Basar": [
            {"name": "Siyom tributary", "type": "river", "bbox": (94.63, 27.95, 94.75, 28.03)},
        ],
        "Koloriang": [
            {"name": "Subansiri basin", "type": "river", "bbox": (93.52, 27.86, 93.64, 27.94)},
        ],
        "Naharlagun": [
            {"name": "Dikrong River", "type": "river", "bbox": (93.64, 27.06, 93.76, 27.14)},
        ],
        "Miao": [
            {"name": "Noa-Dihing River", "type": "river", "bbox": (96.21, 27.44, 96.33, 27.52)},
        ],
    },

    # -------------------------------------------------------------------------
    # 3. ASSAM
    # -------------------------------------------------------------------------
    "Assam": {
        "Guwahati": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (91.68, 26.1, 91.8, 26.18)},
            {"name": "Deepor Beel Lake", "type": "lake", "bbox": (91.71, 26.12, 91.77, 26.16)},
        ],
        "Dibrugarh": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (94.85, 27.43, 94.97, 27.51)},
        ],
        "Tezpur": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (92.74, 26.59, 92.86, 26.67)},
            {"name": "Jia Bharali confluence", "type": "river", "bbox": (92.74, 26.59, 92.86, 26.67)},
        ],
        "Jorhat": [
            {"name": "Brahmaputra", "type": "river", "bbox": (94.16, 26.72, 94.28, 26.8)},
            {"name": "Bhogdoi River", "type": "river", "bbox": (94.16, 26.72, 94.28, 26.8)},
        ],
        "Silchar": [
            {"name": "Barak River", "type": "river", "bbox": (92.74, 24.78, 92.86, 24.86)},
        ],
        "Nagaon": [
            {"name": "Kolong River", "type": "river", "bbox": (92.62, 26.31, 92.74, 26.39)},
            {"name": "Kopili River", "type": "river", "bbox": (92.62, 26.31, 92.74, 26.39)},
        ],
        "Tinsukia": [
            {"name": "Dibru River", "type": "river", "bbox": (95.3, 27.45, 95.42, 27.53)},
            {"name": "Brahmaputra", "type": "river", "bbox": (95.3, 27.45, 95.42, 27.53)},
        ],
        "Goalpara": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (90.57, 26.13, 90.69, 26.21)},
        ],
        "Dhubri": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (89.92, 25.98, 90.04, 26.06)},
        ],
        "Bongaigaon": [
            {"name": "Manas River area", "type": "river", "bbox": (90.5, 26.44, 90.62, 26.52)},
        ],
        "Karimganj": [
            {"name": "Kushiyara River", "type": "river", "bbox": (92.29, 24.83, 92.41, 24.91)},
        ],
        "Sivasagar": [
            {"name": "Dikhow River", "type": "river", "bbox": (94.58, 26.94, 94.7, 27.02)},
            {"name": "Joysagar Lake", "type": "lake", "bbox": (94.61, 26.96, 94.67, 27.0)},
            {"name": "Sibsagar Tank", "type": "lake", "bbox": (94.61, 26.96, 94.67, 27.0)},
        ],
        "North Lakhimpur": [
            {"name": "Subansiri River", "type": "river", "bbox": (94.04, 27.2, 94.16, 27.28)},
        ],
        "Barpeta": [
            {"name": "Manas River", "type": "river", "bbox": (90.94, 26.28, 91.06, 26.36)},
            {"name": "Beki River", "type": "river", "bbox": (90.94, 26.28, 91.06, 26.36)},
        ],
        "Nalbari": [
            {"name": "Pagladia River", "type": "river", "bbox": (91.38, 26.4, 91.5, 26.48)},
            {"name": "Nona River", "type": "river", "bbox": (91.38, 26.4, 91.5, 26.48)},
        ],
        "Kokrajhar": [
            {"name": "Manas", "type": "river", "bbox": (90.21, 26.36, 90.33, 26.44)},
            {"name": "Gaurang River", "type": "river", "bbox": (90.21, 26.36, 90.33, 26.44)},
        ],
        "Haflong": [
            {"name": "Jatinga River", "type": "river", "bbox": (92.96, 25.13, 93.08, 25.21)},
        ],
        "Diphu": [
            {"name": "Kopili", "type": "river", "bbox": (93.37, 25.8, 93.49, 25.88)},
        ],
        "Hailakandi": [
            {"name": "Barak area", "type": "river", "bbox": (92.51, 24.64, 92.63, 24.72)},
        ],
        "Mangaldoi": [
            {"name": "Barnadi River", "type": "river", "bbox": (91.97, 26.4, 92.09, 26.48)},
        ],
        "Hojai": [
            {"name": "Kopili River area", "type": "river", "bbox": (92.8, 25.96, 92.92, 26.04)},
        ],
        "Biswanath Chariali": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (93.09, 26.69, 93.21, 26.77)},
        ],
        "Majuli (island town)": [
            {"name": "Brahmaputra River", "type": "river", "bbox": (94.11, 26.91, 94.23, 26.99)},
        ],
        "Sadiya": [
            {"name": "Brahmaputra", "type": "river", "bbox": (95.61, 27.79, 95.73, 27.87)},
            {"name": "Lohit", "type": "river", "bbox": (95.61, 27.79, 95.73, 27.87)},
            {"name": "Dibang confluence", "type": "river", "bbox": (95.61, 27.79, 95.73, 27.87)},
        ],
        "Rangia": [
            {"name": "Brahmaputra", "type": "river", "bbox": (91.57, 26.41, 91.69, 26.49)},
        ],
        "Pathsala": [
            {"name": "Puthimari River", "type": "river", "bbox": (91.12, 26.45, 91.24, 26.53)},
        ],
    },

    # -------------------------------------------------------------------------
    # 4. BIHAR
    # -------------------------------------------------------------------------
    "Bihar": {
        "Patna": [
            {"name": "Ganga River", "type": "river", "bbox": (85.08, 25.57, 85.2, 25.65)},
            {"name": "Son River", "type": "river", "bbox": (85.08, 25.57, 85.2, 25.65)},
            {"name": "Punpun River", "type": "river", "bbox": (85.08, 25.57, 85.2, 25.65)},
        ],
        "Gaya": [
            {"name": "Phalgu River", "type": "river", "bbox": (84.94, 24.76, 85.06, 24.84)},
            {"name": "Niranjana + Mohana", "type": "river", "bbox": (84.94, 24.76, 85.06, 24.84)},
        ],
        "Bhagalpur": [
            {"name": "Ganga River", "type": "river", "bbox": (86.91, 25.2, 87.03, 25.28)},
        ],
        "Muzaffarpur": [
            {"name": "Gandak River", "type": "river", "bbox": (85.33, 26.08, 85.45, 26.16)},
            {"name": "Budhi Gandak River", "type": "river", "bbox": (85.33, 26.08, 85.45, 26.16)},
        ],
        "Munger (Monghyr)": [
            {"name": "Ganga River", "type": "river", "bbox": (86.41, 25.33, 86.53, 25.41)},
        ],
        "Darbhanga": [
            {"name": "Bagmati River", "type": "river", "bbox": (85.84, 26.11, 85.96, 26.19)},
            {"name": "Kamla River", "type": "river", "bbox": (85.84, 26.11, 85.96, 26.19)},
        ],
        "Buxar": [
            {"name": "Ganga River", "type": "river", "bbox": (83.92, 25.52, 84.04, 25.6)},
        ],
        "Arrah (Ara)": [
            {"name": "Son River area", "type": "river", "bbox": (84.6, 25.52, 84.72, 25.6)},
        ],
        "Chapra (Chhapra)": [
            {"name": "Ghaghara", "type": "river", "bbox": (84.68, 25.74, 84.8, 25.82)},
            {"name": "Gandak confluence near Ganga", "type": "river", "bbox": (84.68, 25.74, 84.8, 25.82)},
        ],
        "Sasaram": [
            {"name": "Son River", "type": "river", "bbox": (83.97, 24.91, 84.09, 24.99)},
        ],
        "Begusarai": [
            {"name": "Ganga River", "type": "river", "bbox": (86.07, 25.38, 86.19, 25.46)},
            {"name": "Balan River", "type": "river", "bbox": (86.07, 25.38, 86.19, 25.46)},
        ],
        "Samastipur": [
            {"name": "Budhi Gandak River", "type": "river", "bbox": (85.72, 25.82, 85.84, 25.9)},
        ],
        "Purnia": [
            {"name": "Kosi River", "type": "river", "bbox": (87.41, 25.74, 87.53, 25.82)},
            {"name": "Saura River", "type": "river", "bbox": (87.41, 25.74, 87.53, 25.82)},
        ],
        "Katihar": [
            {"name": "Ganga River", "type": "river", "bbox": (87.51, 25.5, 87.63, 25.58)},
            {"name": "Mahananda River", "type": "river", "bbox": (87.51, 25.5, 87.63, 25.58)},
        ],
        "Hajipur": [
            {"name": "Gandak River", "type": "river", "bbox": (85.15, 25.65, 85.27, 25.73)},
            {"name": "Ganga confluence", "type": "river", "bbox": (85.15, 25.65, 85.27, 25.73)},
        ],
        "Bettiah": [
            {"name": "Gandak", "type": "river", "bbox": (84.46, 26.76, 84.58, 26.84)},
        ],
        "Motihari": [
            {"name": "Gandak tributaries", "type": "river", "bbox": (84.86, 26.62, 84.98, 26.7)},
        ],
        "Siwan": [
            {"name": "Ghaghara", "type": "river", "bbox": (84.98, 25.64, 85.1, 25.72)},
            {"name": "Daha", "type": "river", "bbox": (84.98, 25.64, 85.1, 25.72)},
        ],
        "Gopalganj": [
            {"name": "Gandak", "type": "river", "bbox": (85.01, 25.58, 85.13, 25.66)},
        ],
        "Madhubani": [
            {"name": "Kamla River", "type": "river", "bbox": (86.01, 26.31, 86.13, 26.39)},
            {"name": "Kareh River", "type": "river", "bbox": (86.01, 26.31, 86.13, 26.39)},
        ],
        "Sitamarhi": [
            {"name": "Bagmati River", "type": "river", "bbox": (85.43, 26.55, 85.55, 26.63)},
        ],
        "Aurangabad": [
            {"name": "Son River area", "type": "river", "bbox": (85.03, 25.51, 85.15, 25.59)},
        ],
        "Nawada": [
            {"name": "Phalgu tributaries", "type": "river", "bbox": (85.48, 24.85, 85.6, 24.93)},
        ],
        "Jehanabad": [
            {"name": "Phalgu", "type": "river", "bbox": (85.17, 25.57, 85.29, 25.65)},
            {"name": "Punpun", "type": "river", "bbox": (85.17, 25.57, 85.29, 25.65)},
        ],
        "Saharsa": [
            {"name": "Kosi River", "type": "river", "bbox": (86.54, 25.84, 86.66, 25.92)},
        ],
        "Supaul": [
            {"name": "Kosi River", "type": "river", "bbox": (86.54, 26.08, 86.66, 26.16)},
        ],
        "Kishanganj": [
            {"name": "Mahananda River", "type": "river", "bbox": (87.89, 26.06, 88.01, 26.14)},
        ],
        "Khagaria": [
            {"name": "Ganga River", "type": "river", "bbox": (85.12, 25.53, 85.24, 25.61)},
        ],
        "Banka": [
            {"name": "Chandan River", "type": "river", "bbox": (86.86, 24.85, 86.98, 24.93)},
        ],
        "Sheikhpura": [
            {"name": "Kiul River", "type": "river", "bbox": (85.06, 25.66, 85.18, 25.74)},
        ],
        "Lakhisarai": [
            {"name": "Kiul River", "type": "river", "bbox": (85.11, 25.63, 85.23, 25.71)},
        ],
        "Jamui": [
            {"name": "Kiul", "type": "river", "bbox": (85.12, 25.52, 85.24, 25.6)},
        ],
        "Dehri-on-Sone": [
            {"name": "Son River", "type": "river", "bbox": (85.04, 25.64, 85.16, 25.72)},
        ],
        "Rajgir": [
            {"name": "Panchane River", "type": "river", "bbox": (85.36, 24.99, 85.48, 25.07)},
        ],
        "Nalanda": [
            {"name": "rivers", "type": "river", "bbox": (85.04, 25.67, 85.16, 25.75)},
            {"name": "ponds", "type": "lake", "bbox": (85.07, 25.69, 85.13, 25.73)},
        ],
        "Barh": [
            {"name": "Ganga River", "type": "river", "bbox": (85.65, 25.44, 85.77, 25.52)},
        ],
        "Mokama": [
            {"name": "Ganga River", "type": "river", "bbox": (85.86, 25.36, 85.98, 25.44)},
        ],
        "Sultanganj": [
            {"name": "Ganga River", "type": "river", "bbox": (86.68, 25.21, 86.8, 25.29)},
        ],
        "Kahalgaon": [
            {"name": "Ganga River", "type": "river", "bbox": (87.18, 25.22, 87.3, 25.3)},
        ],
        "Dumraon": [
            {"name": "Son area", "type": "river", "bbox": (85.05, 25.56, 85.17, 25.64)},
        ],
        "Revelganj": [
            {"name": "Ganga-Gandak confluence", "type": "river", "bbox": (84.98, 25.56, 85.1, 25.64)},
        ],
        "Sonepur": [
            {"name": "Ganga-Gandak confluence", "type": "river", "bbox": (85.12, 25.66, 85.24, 25.74)},
            {"name": "Harishchandra Kshetra", "type": "river", "bbox": (85.12, 25.66, 85.24, 25.74)},
        ],
        "Valmikinagar": [
            {"name": "Gandak River", "type": "river", "bbox": (85.07, 25.6, 85.19, 25.68)},
        ],
        "Barauni": [
            {"name": "Ganga River", "type": "river", "bbox": (85.15, 25.52, 85.27, 25.6)},
            {"name": "Budhi Gandak", "type": "river", "bbox": (85.15, 25.52, 85.27, 25.6)},
        ],
        "Maner": [
            {"name": "Ganga-Son confluence area", "type": "river", "bbox": (85.17, 25.55, 85.29, 25.63)},
        ],
        "Bikramganj": [
            {"name": "Son River area", "type": "river", "bbox": (85.07, 25.61, 85.19, 25.69)},
        ],
    },

    # -------------------------------------------------------------------------
    # 5. CHHATTISGARH
    # -------------------------------------------------------------------------
    "Chhattisgarh": {
        "Raipur": [
            {"name": "Kharun River", "type": "river", "bbox": (81.57, 21.21, 81.69, 21.29)},
        ],
        "Bilaspur": [
            {"name": "Arpa River", "type": "river", "bbox": (82.09, 22.04, 82.21, 22.12)},
        ],
        "Jagdalpur": [
            {"name": "Indravati River", "type": "river", "bbox": (81.96, 19.04, 82.08, 19.12)},
        ],
        "Korba": [
            {"name": "Hasdeo River", "type": "river", "bbox": (82.62, 22.31, 82.74, 22.39)},
        ],
        "Durg": [
            {"name": "Sheonath River", "type": "river", "bbox": (81.22, 21.15, 81.34, 21.23)},
        ],
        "Bhilai": [
            {"name": "Sheonath River", "type": "river", "bbox": (81.32, 21.17, 81.44, 21.25)},
        ],
        "Rajnandgaon": [
            {"name": "Sheonath tributaries", "type": "river", "bbox": (80.97, 21.06, 81.09, 21.14)},
        ],
        "Raigarh": [
            {"name": "Kelo River", "type": "river", "bbox": (83.34, 21.86, 83.46, 21.94)},
        ],
        "Ambikapur": [
            {"name": "Rihand", "type": "river", "bbox": (83.14, 23.08, 83.26, 23.16)},
            {"name": "Renuka", "type": "river", "bbox": (83.14, 23.08, 83.26, 23.16)},
        ],
        "Dhamtari": [
            {"name": "Mahanadi River", "type": "river", "bbox": (81.49, 20.67, 81.61, 20.75)},
        ],
        "Kawardha": [
            {"name": "Sakri River", "type": "river", "bbox": (81.53, 21.19, 81.65, 21.27)},
        ],
        "Janjgir": [
            {"name": "Hasdeo area", "type": "river", "bbox": (82.51, 21.97, 82.63, 22.05)},
        ],
        "Champa": [
            {"name": "Hasdeo River", "type": "river", "bbox": (81.6, 21.15, 81.72, 21.23)},
        ],
        "Jashpur": [
            {"name": "Ib", "type": "river", "bbox": (81.64, 21.21, 81.76, 21.29)},
            {"name": "Kanhar", "type": "river", "bbox": (81.64, 21.21, 81.76, 21.29)},
        ],
        "Kanker": [
            {"name": "Mahanadi tributary", "type": "river", "bbox": (81.43, 20.23, 81.55, 20.31)},
            {"name": "Dudh River", "type": "river", "bbox": (81.43, 20.23, 81.55, 20.31)},
        ],
        "Kondagaon": [
            {"name": "Narangi River", "type": "river", "bbox": (81.6, 19.56, 81.72, 19.64)},
        ],
        "Mahasamund": [
            {"name": "Mahanadi basin", "type": "river", "bbox": (82.04, 21.07, 82.16, 21.15)},
        ],
        "Balod": [
            {"name": "Tandula River", "type": "river", "bbox": (81.14, 20.69, 81.26, 20.77)},
        ],
        "Bemetara": [
            {"name": "Sheonath area", "type": "river", "bbox": (81.47, 21.68, 81.59, 21.76)},
        ],
        "Mungeli": [
            {"name": "Maniyari River", "type": "river", "bbox": (81.62, 22.03, 81.74, 22.11)},
        ],
        "Surajpur": [
            {"name": "Rihand", "type": "river", "bbox": (82.81, 23.17, 82.93, 23.25)},
        ],
        "Balrampur": [
            {"name": "Kanhar", "type": "river", "bbox": (81.55, 21.2, 81.67, 21.28)},
        ],
        "Dongargarh": [
            {"name": "rivers", "type": "river", "bbox": (81.6, 21.27, 81.72, 21.35)},
        ],
        "Manendragarh": [
            {"name": "Hasdeo", "type": "river", "bbox": (81.51, 21.29, 81.63, 21.37)},
        ],
        "Baikunthpur": [
            {"name": "Son", "type": "river", "bbox": (81.6, 21.13, 81.72, 21.21)},
            {"name": "Hasdeo", "type": "river", "bbox": (81.6, 21.13, 81.72, 21.21)},
        ],
        "Sarangarh": [
            {"name": "Mand River", "type": "river", "bbox": (81.63, 21.3, 81.75, 21.38)},
        ],
        "Akaltara": [
            {"name": "Lilagar River", "type": "river", "bbox": (81.66, 21.2, 81.78, 21.28)},
        ],
        "Ratanpur": [
            {"name": "Lilagar", "type": "river", "bbox": (81.67, 21.27, 81.79, 21.35)},
        ],
        "Rajim": [
            {"name": "Mahanadi-Pairi-Sondhur Triveni Sangam", "type": "river", "bbox": (81.59, 21.26, 81.71, 21.34)},
        ],
        "Shivrinarayan": [
            {"name": "Mahanadi-Sheonath-Jonk confluence", "type": "river", "bbox": (81.64, 21.11, 81.76, 21.19)},
        ],
        "Chitrakote": [
            {"name": "Indravati River", "type": "river", "bbox": (81.6, 21.23, 81.72, 21.31)},
            {"name": "Chitrakote Falls", "type": "river", "bbox": (81.6, 21.23, 81.72, 21.31)},
        ],
    },

    # -------------------------------------------------------------------------
    # 6. GOA
    # -------------------------------------------------------------------------
    "Goa": {
        "Panaji (Panjim)": [
            {"name": "Mandovi River", "type": "river", "bbox": (73.77, 15.45, 73.89, 15.53)},
        ],
        "Margao (Madgaon)": [
            {"name": "Sal River", "type": "river", "bbox": (73.9, 15.23, 74.02, 15.31)},
        ],
        "Vasco da Gama": [
            {"name": "Zuari River", "type": "river", "bbox": (73.75, 15.36, 73.87, 15.44)},
        ],
        "Mapusa": [
            {"name": "Mapusa River", "type": "river", "bbox": (73.75, 15.55, 73.87, 15.63)},
        ],
        "Ponda": [
            {"name": "Zuari River", "type": "river", "bbox": (73.95, 15.36, 74.07, 15.44)},
            {"name": "Kushavati River", "type": "river", "bbox": (73.95, 15.36, 74.07, 15.44)},
        ],
        "Old Goa": [
            {"name": "Mandovi River", "type": "river", "bbox": (73.79, 15.39, 73.91, 15.47)},
        ],
        "Bicholim": [
            {"name": "Mandovi tributaries", "type": "river", "bbox": (73.89, 15.55, 74.01, 15.63)},
        ],
        "Canacona": [
            {"name": "Talpona River", "type": "lake", "bbox": (74.02, 14.99, 74.08, 15.03)},
        ],
        "Quepem": [
            {"name": "Kushavati River", "type": "river", "bbox": (74.02, 15.17, 74.14, 15.25)},
        ],
        "Sanguem": [
            {"name": "Zuari River", "type": "river", "bbox": (74.09, 15.19, 74.21, 15.27)},
            {"name": "upstream", "type": "river", "bbox": (74.09, 15.19, 74.21, 15.27)},
        ],
        "Sanquelim": [
            {"name": "Mandovi", "type": "river", "bbox": (73.73, 15.53, 73.85, 15.61)},
        ],
        "Curchorem": [
            {"name": "Zuari area", "type": "river", "bbox": (73.87, 15.47, 73.99, 15.55)},
        ],
        "Pernem": [
            {"name": "Chapora River", "type": "river", "bbox": (73.74, 15.68, 73.86, 15.76)},
        ],
        "Valpoi": [
            {"name": "Mandovi River", "type": "river", "bbox": (73.74, 15.35, 73.86, 15.43)},
            {"name": "Mahadayi", "type": "river", "bbox": (73.74, 15.35, 73.86, 15.43)},
        ],
        "Cortalim": [
            {"name": "Zuari River", "type": "river", "bbox": (73.86, 15.36, 73.98, 15.44)},
        ],
        "Tiswadi": [
            {"name": "Mandovi", "type": "river", "bbox": (73.81, 15.43, 73.93, 15.51)},
            {"name": "Zuari", "type": "river", "bbox": (73.81, 15.43, 73.93, 15.51)},
        ],
    },

    # -------------------------------------------------------------------------
    # 7. GUJARAT
    # -------------------------------------------------------------------------
    "Gujarat": {
        "Ahmedabad": [
            {"name": "Sabarmati River", "type": "river", "bbox": (72.51, 22.98, 72.63, 23.06)},
            {"name": "Kankaria Lake", "type": "lake", "bbox": (72.54, 23.0, 72.6, 23.04)},
        ],
        "Surat": [
            {"name": "Tapi River", "type": "river", "bbox": (72.77, 21.13, 72.89, 21.21)},
        ],
        "Vadodara (Baroda)": [
            {"name": "Vishwamitri River", "type": "river", "bbox": (73.13, 22.27, 73.25, 22.35)},
        ],
        "Rajkot": [
            {"name": "Aji River", "type": "river", "bbox": (70.74, 22.26, 70.86, 22.34)},
            {"name": "Nyari River", "type": "river", "bbox": (70.74, 22.26, 70.86, 22.34)},
        ],
        "Bharuch": [
            {"name": "Narmada River", "type": "river", "bbox": (72.94, 21.66, 73.06, 21.74)},
        ],
        "Junagadh": [
            {"name": "Suvarnarekha River", "type": "river", "bbox": (70.4, 21.48, 70.52, 21.56)},
        ],
        "Bhavnagar": [
            {"name": "Shetrunji River area", "type": "river", "bbox": (72.09, 21.72, 72.21, 21.8)},
        ],
        "Anand": [
            {"name": "Mahi River", "type": "river", "bbox": (72.89, 22.52, 73.01, 22.6)},
        ],
        "Nadiad": [
            {"name": "Mahi area", "type": "river", "bbox": (72.8, 22.65, 72.92, 22.73)},
        ],
        "Gandhinagar": [
            {"name": "Sabarmati River", "type": "river", "bbox": (72.58, 23.18, 72.7, 23.26)},
        ],
        "Porbandar": [
            {"name": "coast", "type": "river", "bbox": (69.55, 21.6, 69.67, 21.68)},
        ],
        "Jamnagar": [
            {"name": "Nagmati River", "type": "river", "bbox": (70.01, 22.43, 70.13, 22.51)},
            {"name": "Rangmati River", "type": "river", "bbox": (70.01, 22.43, 70.13, 22.51)},
            {"name": "Lakhota Lake", "type": "lake", "bbox": (70.04, 22.45, 70.1, 22.49)},
        ],
        "Mehsana": [
            {"name": "Saraswati River", "type": "river", "bbox": (72.32, 23.55, 72.44, 23.63)},
        ],
        "Patan": [
            {"name": "Saraswati River", "type": "river", "bbox": (72.07, 23.81, 72.19, 23.89)},
        ],
        "Palanpur": [
            {"name": "Banas River", "type": "river", "bbox": (72.38, 24.13, 72.5, 24.21)},
        ],
        "Navsari": [
            {"name": "Purna River", "type": "river", "bbox": (72.86, 20.91, 72.98, 20.99)},
        ],
        "Valsad": [
            {"name": "Auranga River", "type": "river", "bbox": (72.87, 20.59, 72.99, 20.67)},
        ],
        "Morbi": [
            {"name": "Machhu River", "type": "river", "bbox": (70.77, 22.78, 70.89, 22.86)},
        ],
        "Surendranagar": [
            {"name": "Bhogavo River", "type": "river", "bbox": (71.62, 22.69, 71.74, 22.77)},
        ],
        "Dahod": [
            {"name": "Mahi River", "type": "river", "bbox": (74.19, 22.8, 74.31, 22.88)},
        ],
        "Godhra": [
            {"name": "Mahi River", "type": "river", "bbox": (73.56, 22.74, 73.68, 22.82)},
        ],
        "Bhuj": [
            {"name": "Hamirsar Lake", "type": "lake", "bbox": (72.66, 23.14, 72.72, 23.18)},
            {"name": "Khari River", "type": "river", "bbox": (72.63, 23.12, 72.75, 23.2)},
        ],
        "Dwarka": [
            {"name": "Gomti River", "type": "river", "bbox": (68.91, 22.2, 69.03, 22.28)},
        ],
        "Dholka": [
            {"name": "Sabarmati", "type": "river", "bbox": (72.54, 23.12, 72.66, 23.2)},
        ],
        "Kheda": [
            {"name": "Vatrak River", "type": "river", "bbox": (72.63, 23.17, 72.75, 23.25)},
        ],
        "Amreli": [
            {"name": "Shetrunji area", "type": "river", "bbox": (72.54, 23.14, 72.66, 23.22)},
        ],
        "Veraval": [
            {"name": "coast", "type": "river", "bbox": (70.31, 20.87, 70.43, 20.95)},
        ],
        "Vapi": [
            {"name": "Damanganga area", "type": "lake", "bbox": (72.64, 23.21, 72.7, 23.25)},
        ],
        "Anklesvar": [
            {"name": "Narmada River", "type": "river", "bbox": (72.63, 23.2, 72.75, 23.28)},
        ],
        "Kevadia": [
            {"name": "Narmada River", "type": "river", "bbox": (72.65, 23.26, 72.77, 23.34)},
            {"name": "Sardar Sarovar Dam", "type": "lake", "bbox": (72.68, 23.28, 72.74, 23.32)},
        ],
        "Chanod": [
            {"name": "Narmada River", "type": "river", "bbox": (72.63, 23.13, 72.75, 23.21)},
        ],
        "Dakor": [
            {"name": "Gomti River", "type": "river", "bbox": (72.54, 23.11, 72.66, 23.19)},
        ],
        "Sidhpur": [
            {"name": "Saraswati River", "type": "river", "bbox": (72.63, 23.25, 72.75, 23.32)},
        ],
        "Himmatnagar": [
            {"name": "Hathmati River", "type": "river", "bbox": (72.58, 23.21, 72.7, 23.29)},
        ],
        "Modasa": [
            {"name": "Meshwo River", "type": "river", "bbox": (72.6, 23.19, 72.72, 23.27)},
        ],
        "Rajpipla": [
            {"name": "Narmada", "type": "river", "bbox": (72.64, 23.28, 72.76, 23.36)},
        ],
        "Songadh": [
            {"name": "Mahi", "type": "river", "bbox": (72.51, 23.14, 72.63, 23.22)},
        ],
        "Tapi (town)": [
            {"name": "Tapi River", "type": "river", "bbox": (72.55, 23.09, 72.67, 23.17)},
        ],
        "Bardoli": [
            {"name": "Tapi", "type": "river", "bbox": (73.05, 21.08, 73.17, 21.16)},
        ],
        "Dabhoi": [
            {"name": "Mahi", "type": "river", "bbox": (72.53, 23.13, 72.65, 23.21)},
        ],
        "Kalol": [
            {"name": "Sabarmati", "type": "river", "bbox": (72.53, 23.14, 72.65, 23.22)},
        ],
        "Mandvi": [
            {"name": "Rukmavati River", "type": "river", "bbox": (72.66, 23.09, 72.78, 23.17)},
        ],
        "Mundra": [
            {"name": "coast", "type": "river", "bbox": (72.66, 23.25, 72.78, 23.33)},
        ],
        "Wankaner": [
            {"name": "Machhu River", "type": "river", "bbox": (72.6, 23.28, 72.72, 23.36)},
        ],
        "Gondal": [
            {"name": "Gondali River", "type": "river", "bbox": (72.56, 23.09, 72.68, 23.17)},
        ],
        "Dhari": [
            {"name": "Shetrunji", "type": "river", "bbox": (72.61, 23.21, 72.73, 23.29)},
        ],
        "Palitana": [
            {"name": "Shetrunji", "type": "river", "bbox": (72.56, 23.19, 72.68, 23.27)},
        ],
        "Garudeshwar": [
            {"name": "Narmada River", "type": "river", "bbox": (72.53, 23.14, 72.65, 23.22)},
        ],
    },

    # -------------------------------------------------------------------------
    # 8. HARYANA
    # -------------------------------------------------------------------------
    "Haryana": {
        "Faridabad": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.25, 28.37, 77.37, 28.45)},
            {"name": "Badkhal Lake", "type": "lake", "bbox": (77.28, 28.39, 77.34, 28.43)},
        ],
        "Yamunanagar": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.21, 30.09, 77.33, 30.17)},
        ],
        "Karnal": [
            {"name": "Yamuna", "type": "river", "bbox": (76.92, 29.65, 77.04, 29.73)},
        ],
        "Panipat": [
            {"name": "Yamuna", "type": "river", "bbox": (76.91, 29.35, 77.03, 29.43)},
        ],
        "Ambala": [
            {"name": "Ghaggar River", "type": "river", "bbox": (76.72, 30.34, 76.84, 30.42)},
            {"name": "Tangri River", "type": "river", "bbox": (76.72, 30.34, 76.84, 30.42)},
        ],
        "Sonipat": [
            {"name": "Yamuna", "type": "river", "bbox": (76.96, 28.95, 77.08, 29.03)},
        ],
        "Rohtak": [
            {"name": "Sahbi River", "type": "river", "bbox": (76.53, 28.85, 76.65, 28.93)},
            {"name": "Tilyar Lake", "type": "lake", "bbox": (76.56, 28.87, 76.62, 28.91)},
        ],
        "Hisar": [
            {"name": "Ghaggar", "type": "river", "bbox": (75.66, 29.11, 75.78, 29.19)},
            {"name": "Blue Bird Lake", "type": "lake", "bbox": (75.69, 29.13, 75.75, 29.17)},
        ],
        "Panchkula": [
            {"name": "Ghaggar River", "type": "river", "bbox": (76.8, 30.65, 76.92, 30.73)},
        ],
        "Kurukshetra": [
            {"name": "Saraswati River", "type": "river", "bbox": (76.78, 29.93, 76.9, 30.01)},
            {"name": "Brahma Sarovar", "type": "lake", "bbox": (76.81, 29.95, 76.87, 29.99)},
        ],
        "Sirsa": [
            {"name": "Ghaggar River", "type": "river", "bbox": (74.97, 29.49, 75.09, 29.57)},
        ],
        "Kaithal": [
            {"name": "Ghaggar", "type": "river", "bbox": (76.34, 29.76, 76.46, 29.84)},
        ],
        "Jind": [
            {"name": "Chautang", "type": "river", "bbox": (76.26, 29.28, 76.38, 29.36)},
        ],
        "Bhiwani": [
            {"name": "Dohan", "type": "river", "bbox": (76.07, 28.75, 76.19, 28.83)},
        ],
        "Rewari": [
            {"name": "Sahbi", "type": "river", "bbox": (76.56, 28.15, 76.68, 28.23)},
            {"name": "Krishnavati", "type": "river", "bbox": (76.56, 28.15, 76.68, 28.23)},
        ],
        "Palwal": [
            {"name": "Yamuna", "type": "river", "bbox": (77.27, 28.1, 77.39, 28.18)},
        ],
        "Narnaul": [
            {"name": "Dohan", "type": "river", "bbox": (76.05, 28.0, 76.17, 28.08)},
        ],
        "Gurugram (Gurgaon)": [
            {"name": "Yamuna", "type": "river", "bbox": (76.97, 28.42, 77.09, 28.5)},
            {"name": "Sahbi Nadi area", "type": "river", "bbox": (76.97, 28.42, 77.09, 28.5)},
            {"name": "Damdama Lake", "type": "lake", "bbox": (77.0, 28.44, 77.06, 28.48)},
        ],
        "Pehowa": [
            {"name": "Saraswati River", "type": "river", "bbox": (76.69, 30.62, 76.81, 30.7)},
        ],
        "Thanesar": [
            {"name": "Saraswati River", "type": "river", "bbox": (76.76, 29.93, 76.88, 30.01)},
            {"name": "Kurukshetra area", "type": "river", "bbox": (76.76, 29.93, 76.88, 30.01)},
        ],
        "Hodal": [
            {"name": "Yamuna", "type": "river", "bbox": (76.65, 30.67, 76.77, 30.75)},
        ],
        "Ballabgarh": [
            {"name": "Yamuna River", "type": "river", "bbox": (76.71, 30.72, 76.83, 30.8)},
        ],
        "Hansi": [
            {"name": "rivers", "type": "river", "bbox": (76.73, 30.67, 76.85, 30.75)},
            {"name": "historical Saraswati", "type": "river", "bbox": (76.73, 30.67, 76.85, 30.75)},
        ],
        "Jhajjar": [
            {"name": "Sahbi Nadi", "type": "river", "bbox": (76.7, 30.68, 76.82, 30.76)},
        ],
        "Mahendragarh": [
            {"name": "seasonal rivers", "type": "river", "bbox": (76.73, 30.68, 76.85, 30.76)},
        ],
        "Nuh (Mewat)": [
            {"name": "Sahbi Nadi area", "type": "river", "bbox": (76.69, 30.78, 76.81, 30.86)},
        ],
        "Pinjore": [
            {"name": "Ghaggar tributaries", "type": "river", "bbox": (76.65, 30.68, 76.77, 30.76)},
        ],
        "Sadhaura": [
            {"name": "Markanda River", "type": "river", "bbox": (76.68, 30.63, 76.8, 30.71)},
        ],
        "Kalesar": [
            {"name": "Yamuna", "type": "river", "bbox": (76.67, 30.71, 76.79, 30.79)},
        ],
        "Hathin": [
            {"name": "seasonal rivers", "type": "river", "bbox": (76.63, 30.63, 76.75, 30.71)},
        ],
    },

    # -------------------------------------------------------------------------
    # 9. HIMACHAL PRADESH
    # -------------------------------------------------------------------------
    "Himachal Pradesh": {
        "Shimla": [
            {"name": "Sutlej basin", "type": "river", "bbox": (77.11, 31.06, 77.23, 31.14)},
            {"name": "Jhakri area", "type": "river", "bbox": (77.11, 31.06, 77.23, 31.14)},
        ],
        "Manali": [
            {"name": "Beas River", "type": "river", "bbox": (77.13, 32.2, 77.25, 32.28)},
            {"name": "Parvati River", "type": "river", "bbox": (77.13, 32.2, 77.25, 32.28)},
        ],
        "Kullu": [
            {"name": "Beas River", "type": "river", "bbox": (77.05, 31.92, 77.17, 32.0)},
        ],
        "Dharamshala": [
            {"name": "Beas tributaries", "type": "river", "bbox": (76.26, 32.18, 76.38, 32.26)},
        ],
        "Mandi": [
            {"name": "Beas River", "type": "river", "bbox": (76.87, 31.67, 76.99, 31.75)},
        ],
        "Bilaspur": [
            {"name": "Sutlej River", "type": "river", "bbox": (82.09, 22.04, 82.21, 22.12)},
            {"name": "Gobind Sagar Lake", "type": "lake", "bbox": (82.12, 22.06, 82.18, 22.1)},
        ],
        "Solan": [
            {"name": "Ashwani Khad", "type": "river", "bbox": (77.04, 30.87, 77.16, 30.95)},
        ],
        "Hamirpur": [
            {"name": "Beas", "type": "river", "bbox": (77.1, 31.01, 77.22, 31.09)},
        ],
        "Una": [
            {"name": "Swan River", "type": "river", "bbox": (76.21, 31.43, 76.33, 31.51)},
        ],
        "Chamba": [
            {"name": "Ravi River", "type": "river", "bbox": (76.07, 32.52, 76.19, 32.6)},
        ],
        "Kangra": [
            {"name": "Beas tributaries", "type": "river", "bbox": (76.21, 32.06, 76.33, 32.14)},
        ],
        "Nahan": [
            {"name": "Markanda River", "type": "river", "bbox": (77.24, 30.52, 77.36, 30.6)},
        ],
        "Keylong": [
            {"name": "Bhaga River", "type": "river", "bbox": (76.98, 32.53, 77.1, 32.61)},
            {"name": "Chandra River", "type": "river", "bbox": (76.98, 32.53, 77.1, 32.61)},
        ],
        "Rampur (Bushahr)": [
            {"name": "Sutlej River", "type": "river", "bbox": (78.96, 28.77, 79.08, 28.85)},
        ],
        "Sundernagar": [
            {"name": "Suketi Khad", "type": "river", "bbox": (76.84, 31.49, 76.96, 31.57)},
        ],
        "Palampur": [
            {"name": "Neugal Khad", "type": "river", "bbox": (76.48, 32.07, 76.6, 32.15)},
        ],
        "Kaza": [
            {"name": "Spiti River", "type": "river", "bbox": (77.07, 31.08, 77.19, 31.16)},
        ],
        "Reckong Peo": [
            {"name": "Sutlej River", "type": "river", "bbox": (77.05, 31.02, 77.17, 31.1)},
            {"name": "Baspa River area", "type": "river", "bbox": (77.05, 31.02, 77.17, 31.1)},
        ],
        "Bhuntar": [
            {"name": "Beas-Parvati confluence", "type": "river", "bbox": (77.17, 31.07, 77.29, 31.15)},
        ],
        "Kasauli": [
            {"name": "seasonal streams", "type": "river", "bbox": (77.09, 31.16, 77.21, 31.24)},
        ],
        "Manikaran": [
            {"name": "Parvati River", "type": "river", "bbox": (77.02, 31.14, 77.14, 31.22)},
        ],
        "Baijnath": [
            {"name": "Binwa River", "type": "river", "bbox": (77.11, 31.01, 77.23, 31.09)},
        ],
        "Jogindernagar": [
            {"name": "Uhl River", "type": "river", "bbox": (77.12, 30.97, 77.24, 31.05)},
        ],
        "Sujanpur Tira": [
            {"name": "Beas River", "type": "river", "bbox": (77.09, 31.14, 77.21, 31.22)},
        ],
        "Nadaun": [
            {"name": "Beas River", "type": "river", "bbox": (77.17, 30.98, 77.29, 31.06)},
        ],
        "Nalagarh": [
            {"name": "Sirsa River", "type": "river", "bbox": (77.12, 30.99, 77.24, 31.07)},
        ],
        "Parwanoo": [
            {"name": "streams", "type": "river", "bbox": (76.9, 30.8, 77.02, 30.88)},
        ],
        "Tabo": [
            {"name": "Spiti River", "type": "river", "bbox": (77.09, 31.11, 77.21, 31.19)},
        ],
        "Sarahan": [
            {"name": "Sutlej", "type": "river", "bbox": (77.03, 31.03, 77.15, 31.11)},
        ],
        "Dalhousie": [
            {"name": "Ravi area", "type": "river", "bbox": (77.12, 31.07, 77.24, 31.15)},
        ],
        "Kalpa": [
            {"name": "Sutlej", "type": "river", "bbox": (77.19, 31.01, 77.31, 31.09)},
        ],
        "Tattapani": [
            {"name": "Sutlej River", "type": "river", "bbox": (77.05, 31.15, 77.17, 31.23)},
        ],
        "Pandoh": [
            {"name": "Beas River", "type": "river", "bbox": (77.18, 31.03, 77.3, 31.11)},
            {"name": "Pandoh Dam", "type": "lake", "bbox": (77.21, 31.05, 77.27, 31.09)},
        ],
        "Larji": [
            {"name": "Beas River", "type": "river", "bbox": (77.14, 30.97, 77.26, 31.05)},
        ],
    },

    # -------------------------------------------------------------------------
    # 10. JHARKHAND
    # -------------------------------------------------------------------------
    "Jharkhand": {
        "Ranchi": [
            {"name": "Subarnarekha River", "type": "river", "bbox": (85.25, 23.3, 85.37, 23.38)},
            {"name": "Kanchi River", "type": "river", "bbox": (85.25, 23.3, 85.37, 23.38)},
        ],
        "Jamshedpur": [
            {"name": "Subarnarekha River", "type": "river", "bbox": (86.14, 22.76, 86.26, 22.84)},
            {"name": "Kharkai River", "type": "river", "bbox": (86.14, 22.76, 86.26, 22.84)},
        ],
        "Dhanbad": [
            {"name": "Damodar River", "type": "lake", "bbox": (86.4, 23.77, 86.46, 23.81)},
        ],
        "Bokaro Steel City": [
            {"name": "Damodar River", "type": "lake", "bbox": (86.12, 23.65, 86.18, 23.69)},
            {"name": "Bokaro River", "type": "river", "bbox": (86.09, 23.63, 86.21, 23.71)},
        ],
        "Hazaribagh": [
            {"name": "Damodar tributaries", "type": "lake", "bbox": (85.33, 23.97, 85.39, 24.01)},
        ],
        "Deoghar": [
            {"name": "Ajay River", "type": "river", "bbox": (86.64, 24.45, 86.76, 24.53)},
        ],
        "Giridih": [
            {"name": "Usri River", "type": "river", "bbox": (86.24, 24.15, 86.36, 24.23)},
        ],
        "Dumka": [
            {"name": "Mayurakshi River", "type": "river", "bbox": (87.19, 24.23, 87.31, 24.31)},
        ],
        "Chaibasa": [
            {"name": "South Koel", "type": "river", "bbox": (85.74, 22.51, 85.86, 22.59)},
        ],
        "Ramgarh": [
            {"name": "Damodar", "type": "lake", "bbox": (85.53, 23.61, 85.59, 23.65)},
        ],
        "Daltonganj (Medininagar)": [
            {"name": "North Koel River", "type": "river", "bbox": (85.19, 23.27, 85.31, 23.35)},
        ],
        "Sahibganj": [
            {"name": "Ganga River", "type": "river", "bbox": (85.29, 23.31, 85.41, 23.39)},
        ],
        "Rajmahal": [
            {"name": "Ganga River", "type": "river", "bbox": (85.27, 23.23, 85.39, 23.31)},
        ],
        "Godda": [
            {"name": "Sundarpahari streams", "type": "river", "bbox": (87.15, 24.79, 87.27, 24.87)},
        ],
        "Pakur": [
            {"name": "streams", "type": "river", "bbox": (87.78, 24.59, 87.9, 24.67)},
            {"name": "Ganga nearby", "type": "river", "bbox": (87.78, 24.59, 87.9, 24.67)},
        ],
        "Chatra": [
            {"name": "Damodar headwaters", "type": "lake", "bbox": (84.84, 24.19, 84.9, 24.23)},
        ],
        "Gumla": [
            {"name": "South Koel", "type": "river", "bbox": (84.48, 23.0, 84.6, 23.08)},
        ],
        "Lohardaga": [
            {"name": "South Koel tributary", "type": "river", "bbox": (84.62, 23.4, 84.74, 23.48)},
        ],
        "Simdega": [
            {"name": "Sankh River", "type": "river", "bbox": (84.44, 22.58, 84.56, 22.66)},
        ],
        "Khunti": [
            {"name": "Karo River", "type": "river", "bbox": (85.22, 23.03, 85.34, 23.11)},
        ],
        "Koderma": [
            {"name": "Barakar", "type": "river", "bbox": (85.53, 24.43, 85.65, 24.51)},
        ],
        "Latehar": [
            {"name": "Auranga River", "type": "river", "bbox": (84.44, 23.7, 84.56, 23.78)},
        ],
        "Jamtara": [
            {"name": "Ajay River", "type": "river", "bbox": (85.25, 23.3, 85.37, 23.38)},
        ],
        "Saraikela": [
            {"name": "Kharkai", "type": "river", "bbox": (85.27, 23.36, 85.39, 23.44)},
        ],
        "Ghatshila": [
            {"name": "Subarnarekha River", "type": "river", "bbox": (85.28, 23.38, 85.4, 23.46)},
        ],
        "Sindri": [
            {"name": "Damodar", "type": "lake", "bbox": (85.27, 23.35, 85.33, 23.39)},
        ],
        "Tenughat": [
            {"name": "Damodar River", "type": "lake", "bbox": (85.3, 23.3, 85.36, 23.34)},
        ],
        "Chandil": [
            {"name": "Subarnarekha River", "type": "river", "bbox": (85.3, 23.31, 85.42, 23.39)},
            {"name": "Chandil Dam", "type": "lake", "bbox": (85.33, 23.33, 85.39, 23.37)},
        ],
    },

    # -------------------------------------------------------------------------
    # 11. KARNATAKA
    # -------------------------------------------------------------------------
    "Karnataka": {
        "Bengaluru": [
            {"name": "Vrishabhavathi River", "type": "river", "bbox": (77.53, 12.93, 77.65, 13.01)},
            {"name": "Arkavathi River", "type": "river", "bbox": (77.53, 12.93, 77.65, 13.01)},
            {"name": "Ulsoor Lake", "type": "lake", "bbox": (77.56, 12.95, 77.62, 12.99)},
            {"name": "Hebbal Lake", "type": "lake", "bbox": (77.56, 12.95, 77.62, 12.99)},
            {"name": "Bellandur Lake", "type": "lake", "bbox": (77.56, 12.95, 77.62, 12.99)},
            {"name": "Sankey Tank", "type": "lake", "bbox": (77.56, 12.95, 77.62, 12.99)},
            {"name": "Madiwala Lake", "type": "lake", "bbox": (77.56, 12.95, 77.62, 12.99)},
        ],
        "Mysuru (Mysore)": [
            {"name": "Kaveri", "type": "river", "bbox": (76.6, 12.26, 76.72, 12.34)},
            {"name": "Kukkarahalli Lake", "type": "lake", "bbox": (76.63, 12.28, 76.69, 12.32)},
            {"name": "Karanji Lake", "type": "lake", "bbox": (76.63, 12.28, 76.69, 12.32)},
        ],
        "Hubli-Dharwad": [
            {"name": "Malaprabha", "type": "river", "bbox": (77.52, 12.91, 77.64, 12.99)},
            {"name": "Unkal Lake", "type": "lake", "bbox": (77.55, 12.93, 77.61, 12.97)},
        ],
        "Mangaluru (Mangalore)": [
            {"name": "Nethravathi River", "type": "river", "bbox": (74.82, 12.83, 74.94, 12.91)},
            {"name": "Gurupura River", "type": "river", "bbox": (74.82, 12.83, 74.94, 12.91)},
        ],
        "Belagavi (Belgaum)": [
            {"name": "Malaprabha River", "type": "river", "bbox": (77.53, 12.93, 77.65, 13.01)},
        ],
        "Davangere": [
            {"name": "Tungabhadra", "type": "river", "bbox": (75.86, 14.43, 75.98, 14.51)},
        ],
        "Raichur": [
            {"name": "Krishna-Tungabhadra area", "type": "river", "bbox": (77.3, 16.17, 77.42, 16.25)},
        ],
        "Shivamogga (Shimoga)": [
            {"name": "Tunga River", "type": "river", "bbox": (75.51, 13.89, 75.63, 13.97)},
        ],
        "Kalaburagi (Gulbarga)": [
            {"name": "Bhima River", "type": "river", "bbox": (77.5, 13.01, 77.62, 13.09)},
        ],
        "Vijayapura (Bijapur)": [
            {"name": "Krishna tributaries", "type": "river", "bbox": (77.44, 12.97, 77.56, 13.05)},
        ],
        "Udupi": [
            {"name": "Swarna River", "type": "river", "bbox": (74.69, 13.3, 74.81, 13.38)},
            {"name": "Sita River", "type": "river", "bbox": (74.69, 13.3, 74.81, 13.38)},
        ],
        "Ballari (Bellary)": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.56, 12.99, 77.68, 13.07)},
        ],
        "Hassan": [
            {"name": "Hemavathi area", "type": "river", "bbox": (76.04, 12.97, 76.16, 13.05)},
        ],
        "Mandya": [
            {"name": "Kaveri", "type": "river", "bbox": (76.84, 12.48, 76.96, 12.56)},
            {"name": "Shimsha", "type": "river", "bbox": (76.84, 12.48, 76.96, 12.56)},
        ],
        "Hosapete (Hospet)": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.6, 12.99, 77.72, 13.07)},
        ],
        "Karwar": [
            {"name": "Kali River", "type": "river", "bbox": (77.59, 13.0, 77.71, 13.08)},
        ],
        "Kolar": [
            {"name": "Arkavathi", "type": "river", "bbox": (78.07, 13.1, 78.19, 13.18)},
            {"name": "Palar tributaries", "type": "river", "bbox": (78.07, 13.1, 78.19, 13.18)},
        ],
        "Tumkuru": [
            {"name": "Shimsha tributaries", "type": "river", "bbox": (77.61, 13.02, 77.73, 13.1)},
        ],
        "Chikkamagaluru": [
            {"name": "Bhadra River", "type": "river", "bbox": (77.59, 12.91, 77.71, 12.99)},
        ],
        "Bidar": [
            {"name": "Manjira", "type": "river", "bbox": (77.46, 17.87, 77.58, 17.95)},
        ],
        "Bagalkot": [
            {"name": "Ghataprabha River", "type": "river", "bbox": (75.64, 16.14, 75.76, 16.22)},
            {"name": "Krishna River", "type": "river", "bbox": (75.64, 16.14, 75.76, 16.22)},
        ],
        "Srirangapatna": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.53, 12.95, 77.65, 13.03)},
            {"name": "island between two channels", "type": "river", "bbox": (77.53, 12.95, 77.65, 13.03)},
        ],
        "Hampi": [
            {"name": "Tungabhadra River", "type": "river", "bbox": (77.44, 12.94, 77.56, 13.02)},
        ],
        "Madikeri (Coorg)": [
            {"name": "Kaveri origin area", "type": "river", "bbox": (77.52, 12.91, 77.64, 12.99)},
        ],
        "Ramanagara": [
            {"name": "Arkavathi River", "type": "river", "bbox": (77.22, 12.68, 77.34, 12.76)},
        ],
        "Chamarajanagar": [
            {"name": "Kabini", "type": "river", "bbox": (76.88, 11.88, 77.0, 11.96)},
        ],
        "Chitradurga": [
            {"name": "Vedavathi River", "type": "river", "bbox": (76.34, 14.19, 76.46, 14.27)},
        ],
        "Gadag": [
            {"name": "Malaprabha", "type": "river", "bbox": (75.57, 15.39, 75.69, 15.47)},
        ],
        "Haveri": [
            {"name": "Varada River", "type": "river", "bbox": (75.34, 14.75, 75.46, 14.83)},
        ],
        "Koppal": [
            {"name": "Tungabhadra", "type": "river", "bbox": (76.09, 15.31, 76.21, 15.39)},
        ],
        "Yadgir": [
            {"name": "Krishna", "type": "river", "bbox": (77.08, 16.73, 77.2, 16.81)},
            {"name": "Bhima", "type": "river", "bbox": (77.08, 16.73, 77.2, 16.81)},
        ],
        "Sirsi": [
            {"name": "Aghanashini", "type": "river", "bbox": (77.57, 12.99, 77.69, 13.07)},
        ],
        "Dandeli": [
            {"name": "Kali River", "type": "river", "bbox": (77.52, 12.88, 77.64, 12.96)},
        ],
        "Gokak": [
            {"name": "Ghataprabha River", "type": "river", "bbox": (77.45, 12.84, 77.57, 12.92)},
            {"name": "Gokak Falls", "type": "river", "bbox": (77.45, 12.84, 77.57, 12.92)},
        ],
        "Nanjangud": [
            {"name": "Kabini River", "type": "river", "bbox": (77.46, 12.9, 77.58, 12.98)},
        ],
        "T Narasipura": [
            {"name": "Kaveri-Kabini confluence", "type": "river", "bbox": (77.46, 12.84, 77.58, 12.92)},
        ],
        "Kollegal": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.54, 12.91, 77.66, 12.99)},
        ],
        "Bhadravathi": [
            {"name": "Bhadra River", "type": "river", "bbox": (77.58, 12.91, 77.7, 12.99)},
            {"name": "Tunga River", "type": "river", "bbox": (77.58, 12.91, 77.7, 12.99)},
        ],
        "Tirthahalli": [
            {"name": "Tunga River", "type": "river", "bbox": (77.6, 12.86, 77.72, 12.94)},
        ],
        "Sagar (Karnataka)": [
            {"name": "Sharavathi", "type": "river", "bbox": (78.68, 23.8, 78.8, 23.88)},
        ],
        "Jog Falls area": [
            {"name": "Sharavathi River", "type": "river", "bbox": (77.5, 12.91, 77.62, 12.99)},
        ],
        "Kushalnagar": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.61, 12.83, 77.73, 12.91)},
        ],
        "Talakadu": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.5, 12.93, 77.62, 13.01)},
        ],
        "Mekedatu": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.51, 12.88, 77.63, 12.96)},
        ],
        "Almatti": [
            {"name": "Krishna River", "type": "river", "bbox": (77.53, 13.03, 77.65, 13.11)},
            {"name": "Almatti Dam", "type": "lake", "bbox": (77.56, 13.05, 77.62, 13.09)},
        ],
        "Narayanpur": [
            {"name": "Krishna River", "type": "river", "bbox": (81.19, 19.69, 81.31, 19.77)},
            {"name": "Narayanpur Dam", "type": "lake", "bbox": (81.22, 19.71, 81.28, 19.75)},
        ],
        "Bhatkal": [
            {"name": "Sharavathi area", "type": "river", "bbox": (77.63, 12.97, 77.75, 13.05)},
        ],
        "Kundapura": [
            {"name": "rivers", "type": "river", "bbox": (77.56, 13.0, 77.68, 13.08)},
        ],
        "Puttur": [
            {"name": "Kumaradhara River", "type": "river", "bbox": (77.49, 12.9, 77.61, 12.98)},
        ],
        "Sullia": [
            {"name": "Payaswini River", "type": "river", "bbox": (77.63, 12.88, 77.75, 12.96)},
        ],
    },

    # -------------------------------------------------------------------------
    # 12. KERALA
    # -------------------------------------------------------------------------
    "Kerala": {
        "Thiruvananthapuram": [
            {"name": "Karamana River", "type": "river", "bbox": (76.88, 8.48, 77.0, 8.56)},
            {"name": "Killi River", "type": "river", "bbox": (76.88, 8.48, 77.0, 8.56)},
            {"name": "Vellayani Lake", "type": "lake", "bbox": (76.91, 8.5, 76.97, 8.54)},
        ],
        "Kochi (Ernakulam)": [
            {"name": "Periyar River", "type": "river", "bbox": (76.2, 9.89, 76.32, 9.97)},
            {"name": "Vembanad Lake backwaters", "type": "lake", "bbox": (76.23, 9.91, 76.29, 9.95)},
        ],
        "Kozhikode (Calicut)": [
            {"name": "Kallai River", "type": "river", "bbox": (75.71, 11.21, 75.83, 11.29)},
            {"name": "Kadalundi River", "type": "river", "bbox": (75.71, 11.21, 75.83, 11.29)},
        ],
        "Thrissur": [
            {"name": "Bharathapuzha", "type": "river", "bbox": (76.15, 10.49, 76.27, 10.57)},
            {"name": "Chalakudy River", "type": "river", "bbox": (76.15, 10.49, 76.27, 10.57)},
        ],
        "Kollam": [
            {"name": "Kallada River", "type": "river", "bbox": (76.54, 8.85, 76.66, 8.93)},
            {"name": "Ashtamudi Lake", "type": "lake", "bbox": (76.57, 8.87, 76.63, 8.91)},
        ],
        "Alappuzha (Alleppey)": [
            {"name": "Backwaters", "type": "river", "bbox": (76.28, 9.45, 76.4, 9.53)},
            {"name": "Vembanad Lake", "type": "lake", "bbox": (76.31, 9.47, 76.37, 9.51)},
            {"name": "Punnamada Lake", "type": "lake", "bbox": (76.31, 9.47, 76.37, 9.51)},
        ],
        "Palakkad": [
            {"name": "Bharathapuzha River", "type": "river", "bbox": (76.59, 10.74, 76.71, 10.82)},
        ],
        "Kottayam": [
            {"name": "Meenachil River", "type": "river", "bbox": (76.46, 9.55, 76.58, 9.63)},
        ],
        "Kannur": [
            {"name": "Valapattanam River", "type": "river", "bbox": (75.31, 11.83, 75.43, 11.91)},
        ],
        "Kasaragod": [
            {"name": "Chandragiri River", "type": "river", "bbox": (74.94, 12.46, 75.06, 12.54)},
        ],
        "Pathanamthitta": [
            {"name": "Pamba River", "type": "river", "bbox": (76.73, 9.23, 76.85, 9.31)},
            {"name": "Achankovil River", "type": "river", "bbox": (76.73, 9.23, 76.85, 9.31)},
        ],
        "Malappuram": [
            {"name": "Kadalundi River area", "type": "river", "bbox": (76.01, 11.0, 76.13, 11.08)},
        ],
        "Idukki": [
            {"name": "Periyar River", "type": "river", "bbox": (76.91, 9.81, 77.03, 9.89)},
        ],
        "Munnar": [
            {"name": "Muthirapuzha River", "type": "river", "bbox": (77.0, 10.05, 77.12, 10.13)},
            {"name": "tributary of Periyar", "type": "river", "bbox": (77.0, 10.05, 77.12, 10.13)},
        ],
        "Thodupuzha": [
            {"name": "Thodupuzha River", "type": "river", "bbox": (76.95, 8.5, 77.07, 8.58)},
            {"name": "Muvattupuzha tributary", "type": "river", "bbox": (76.95, 8.5, 77.07, 8.58)},
        ],
        "Attingal": [
            {"name": "Vamanapuram River", "type": "river", "bbox": (76.88, 8.53, 77.0, 8.61)},
        ],
        "Changanassery": [
            {"name": "Meenachil", "type": "river", "bbox": (76.94, 8.51, 77.06, 8.59)},
            {"name": "Manimala", "type": "river", "bbox": (76.94, 8.51, 77.06, 8.59)},
        ],
        "Tirur": [
            {"name": "Bharathapuzha River", "type": "river", "bbox": (76.87, 8.5, 76.99, 8.58)},
        ],
        "Ponnani": [
            {"name": "Bharathapuzha mouth", "type": "river", "bbox": (76.9, 8.57, 77.02, 8.65)},
        ],
        "Nilambur": [
            {"name": "Chaliyar River", "type": "river", "bbox": (76.86, 8.39, 76.98, 8.47)},
        ],
        "Sultanbathery": [
            {"name": "Kabini tributaries", "type": "river", "bbox": (76.93, 8.55, 77.05, 8.63)},
        ],
        "Mananthavady": [
            {"name": "Kabini tributaries", "type": "river", "bbox": (76.87, 8.51, 76.99, 8.59)},
        ],
        "Chalakudy": [
            {"name": "Chalakudy River", "type": "river", "bbox": (76.79, 8.53, 76.91, 8.61)},
        ],
        "Aluva": [
            {"name": "Periyar River", "type": "river", "bbox": (76.83, 8.47, 76.95, 8.55)},
        ],
        "Kodungallur": [
            {"name": "Periyar mouth", "type": "river", "bbox": (76.79, 8.53, 76.91, 8.61)},
        ],
        "Paravur": [
            {"name": "Paravur Lake", "type": "lake", "bbox": (76.84, 8.44, 76.9, 8.47)},
        ],
        "Kayamkulam": [
            {"name": "Kayamkulam Lake", "type": "lake", "bbox": (76.81, 8.46, 76.87, 8.5)},
        ],
        "Kumarakom": [
            {"name": "Vembanad Lake", "type": "lake", "bbox": (76.4, 9.6, 76.46, 9.64)},
        ],
        "Nedumangad": [
            {"name": "Vamanapuram River", "type": "river", "bbox": (76.84, 8.42, 76.96, 8.5)},
        ],
        "Neyyattinkara": [
            {"name": "Neyyar River", "type": "river", "bbox": (76.95, 8.48, 77.07, 8.56)},
        ],
        "Thekkady": [
            {"name": "Periyar Lake", "type": "lake", "bbox": (76.83, 8.46, 76.89, 8.5)},
            {"name": "River", "type": "river", "bbox": (76.8, 8.44, 76.92, 8.52)},
        ],
        "Adoor": [
            {"name": "Pamba basin", "type": "river", "bbox": (76.83, 8.45, 76.95, 8.53)},
        ],
        "Ranni": [
            {"name": "Pamba River", "type": "river", "bbox": (76.95, 8.43, 77.07, 8.51)},
        ],
        "Punalur": [
            {"name": "Kallada River", "type": "river", "bbox": (76.94, 8.44, 77.06, 8.52)},
        ],
        "Thiruvalla": [
            {"name": "Manimala River", "type": "river", "bbox": (76.97, 8.43, 77.09, 8.51)},
        ],
        "Chengannur": [
            {"name": "Pamba River", "type": "river", "bbox": (76.86, 8.52, 76.98, 8.6)},
        ],
        "Shornur": [
            {"name": "Bharathapuzha River", "type": "river", "bbox": (76.83, 8.51, 76.95, 8.59)},
        ],
        "Ottapalam": [
            {"name": "Bharathapuzha River", "type": "river", "bbox": (76.81, 8.39, 76.93, 8.47)},
        ],
        "Vadakara": [
            {"name": "Kuttiyadi River", "type": "river", "bbox": (76.97, 8.58, 77.09, 8.66)},
        ],
        "Thalassery": [
            {"name": "Anjarakandy River", "type": "river", "bbox": (76.89, 8.48, 77.01, 8.56)},
        ],
        "Mattannur": [
            {"name": "rivers", "type": "river", "bbox": (76.97, 8.47, 77.09, 8.55)},
        ],
        "Payyanur": [
            {"name": "Perumba River", "type": "river", "bbox": (76.89, 8.39, 77.01, 8.47)},
        ],
        "Manjeswaram": [
            {"name": "Manjeswaram River", "type": "river", "bbox": (76.8, 8.57, 76.92, 8.65)},
        ],
    },

    # -------------------------------------------------------------------------
    # 13. MADHYA PRADESH
    # -------------------------------------------------------------------------
    "Madhya Pradesh": {
        "Bhopal": [
            {"name": "Betwa basin", "type": "river", "bbox": (77.35, 23.22, 77.47, 23.3)},
            {"name": "Upper Lake", "type": "lake", "bbox": (77.38, 23.24, 77.44, 23.28)},
            {"name": "Bhojtal", "type": "lake", "bbox": (77.38, 23.24, 77.44, 23.28)},
            {"name": "Lower Lake", "type": "lake", "bbox": (77.38, 23.24, 77.44, 23.28)},
        ],
        "Indore": [
            {"name": "Khan River", "type": "river", "bbox": (75.8, 22.68, 75.92, 22.76)},
            {"name": "Saraswati River", "type": "river", "bbox": (75.8, 22.68, 75.92, 22.76)},
        ],
        "Jabalpur": [
            {"name": "Narmada River", "type": "river", "bbox": (79.89, 23.14, 80.01, 23.22)},
        ],
        "Gwalior": [
            {"name": "Chambal", "type": "river", "bbox": (78.12, 26.18, 78.24, 26.26)},
            {"name": "Sindh area", "type": "river", "bbox": (78.12, 26.18, 78.24, 26.26)},
        ],
        "Ujjain": [
            {"name": "Shipra River", "type": "river", "bbox": (75.71, 23.14, 75.83, 23.22)},
            {"name": "Kshipra", "type": "river", "bbox": (75.71, 23.14, 75.83, 23.22)},
        ],
        "Sagar": [
            {"name": "Dhasan", "type": "river", "bbox": (78.68, 23.8, 78.8, 23.88)},
            {"name": "Bina", "type": "river", "bbox": (78.68, 23.8, 78.8, 23.88)},
        ],
        "Rewa": [
            {"name": "Tamas River", "type": "river", "bbox": (81.24, 24.49, 81.36, 24.57)},
            {"name": "Tons", "type": "river", "bbox": (81.24, 24.49, 81.36, 24.57)},
            {"name": "Beehar River", "type": "river", "bbox": (81.24, 24.49, 81.36, 24.57)},
        ],
        "Satna": [
            {"name": "Tamas River", "type": "river", "bbox": (80.77, 24.54, 80.89, 24.62)},
            {"name": "Tons", "type": "river", "bbox": (80.77, 24.54, 80.89, 24.62)},
        ],
        "Narmadapuram (Hoshangabad)": [
            {"name": "Narmada River", "type": "river", "bbox": (77.44, 23.32, 77.56, 23.4)},
        ],
        "Khandwa (East Nimar)": [
            {"name": "Narmada", "type": "river", "bbox": (76.29, 21.78, 76.41, 21.86)},
        ],
        "Vidisha": [
            {"name": "Betwa River", "type": "river", "bbox": (77.75, 23.49, 77.87, 23.57)},
        ],
        "Mandsaur": [
            {"name": "Shivna River", "type": "river", "bbox": (75.01, 24.03, 75.13, 24.11)},
        ],
        "Ratlam": [
            {"name": "Chambal tributaries", "type": "river", "bbox": (77.37, 23.25, 77.49, 23.33)},
        ],
        "Dewas": [
            {"name": "Kshipra tributaries", "type": "river", "bbox": (75.99, 22.93, 76.11, 23.01)},
        ],
        "Shivpuri": [
            {"name": "Sindh River", "type": "river", "bbox": (77.6, 25.39, 77.72, 25.47)},
        ],
        "Chhatarpur": [
            {"name": "Ken River area", "type": "river", "bbox": (79.53, 24.87, 79.65, 24.95)},
        ],
        "Panna": [
            {"name": "Ken River", "type": "river", "bbox": (80.13, 24.68, 80.25, 24.76)},
        ],
        "Orchha": [
            {"name": "Betwa River", "type": "river", "bbox": (78.58, 25.31, 78.7, 25.39)},
        ],
        "Omkareshwar": [
            {"name": "Narmada River", "type": "river", "bbox": (76.09, 22.2, 76.21, 22.28)},
        ],
        "Maheshwar": [
            {"name": "Narmada River", "type": "river", "bbox": (75.53, 22.14, 75.65, 22.22)},
        ],
        "Mandla": [
            {"name": "Narmada River", "type": "river", "bbox": (80.32, 22.56, 80.44, 22.64)},
        ],
        "Amarkantak": [
            {"name": "Narmada", "type": "river", "bbox": (77.27, 23.31, 77.39, 23.39)},
            {"name": "origin", "type": "river", "bbox": (77.27, 23.31, 77.39, 23.39)},
            {"name": "Son", "type": "river", "bbox": (77.27, 23.31, 77.39, 23.39)},
        ],
        "Burhanpur": [
            {"name": "Tapti River", "type": "river", "bbox": (76.17, 21.27, 76.29, 21.35)},
        ],
        "Seoni": [
            {"name": "Wainganga River", "type": "river", "bbox": (79.48, 22.05, 79.6, 22.13)},
        ],
        "Damoh": [
            {"name": "Sindh tributaries", "type": "river", "bbox": (79.38, 23.8, 79.5, 23.88)},
        ],
        "Chhindwara": [
            {"name": "Kanhan River", "type": "river", "bbox": (78.88, 22.02, 79.0, 22.1)},
        ],
        "Balaghat": [
            {"name": "Wainganga", "type": "river", "bbox": (80.13, 21.77, 80.25, 21.85)},
        ],
        "Morena": [
            {"name": "Chambal", "type": "river", "bbox": (77.38, 23.32, 77.5, 23.4)},
        ],
        "Bhind": [
            {"name": "Chambal", "type": "river", "bbox": (77.27, 23.26, 77.39, 23.34)},
        ],
        "Datia": [
            {"name": "Sindh", "type": "river", "bbox": (78.4, 25.63, 78.52, 25.71)},
        ],
        "Tikamgarh": [
            {"name": "Betwa tributaries", "type": "river", "bbox": (78.77, 24.7, 78.89, 24.78)},
        ],
        "Neemuch": [
            {"name": "Chambal area", "type": "river", "bbox": (74.81, 24.43, 74.93, 24.51)},
        ],
        "Shajapur": [
            {"name": "Parbati", "type": "river", "bbox": (76.21, 23.39, 76.33, 23.47)},
        ],
        "Dhar": [
            {"name": "Narmada tributaries", "type": "river", "bbox": (75.24, 22.56, 75.36, 22.64)},
        ],
        "Jhabua": [
            {"name": "Mahi", "type": "river", "bbox": (77.27, 23.18, 77.39, 23.26)},
            {"name": "Narmada area", "type": "river", "bbox": (77.27, 23.18, 77.39, 23.26)},
        ],
        "Barwani": [
            {"name": "Narmada River", "type": "river", "bbox": (74.84, 22.0, 74.96, 22.08)},
        ],
        "Khargone (West Nimar)": [
            {"name": "Narmada", "type": "river", "bbox": (75.56, 21.79, 75.68, 21.87)},
        ],
        "Betul": [
            {"name": "Tapti tributaries", "type": "river", "bbox": (77.84, 21.87, 77.96, 21.95)},
        ],
        "Raisen": [
            {"name": "Betwa", "type": "river", "bbox": (77.73, 23.29, 77.85, 23.37)},
        ],
        "Narsinghpur": [
            {"name": "Narmada River", "type": "river", "bbox": (79.13, 22.91, 79.25, 22.99)},
        ],
        "Katni": [
            {"name": "Katni River", "type": "river", "bbox": (80.33, 23.79, 80.45, 23.87)},
            {"name": "tributary of Son", "type": "river", "bbox": (80.33, 23.79, 80.45, 23.87)},
        ],
        "Umaria": [
            {"name": "Son", "type": "river", "bbox": (77.44, 23.15, 77.56, 23.23)},
            {"name": "Tamas", "type": "river", "bbox": (77.44, 23.15, 77.56, 23.23)},
        ],
        "Shahdol": [
            {"name": "Son", "type": "river", "bbox": (77.35, 23.13, 77.47, 23.21)},
        ],
        "Anuppur": [
            {"name": "Narmada", "type": "river", "bbox": (81.63, 23.06, 81.75, 23.14)},
            {"name": "Son origin area", "type": "river", "bbox": (81.63, 23.06, 81.75, 23.14)},
        ],
        "Dindori": [
            {"name": "Narmada", "type": "river", "bbox": (77.28, 23.14, 77.4, 23.22)},
        ],
        "Harda": [
            {"name": "Narmada River", "type": "river", "bbox": (77.04, 22.3, 77.16, 22.38)},
        ],
        "Sehore": [
            {"name": "Parbati", "type": "river", "bbox": (77.44, 23.29, 77.56, 23.37)},
        ],
        "Ashok Nagar": [
            {"name": "Sindh", "type": "river", "bbox": (77.33, 23.28, 77.45, 23.36)},
        ],
        "Guna": [
            {"name": "Parbati", "type": "river", "bbox": (77.25, 23.29, 77.37, 23.37)},
            {"name": "Sindh", "type": "river", "bbox": (77.25, 23.29, 77.37, 23.37)},
        ],
        "Alirajpur": [
            {"name": "Narmada", "type": "river", "bbox": (74.3, 22.27, 74.42, 22.35)},
        ],
        "Singrauli": [
            {"name": "Son", "type": "river", "bbox": (82.61, 24.16, 82.73, 24.24)},
            {"name": "Rihand", "type": "river", "bbox": (82.61, 24.16, 82.73, 24.24)},
        ],
        "Maihar": [
            {"name": "Tamas", "type": "river", "bbox": (80.7, 24.22, 80.82, 24.3)},
        ],
        "Pachmarhi": [
            {"name": "Denwa River", "type": "river", "bbox": (77.44, 23.14, 77.56, 23.22)},
        ],
        "Sanchi": [
            {"name": "Betwa area", "type": "river", "bbox": (77.4, 23.13, 77.52, 23.21)},
        ],
        "Bhedaghat": [
            {"name": "Narmada River", "type": "river", "bbox": (77.45, 23.24, 77.57, 23.32)},
            {"name": "Marble Rocks", "type": "river", "bbox": (77.45, 23.24, 77.57, 23.32)},
        ],
    },

    # -------------------------------------------------------------------------
    # 14. MAHARASHTRA
    # -------------------------------------------------------------------------
    "Maharashtra": {
        "Mumbai": [
            {"name": "Mithi River", "type": "river", "bbox": (72.82, 19.04, 72.94, 19.12)},
            {"name": "Ulhas River", "type": "river", "bbox": (72.82, 19.04, 72.94, 19.12)},
            {"name": "Powai Lake", "type": "lake", "bbox": (72.85, 19.06, 72.91, 19.1)},
            {"name": "Vihar Lake", "type": "lake", "bbox": (72.85, 19.06, 72.91, 19.1)},
            {"name": "Tulsi Lake", "type": "lake", "bbox": (72.85, 19.06, 72.91, 19.1)},
        ],
        "Pune": [
            {"name": "Mula-Mutha River", "type": "river", "bbox": (73.8, 18.48, 73.92, 18.56)},
            {"name": "Pavana River", "type": "river", "bbox": (73.8, 18.48, 73.92, 18.56)},
            {"name": "Khadakwasla", "type": "river", "bbox": (73.8, 18.48, 73.92, 18.56)},
            {"name": "Pashan Lake", "type": "lake", "bbox": (73.83, 18.5, 73.89, 18.54)},
        ],
        "Nagpur": [
            {"name": "Nag River", "type": "river", "bbox": (79.03, 21.11, 79.15, 21.19)},
            {"name": "Gorewada Lake", "type": "lake", "bbox": (79.06, 21.13, 79.12, 21.17)},
            {"name": "Ambazari Lake", "type": "lake", "bbox": (79.06, 21.13, 79.12, 21.17)},
            {"name": "Futala Lake", "type": "lake", "bbox": (79.06, 21.13, 79.12, 21.17)},
        ],
        "Nashik": [
            {"name": "Godavari River", "type": "river", "bbox": (73.73, 19.95, 73.85, 20.03)},
            {"name": "origin at Trimbakeshwar", "type": "river", "bbox": (73.73, 19.95, 73.85, 20.03)},
        ],
        "Chhatrapati Sambhajinagar (Aurangabad)": [
            {"name": "Kham River", "type": "river", "bbox": (72.88, 19.02, 73.0, 19.1)},
            {"name": "Salim Ali Lake", "type": "lake", "bbox": (72.91, 19.04, 72.97, 19.08)},
        ],
        "Kolhapur": [
            {"name": "Panchganga River", "type": "river", "bbox": (74.18, 16.66, 74.3, 16.74)},
            {"name": "Rankala Lake", "type": "lake", "bbox": (74.21, 16.68, 74.27, 16.72)},
        ],
        "Solapur": [
            {"name": "Bhima River", "type": "river", "bbox": (75.85, 17.64, 75.97, 17.72)},
            {"name": "Sina River", "type": "river", "bbox": (75.85, 17.64, 75.97, 17.72)},
        ],
        "Satara": [
            {"name": "Krishna River", "type": "river", "bbox": (73.94, 17.64, 74.06, 17.72)},
        ],
        "Sangli": [
            {"name": "Krishna River", "type": "river", "bbox": (74.51, 16.81, 74.63, 16.89)},
        ],
        "Nanded": [
            {"name": "Godavari River", "type": "river", "bbox": (77.25, 19.12, 77.37, 19.2)},
        ],
        "Ratnagiri": [
            {"name": "Kajali River", "type": "river", "bbox": (73.24, 16.95, 73.36, 17.03)},
        ],
        "Amravati": [
            {"name": "Wardha River", "type": "river", "bbox": (77.69, 20.89, 77.81, 20.97)},
        ],
        "Akola": [
            {"name": "Morna River", "type": "river", "bbox": (76.94, 20.67, 77.06, 20.75)},
            {"name": "Purna River", "type": "river", "bbox": (76.94, 20.67, 77.06, 20.75)},
        ],
        "Chandrapur": [
            {"name": "Wardha River", "type": "river", "bbox": (79.24, 19.91, 79.36, 19.99)},
            {"name": "Erai River", "type": "river", "bbox": (79.24, 19.91, 79.36, 19.99)},
        ],
        "Jalgaon": [
            {"name": "Tapi River", "type": "river", "bbox": (75.5, 20.97, 75.62, 21.05)},
        ],
        "Dhule": [
            {"name": "Tapi River", "type": "river", "bbox": (74.72, 20.86, 74.84, 20.94)},
            {"name": "Panzara River", "type": "river", "bbox": (74.72, 20.86, 74.84, 20.94)},
        ],
        "Latur": [
            {"name": "Manjira", "type": "river", "bbox": (76.51, 18.36, 76.63, 18.44)},
        ],
        "Beed": [
            {"name": "Bindusara", "type": "river", "bbox": (75.7, 18.95, 75.82, 19.03)},
            {"name": "Godavari tributary", "type": "river", "bbox": (75.7, 18.95, 75.82, 19.03)},
        ],
        "Parbhani": [
            {"name": "Godavari", "type": "river", "bbox": (76.72, 19.23, 76.84, 19.31)},
            {"name": "Purna River", "type": "river", "bbox": (76.72, 19.23, 76.84, 19.31)},
        ],
        "Wardha": [
            {"name": "Wardha River", "type": "river", "bbox": (78.54, 20.7, 78.66, 20.78)},
        ],
        "Gondia": [
            {"name": "Wainganga", "type": "river", "bbox": (80.14, 21.42, 80.26, 21.5)},
        ],
        "Bhandara": [
            {"name": "Wainganga River", "type": "river", "bbox": (79.59, 21.13, 79.71, 21.21)},
        ],
        "Hingoli": [
            {"name": "Penganga", "type": "river", "bbox": (77.09, 19.68, 77.21, 19.76)},
            {"name": "Purna", "type": "river", "bbox": (77.09, 19.68, 77.21, 19.76)},
        ],
        "Dharashiv (Osmanabad)": [
            {"name": "Terna", "type": "river", "bbox": (72.89, 18.96, 73.01, 19.04)},
        ],
        "Washim": [
            {"name": "Penganga", "type": "river", "bbox": (77.07, 20.07, 77.19, 20.15)},
            {"name": "Adan", "type": "river", "bbox": (77.07, 20.07, 77.19, 20.15)},
        ],
        "Buldhana": [
            {"name": "Penganga area", "type": "river", "bbox": (76.12, 20.49, 76.24, 20.57)},
            {"name": "Lonar Lake nearby", "type": "lake", "bbox": (76.15, 20.51, 76.21, 20.55)},
        ],
        "Yavatmal": [
            {"name": "Wardha", "type": "river", "bbox": (78.06, 20.35, 78.18, 20.43)},
            {"name": "Penganga", "type": "river", "bbox": (78.06, 20.35, 78.18, 20.43)},
        ],
        "Nandurbar": [
            {"name": "Tapi River", "type": "river", "bbox": (72.85, 19.09, 72.97, 19.17)},
        ],
        "Pandharpur": [
            {"name": "Bhima River", "type": "river", "bbox": (75.27, 17.64, 75.39, 17.72)},
            {"name": "Chandrabhaga", "type": "river", "bbox": (75.27, 17.64, 75.39, 17.72)},
        ],
        "Mahabaleshwar": [
            {"name": "Krishna River origin", "type": "river", "bbox": (73.6, 17.89, 73.72, 17.97)},
            {"name": "Venna Lake", "type": "lake", "bbox": (73.63, 17.91, 73.69, 17.95)},
        ],
        "Trimbakeshwar": [
            {"name": "Godavari River", "type": "river", "bbox": (73.47, 19.9, 73.59, 19.98)},
            {"name": "origin", "type": "river", "bbox": (73.47, 19.9, 73.59, 19.98)},
        ],
        "Paithan": [
            {"name": "Godavari River", "type": "river", "bbox": (72.87, 19.08, 72.99, 19.16)},
            {"name": "Jayakwadi Dam", "type": "lake", "bbox": (72.9, 19.1, 72.96, 19.14)},
        ],
        "Baramati": [
            {"name": "Nira River", "type": "river", "bbox": (72.87, 18.98, 72.99, 19.06)},
        ],
        "Sinnar": [
            {"name": "Godavari", "type": "river", "bbox": (72.91, 18.97, 73.03, 19.05)},
        ],
        "Igatpuri": [
            {"name": "Godavari tributaries", "type": "river", "bbox": (72.89, 19.11, 73.01, 19.19)},
        ],
        "Lonavala": [
            {"name": "Indrayani", "type": "river", "bbox": (73.35, 18.71, 73.47, 18.79)},
            {"name": "Pavana", "type": "river", "bbox": (73.35, 18.71, 73.47, 18.79)},
        ],
        "Panchgani": [
            {"name": "Krishna tributaries", "type": "river", "bbox": (73.74, 17.89, 73.86, 17.97)},
        ],
        "Wai": [
            {"name": "Krishna River", "type": "river", "bbox": (72.75, 19.07, 72.87, 19.15)},
        ],
        "Karad": [
            {"name": "Krishna-Koyna confluence", "type": "river", "bbox": (72.81, 19.13, 72.93, 19.21)},
        ],
        "Miraj": [
            {"name": "Krishna", "type": "river", "bbox": (72.73, 19.04, 72.85, 19.12)},
        ],
        "Ichalkaranji": [
            {"name": "Panchganga River", "type": "river", "bbox": (72.84, 19.08, 72.96, 19.16)},
        ],
        "Chiplun": [
            {"name": "Vashishti River", "type": "river", "bbox": (72.81, 19.06, 72.93, 19.14)},
        ],
        "Bhusawal": [
            {"name": "Tapi", "type": "river", "bbox": (72.72, 19.09, 72.84, 19.17)},
        ],
        "Amalner": [
            {"name": "Bori River", "type": "river", "bbox": (72.78, 18.97, 72.9, 19.05)},
        ],
        "Pachora": [
            {"name": "Girna", "type": "river", "bbox": (72.89, 19.08, 73.01, 19.16)},
        ],
        "Ahmednagar": [
            {"name": "Sina River", "type": "river", "bbox": (74.68, 19.05, 74.8, 19.13)},
            {"name": "Bhima basin", "type": "river", "bbox": (74.68, 19.05, 74.8, 19.13)},
        ],
        "Shrirampur": [
            {"name": "Godavari", "type": "river", "bbox": (72.73, 19.05, 72.85, 19.13)},
            {"name": "Pravara", "type": "river", "bbox": (72.73, 19.05, 72.85, 19.13)},
        ],
        "Kopargaon": [
            {"name": "Godavari River", "type": "river", "bbox": (72.82, 19.04, 72.94, 19.12)},
        ],
        "Sangamner": [
            {"name": "Pravara River", "type": "river", "bbox": (72.84, 18.98, 72.96, 19.06)},
        ],
        "Shegaon": [
            {"name": "Morna", "type": "river", "bbox": (72.76, 19.07, 72.88, 19.15)},
        ],
        "Gadchiroli": [
            {"name": "Pranhita", "type": "river", "bbox": (79.94, 20.14, 80.06, 20.22)},
            {"name": "Indravati", "type": "river", "bbox": (79.94, 20.14, 80.06, 20.22)},
        ],
        "Bramhapuri": [
            {"name": "Wainganga", "type": "river", "bbox": (72.78, 19.11, 72.9, 19.19)},
        ],
        "Ballarpur": [
            {"name": "Wardha", "type": "river", "bbox": (72.73, 19.13, 72.85, 19.21)},
        ],
        "Pusad": [
            {"name": "Penganga River", "type": "river", "bbox": (72.83, 18.96, 72.95, 19.04)},
        ],
        "Umarkhed": [
            {"name": "Penganga", "type": "river", "bbox": (72.76, 18.96, 72.88, 19.04)},
        ],
        "Kinwat": [
            {"name": "Penganga", "type": "river", "bbox": (72.87, 19.05, 72.99, 19.13)},
        ],
        "Gangakhed": [
            {"name": "Godavari River", "type": "river", "bbox": (72.76, 19.06, 72.88, 19.14)},
        ],
        "Kalyan-Dombivli": [
            {"name": "Ulhas River", "type": "river", "bbox": (72.81, 18.95, 72.93, 19.03)},
        ],
        "Thane": [
            {"name": "Thane Creek", "type": "river", "bbox": (72.92, 19.18, 73.04, 19.26)},
            {"name": "Upvan Lake", "type": "lake", "bbox": (72.95, 19.2, 73.01, 19.24)},
            {"name": "Masunda Lake", "type": "lake", "bbox": (72.95, 19.2, 73.01, 19.24)},
        ],
        "Vasai-Virar": [
            {"name": "Vaitarna River", "type": "river", "bbox": (72.82, 19.03, 72.94, 19.11)},
        ],
        "Bhiwandi": [
            {"name": "Kamvari River", "type": "river", "bbox": (72.84, 19.1, 72.96, 19.18)},
        ],
        "Navi Mumbai": [
            {"name": "Panvel Creek", "type": "river", "bbox": (72.73, 18.96, 72.85, 19.04)},
        ],
    },

    # -------------------------------------------------------------------------
    # 15. MANIPUR
    # -------------------------------------------------------------------------
    "Manipur": {
        "Imphal": [
            {"name": "Imphal River", "type": "river", "bbox": (93.88, 24.77, 94.0, 24.85)},
            {"name": "Nambul River", "type": "river", "bbox": (93.88, 24.77, 94.0, 24.85)},
        ],
        "Thoubal": [
            {"name": "Thoubal River", "type": "river", "bbox": (93.95, 24.59, 94.07, 24.67)},
        ],
        "Bishnupur": [
            {"name": "Loktak Lake", "type": "lake", "bbox": (93.75, 24.61, 93.81, 24.65)},
            {"name": "Nambol River", "type": "river", "bbox": (93.72, 24.59, 93.84, 24.67)},
        ],
        "Churachandpur": [
            {"name": "Khuga River", "type": "river", "bbox": (93.62, 24.29, 93.74, 24.37)},
        ],
        "Senapati": [
            {"name": "Barak tributaries", "type": "river", "bbox": (93.96, 25.23, 94.08, 25.31)},
        ],
        "Ukhrul": [
            {"name": "Thoubal headwaters", "type": "river", "bbox": (94.31, 25.08, 94.43, 25.16)},
        ],
        "Chandel": [
            {"name": "rivers", "type": "river", "bbox": (93.98, 24.28, 94.1, 24.36)},
        ],
        "Tamenglong": [
            {"name": "Barak tributaries", "type": "river", "bbox": (93.45, 24.94, 93.57, 25.02)},
        ],
        "Jiribam": [
            {"name": "Barak River", "type": "river", "bbox": (93.06, 24.75, 93.18, 24.83)},
            {"name": "Jiri River", "type": "river", "bbox": (93.06, 24.75, 93.18, 24.83)},
        ],
        "Moirang": [
            {"name": "Loktak Lake", "type": "lake", "bbox": (93.74, 24.47, 93.8, 24.51)},
        ],
        "Kakching": [
            {"name": "Sekmai River", "type": "river", "bbox": (93.99, 24.46, 94.11, 24.54)},
        ],
        "Kangpokpi": [
            {"name": "Iril headwaters", "type": "river", "bbox": (93.8, 24.67, 93.92, 24.75)},
        ],
        "Moreh": [
            {"name": "Tiau River area", "type": "river", "bbox": (94.24, 24.21, 94.36, 24.29)},
        ],
        "Nambol": [
            {"name": "Nambol River", "type": "river", "bbox": (93.91, 24.84, 94.03, 24.92)},
        ],
    },

    # -------------------------------------------------------------------------
    # 16. MEGHALAYA
    # -------------------------------------------------------------------------
    "Meghalaya": {
        "Shillong": [
            {"name": "Umkhrah River", "type": "river", "bbox": (91.82, 25.53, 91.94, 25.61)},
            {"name": "Umshyrpi River", "type": "river", "bbox": (91.82, 25.53, 91.94, 25.61)},
            {"name": "Ward's Lake", "type": "lake", "bbox": (91.85, 25.55, 91.91, 25.59)},
        ],
        "Tura": [
            {"name": "Simsang River", "type": "river", "bbox": (90.16, 25.47, 90.28, 25.55)},
        ],
        "Cherrapunji (Sohra)": [
            {"name": "many streams and waterfalls", "type": "river", "bbox": (91.64, 25.26, 91.76, 25.34)},
        ],
        "Jowai": [
            {"name": "Myntdu River", "type": "river", "bbox": (92.14, 25.41, 92.26, 25.49)},
        ],
        "Nongpoh": [
            {"name": "Umiam River", "type": "river", "bbox": (91.82, 25.86, 91.94, 25.94)},
        ],
        "Nongstoin": [
            {"name": "Kynshi River", "type": "river", "bbox": (91.2, 25.48, 91.32, 25.56)},
        ],
        "Baghmara": [
            {"name": "Simsang", "type": "river", "bbox": (90.57, 25.18, 90.69, 25.26)},
        ],
        "Williamnagar": [
            {"name": "Simsang River", "type": "river", "bbox": (90.56, 25.46, 90.68, 25.54)},
        ],
        "Dawki": [
            {"name": "Umngot River", "type": "river", "bbox": (91.96, 25.15, 92.08, 25.23)},
        ],
        "Mairang": [
            {"name": "Umiam", "type": "river", "bbox": (91.5, 25.51, 91.62, 25.59)},
        ],
        "Mawkyrwat": [
            {"name": "Kynshi", "type": "river", "bbox": (91.92, 25.49, 92.04, 25.57)},
        ],
        "Resubelpara": [
            {"name": "Simsang tributaries", "type": "river", "bbox": (90.56, 25.83, 90.68, 25.91)},
        ],
        "Khliehriat": [
            {"name": "Kopili headwaters", "type": "river", "bbox": (91.72, 25.45, 91.84, 25.53)},
        ],
    },

    # -------------------------------------------------------------------------
    # 17. MIZORAM
    # -------------------------------------------------------------------------
    "Mizoram": {
        "Aizawl": [
            {"name": "Tlawng River", "type": "river", "bbox": (92.66, 23.69, 92.78, 23.77)},
        ],
        "Lunglei": [
            {"name": "Tlawng River", "type": "river", "bbox": (92.69, 22.84, 92.81, 22.92)},
        ],
        "Champhai": [
            {"name": "Tiau River", "type": "river", "bbox": (93.27, 23.42, 93.39, 23.5)},
        ],
        "Serchhip": [
            {"name": "Tuikum River", "type": "river", "bbox": (92.79, 23.26, 92.91, 23.34)},
        ],
        "Kolasib": [
            {"name": "Tlawng River", "type": "river", "bbox": (92.62, 24.18, 92.74, 24.26)},
        ],
        "Lawngtlai": [
            {"name": "Chhimtuipui River", "type": "river", "bbox": (92.84, 22.49, 92.96, 22.57)},
        ],
        "Saiha (Siaha)": [
            {"name": "Chhimtuipui River", "type": "river", "bbox": (92.92, 22.45, 93.04, 22.53)},
        ],
        "Mamit": [
            {"name": "Tlawng tributaries", "type": "river", "bbox": (92.43, 23.88, 92.55, 23.96)},
        ],
        "Khawzawl": [
            {"name": "Tuivawl River", "type": "river", "bbox": (93.09, 23.31, 93.21, 23.39)},
        ],
        "Hnahthial": [
            {"name": "Mat River", "type": "river", "bbox": (92.7, 22.59, 92.82, 22.67)},
        ],
        "Saitual": [
            {"name": "Tuirial River", "type": "river", "bbox": (92.86, 23.75, 92.98, 23.83)},
        ],
    },

    # -------------------------------------------------------------------------
    # 18. NAGALAND
    # -------------------------------------------------------------------------
    "Nagaland": {
        "Kohima": [
            {"name": "Dzukou streams", "type": "river", "bbox": (94.05, 25.63, 94.17, 25.71)},
        ],
        "Dimapur": [
            {"name": "Dhansiri River", "type": "river", "bbox": (93.67, 25.86, 93.79, 25.94)},
        ],
        "Mokokchung": [
            {"name": "Dikhu", "type": "river", "bbox": (94.46, 26.28, 94.58, 26.36)},
            {"name": "Milak", "type": "river", "bbox": (94.46, 26.28, 94.58, 26.36)},
        ],
        "Wokha": [
            {"name": "Doyang River", "type": "river", "bbox": (94.21, 26.06, 94.33, 26.14)},
        ],
        "Zunheboto": [
            {"name": "Tizu", "type": "river", "bbox": (94.46, 25.93, 94.58, 26.01)},
            {"name": "Doyang", "type": "river", "bbox": (94.46, 25.93, 94.58, 26.01)},
        ],
        "Tuensang": [
            {"name": "Dikhu", "type": "river", "bbox": (94.77, 26.23, 94.89, 26.31)},
        ],
        "Mon": [
            {"name": "Dikhu headwaters", "type": "river", "bbox": (94.86, 26.71, 94.98, 26.79)},
        ],
        "Phek": [
            {"name": "rivers", "type": "river", "bbox": (94.41, 25.63, 94.53, 25.71)},
        ],
        "Peren": [
            {"name": "Dhansiri", "type": "river", "bbox": (93.68, 25.48, 93.8, 25.56)},
        ],
        "Kiphire": [
            {"name": "Tizu", "type": "river", "bbox": (94.91, 25.84, 95.03, 25.92)},
        ],
        "Longleng": [
            {"name": "Dikhu", "type": "river", "bbox": (94.81, 26.38, 94.93, 26.46)},
        ],
        "Chumukedima": [
            {"name": "Dhansiri River", "type": "river", "bbox": (94.0, 25.61, 94.12, 25.69)},
        ],
    },

    # -------------------------------------------------------------------------
    # 19. ODISHA
    # -------------------------------------------------------------------------
    "Odisha": {
        "Bhubaneswar": [
            {"name": "Daya River", "type": "river", "bbox": (85.76, 20.26, 85.88, 20.34)},
            {"name": "Kuakhai River", "type": "river", "bbox": (85.76, 20.26, 85.88, 20.34)},
        ],
        "Cuttack": [
            {"name": "Mahanadi River", "type": "river", "bbox": (85.82, 20.42, 85.94, 20.5)},
            {"name": "Kathajodi River", "type": "river", "bbox": (85.82, 20.42, 85.94, 20.5)},
        ],
        "Sambalpur": [
            {"name": "Mahanadi River", "type": "river", "bbox": (83.91, 21.43, 84.03, 21.51)},
            {"name": "Hirakud Dam", "type": "lake", "bbox": (83.94, 21.45, 84.0, 21.49)},
        ],
        "Berhampur (Brahmapur)": [
            {"name": "Rushikulya River", "type": "river", "bbox": (84.73, 19.27, 84.85, 19.35)},
        ],
        "Rourkela": [
            {"name": "Brahmani River", "type": "river", "bbox": (84.79, 22.22, 84.91, 22.3)},
            {"name": "Koel + Sankh confluence", "type": "river", "bbox": (84.79, 22.22, 84.91, 22.3)},
        ],
        "Balasore (Baleshwar)": [
            {"name": "Budhabalanga River", "type": "river", "bbox": (86.87, 21.45, 86.99, 21.53)},
        ],
        "Puri": [
            {"name": "small rivers", "type": "river", "bbox": (85.77, 19.77, 85.89, 19.85)},
        ],
        "Jeypore": [
            {"name": "Kolab River", "type": "river", "bbox": (82.51, 18.82, 82.63, 18.9)},
        ],
        "Jharsuguda": [
            {"name": "Ib River", "type": "river", "bbox": (83.95, 21.82, 84.07, 21.9)},
        ],
        "Angul": [
            {"name": "Brahmani", "type": "river", "bbox": (85.04, 20.8, 85.16, 20.88)},
        ],
        "Baripada": [
            {"name": "Budhabalanga River", "type": "river", "bbox": (86.67, 21.89, 86.79, 21.97)},
        ],
        "Koraput": [
            {"name": "Kolab River", "type": "river", "bbox": (82.65, 18.77, 82.77, 18.85)},
        ],
        "Dhenkanal": [
            {"name": "Brahmani", "type": "river", "bbox": (85.54, 20.62, 85.66, 20.7)},
        ],
        "Kendrapara": [
            {"name": "Mahanadi Delta", "type": "river", "bbox": (86.36, 20.46, 86.48, 20.54)},
        ],
        "Paradip": [
            {"name": "Mahanadi River mouth", "type": "river", "bbox": (86.55, 20.28, 86.67, 20.36)},
        ],
        "Barbil": [
            {"name": "Koel River", "type": "river", "bbox": (85.76, 20.19, 85.88, 20.27)},
        ],
        "Sundargarh": [
            {"name": "Ib River", "type": "river", "bbox": (83.98, 22.08, 84.1, 22.16)},
        ],
        "Rayagada": [
            {"name": "Nagavali River", "type": "river", "bbox": (83.36, 19.13, 83.48, 19.21)},
        ],
        "Bolangir (Balangir)": [
            {"name": "Tel River", "type": "river", "bbox": (85.7, 20.28, 85.82, 20.36)},
        ],
        "Bhawanipatna": [
            {"name": "Indravati tributaries", "type": "river", "bbox": (85.69, 20.33, 85.81, 20.41)},
        ],
        "Jajpur": [
            {"name": "Baitarani River", "type": "river", "bbox": (85.68, 20.24, 85.8, 20.32)},
        ],
        "Keonjhar (Kendujhar)": [
            {"name": "Baitarani River", "type": "river", "bbox": (85.75, 20.22, 85.87, 20.3)},
        ],
        "Bargarh": [
            {"name": "Mahanadi", "type": "river", "bbox": (83.56, 21.29, 83.68, 21.37)},
        ],
        "Bhadrak": [
            {"name": "Salandi", "type": "river", "bbox": (85.79, 20.22, 85.91, 20.3)},
            {"name": "Baitarani", "type": "river", "bbox": (85.79, 20.22, 85.91, 20.3)},
        ],
        "Sonepur (Subarnapur)": [
            {"name": "Mahanadi-Tel confluence", "type": "river", "bbox": (85.12, 25.66, 85.24, 25.74)},
        ],
        "Phulbani": [
            {"name": "Salunki River", "type": "river", "bbox": (85.72, 20.27, 85.84, 20.35)},
        ],
        "Nayagarh": [
            {"name": "Mahanadi tributaries", "type": "river", "bbox": (85.04, 20.09, 85.16, 20.17)},
        ],
        "Boudh": [
            {"name": "Mahanadi River", "type": "river", "bbox": (84.26, 20.8, 84.38, 20.88)},
        ],
        "Nuapada": [
            {"name": "Jonk River", "type": "river", "bbox": (85.69, 20.19, 85.81, 20.27)},
        ],
        "Malkangiri": [
            {"name": "Sabari", "type": "river", "bbox": (81.82, 18.31, 81.94, 18.39)},
            {"name": "Kolab", "type": "river", "bbox": (81.82, 18.31, 81.94, 18.39)},
        ],
        "Nabarangpur": [
            {"name": "Indravati", "type": "river", "bbox": (82.49, 19.19, 82.61, 19.27)},
        ],
        "Titlagarh": [
            {"name": "Tel River", "type": "river", "bbox": (85.67, 20.33, 85.79, 20.41)},
        ],
        "Talcher": [
            {"name": "Brahmani River", "type": "river", "bbox": (85.68, 20.33, 85.8, 20.41)},
        ],
        "Rajgangpur": [
            {"name": "Brahmani", "type": "river", "bbox": (85.68, 20.29, 85.8, 20.37)},
            {"name": "Koel", "type": "river", "bbox": (85.68, 20.29, 85.8, 20.37)},
        ],
        "Chhatrapur": [
            {"name": "Rushikulya", "type": "river", "bbox": (85.79, 20.2, 85.91, 20.28)},
        ],
        "Gopalpur": [
            {"name": "Rushikulya mouth", "type": "river", "bbox": (85.72, 20.35, 85.84, 20.43)},
        ],
    },

    # -------------------------------------------------------------------------
    # 20. PUNJAB
    # -------------------------------------------------------------------------
    "Punjab": {
        "Amritsar": [
            {"name": "Ravi River",            "type": "river", "bbox": (74.75, 31.58, 74.98, 31.72)},
            {"name": "Amrit Sarovar",         "type": "lake",  "bbox": (74.870, 31.618, 74.882, 31.626)},
        ],
        "Ludhiana": [
            {"name": "Sutlej River",          "type": "river", "bbox": (75.72, 30.82, 75.96, 30.96)},
            {"name": "Buddha Dariya",         "type": "river", "bbox": (75.80, 30.88, 75.94, 30.95)},
        ],
        "Jalandhar": [
            {"name": "Beas River",            "type": "river", "bbox": (75.36, 31.26, 75.56, 31.44)},
            {"name": "Kali Bein",             "type": "river", "bbox": (75.16, 31.42, 75.24, 31.50)},
        ],
        "Patiala": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (76.20, 30.22, 76.50, 30.42)},
            {"name": "Sirhind Canal",         "type": "river", "bbox": (76.30, 30.28, 76.46, 30.38)},
        ],
        "Bathinda": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (74.85, 30.12, 75.06, 30.28)},
            {"name": "Sirhind Feeder Canal",  "type": "river", "bbox": (74.90, 30.15, 75.02, 30.25)},
        ],
        "Mohali (SAS Nagar)": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (76.60, 30.64, 76.82, 30.78)},
            {"name": "Sukhna Lake",           "type": "lake",  "bbox": (76.814, 30.742, 76.840, 30.758)},
        ],
        "Pathankot": [
            {"name": "Ravi River",            "type": "river", "bbox": (75.52, 32.20, 75.74, 32.34)},
            {"name": "Chakki River",          "type": "river", "bbox": (75.55, 32.24, 75.70, 32.32)},
        ],
        "Ferozepur (Firozpur)": [
            {"name": "Sutlej River",          "type": "river", "bbox": (74.44, 30.82, 74.70, 31.00)},
        ],
        "Hoshiarpur": [
            {"name": "Beas River",            "type": "river", "bbox": (75.72, 31.42, 75.94, 31.60)},
            {"name": "Swan River",            "type": "river", "bbox": (75.80, 31.44, 75.92, 31.54)},
        ],
        "Ropar (Rupnagar)": [
            {"name": "Sutlej River",          "type": "river", "bbox": (76.40, 30.92, 76.62, 31.04)},
            {"name": "Ropar Wetland",         "type": "lake",  "bbox": (76.44, 30.94, 76.58, 31.02)},
        ],
        "Gurdaspur": [
            {"name": "Ravi River",            "type": "river", "bbox": (75.26, 31.96, 75.50, 32.12)},
            {"name": "Beas River",            "type": "river", "bbox": (75.28, 31.98, 75.46, 32.10)},
        ],
        "Kapurthala": [
            {"name": "Beas River",            "type": "river", "bbox": (75.24, 31.32, 75.46, 31.46)},
            {"name": "Kanjli Wetland",        "type": "lake",  "bbox": (75.360, 31.374, 75.402, 31.398)},
        ],
        "Moga": [
            {"name": "Beas River",            "type": "river", "bbox": (75.04, 30.74, 75.24, 30.90)},
            {"name": "Sutlej River",          "type": "river", "bbox": (75.08, 30.76, 75.20, 30.88)},
        ],
        "Barnala": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (75.42, 30.30, 75.62, 30.44)},
        ],
        "Faridkot": [
            {"name": "Sutlej River",          "type": "river", "bbox": (74.62, 30.58, 74.84, 30.74)},
        ],
        "Muktsar": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (74.36, 30.38, 74.60, 30.54)},
        ],
        "Sangrur": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (75.70, 30.16, 75.94, 30.32)},
            {"name": "Patialvi Rao",          "type": "river", "bbox": (75.74, 30.18, 75.90, 30.30)},
        ],
        "Mansa": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (75.28, 29.88, 75.50, 30.06)},
        ],
        "SBS Nagar (Nawanshahr)": [
            {"name": "Sutlej River",          "type": "river", "bbox": (76.72, 30.66, 76.96, 30.82)},
            {"name": "Beas River",            "type": "river", "bbox": (76.74, 30.68, 76.92, 30.80)},
        ],
        "Anandpur Sahib": [
            {"name": "Sutlej River",          "type": "river", "bbox": (76.38, 31.18, 76.60, 31.32)},
        ],
        "Kiratpur Sahib": [
            {"name": "Sutlej River",          "type": "river", "bbox": (76.46, 31.10, 76.68, 31.26)},
        ],
        "Goindwal Sahib": [
            {"name": "Beas River",            "type": "river", "bbox": (74.92, 31.60, 75.08, 31.72)},
        ],
        "Harike": [
            {"name": "Beas-Sutlej Confluence","type": "river", "bbox": (74.86, 31.08, 75.06, 31.24)},
            {"name": "Harike Wetland",        "type": "lake",  "bbox": (74.908, 31.146, 74.968, 31.188)},
        ],
        "Sultanpur Lodhi": [
            {"name": "Beas River",            "type": "river", "bbox": (75.06, 31.14, 75.26, 31.30)},
            {"name": "Kanjli Lake",           "type": "lake",  "bbox": (75.162, 31.196, 75.218, 31.238)},
        ],
        "Phillaur": [
            {"name": "Sutlej River",          "type": "river", "bbox": (75.78, 31.00, 76.00, 31.14)},
        ],
        "Machhiwara": [
            {"name": "Sutlej River",          "type": "river", "bbox": (75.85, 30.90, 76.06, 31.04)},
        ],
        "Nangal": [
            {"name": "Sutlej River",          "type": "river", "bbox": (76.34, 31.36, 76.50, 31.48)},
            {"name": "Bhakra-Nangal Reservoir","type": "lake", "bbox": (76.420, 31.408, 76.458, 31.438)},
        ],
        "Talwara": [
            {"name": "Beas River",            "type": "river", "bbox": (75.88, 31.92, 76.06, 32.06)},
            {"name": "Pong Dam Reservoir",    "type": "lake",  "bbox": (75.920, 31.956, 75.980, 31.996)},
        ],
        "Mukerian": [
            {"name": "Beas River",            "type": "river", "bbox": (75.60, 31.92, 75.82, 32.06)},
        ],
        "Dasuya": [
            {"name": "Beas River",            "type": "river", "bbox": (75.64, 31.80, 75.88, 31.94)},
        ],
        "Fazilka": [
            {"name": "Sutlej River",          "type": "river", "bbox": (73.88, 30.28, 74.12, 30.44)},
        ],
        "Abohar": [
            {"name": "Ghaggar River",         "type": "river", "bbox": (74.10, 30.06, 74.36, 30.24)},
        ],
        "Dinanagar": [
            {"name": "Ravi River",            "type": "river", "bbox": (75.50, 32.06, 75.68, 32.20)},
        ],
    },

    # -------------------------------------------------------------------------
    "Rajasthan": {
        "Jaipur": [
            {"name": "Dravyavati River", "type": "river", "bbox": (75.73, 26.87, 75.85, 26.95)},
            {"name": "Man Sagar", "type": "lake", "bbox": (75.76, 26.89, 75.82, 26.93)},
            {"name": "Jal Mahal Lake", "type": "lake", "bbox": (75.76, 26.89, 75.82, 26.93)},
        ],
        "Jodhpur": [
            {"name": "Luni", "type": "river", "bbox": (72.96, 26.25, 73.08, 26.33)},
            {"name": "Balsamand Lake", "type": "lake", "bbox": (72.99, 26.27, 73.05, 26.31)},
            {"name": "Kaylana Lake", "type": "lake", "bbox": (72.99, 26.27, 73.05, 26.31)},
        ],
        "Udaipur": [
            {"name": "Berach", "type": "river", "bbox": (73.65, 24.55, 73.77, 24.63)},
            {"name": "Ahar River", "type": "river", "bbox": (73.65, 24.55, 73.77, 24.63)},
            {"name": "Pichola Lake", "type": "lake", "bbox": (73.68, 24.57, 73.74, 24.61)},
            {"name": "Fateh Sagar", "type": "lake", "bbox": (73.68, 24.57, 73.74, 24.61)},
            {"name": "Udai Sagar", "type": "lake", "bbox": (73.68, 24.57, 73.74, 24.61)},
            {"name": "Jaisamand", "type": "river", "bbox": (73.65, 24.55, 73.77, 24.63)},
        ],
        "Kota": [
            {"name": "Chambal River", "type": "river", "bbox": (75.8, 25.14, 75.92, 25.22)},
        ],
        "Ajmer": [
            {"name": "Banas area", "type": "river", "bbox": (74.58, 26.41, 74.7, 26.49)},
            {"name": "Ana Sagar Lake", "type": "lake", "bbox": (74.61, 26.43, 74.67, 26.47)},
        ],
        "Bikaner": [
            {"name": "No major river", "type": "river", "bbox": (73.25, 27.98, 73.37, 28.06)},
            {"name": "Gajner Lake", "type": "lake", "bbox": (73.28, 28.0, 73.34, 28.04)},
        ],
        "Alwar": [
            {"name": "Ruparel", "type": "river", "bbox": (76.55, 27.52, 76.67, 27.6)},
            {"name": "Siliserh Lake", "type": "lake", "bbox": (76.58, 27.54, 76.64, 27.58)},
        ],
        "Bharatpur": [
            {"name": "Banganga", "type": "river", "bbox": (77.44, 27.18, 77.56, 27.26)},
            {"name": "Gambhir", "type": "river", "bbox": (77.44, 27.18, 77.56, 27.26)},
            {"name": "Keoladeo", "type": "river", "bbox": (77.44, 27.18, 77.56, 27.26)},
            {"name": "Ghana wetland", "type": "lake", "bbox": (77.47, 27.2, 77.53, 27.24)},
        ],
        "Bhilwara": [
            {"name": "Banas", "type": "river", "bbox": (74.58, 25.31, 74.7, 25.39)},
            {"name": "Berach", "type": "river", "bbox": (74.58, 25.31, 74.7, 25.39)},
            {"name": "Kothari", "type": "river", "bbox": (74.58, 25.31, 74.7, 25.39)},
        ],
        "Chittorgarh": [
            {"name": "Gambhiri River", "type": "river", "bbox": (74.57, 24.84, 74.69, 24.92)},
            {"name": "Berach River", "type": "river", "bbox": (74.57, 24.84, 74.69, 24.92)},
        ],
        "Pali": [
            {"name": "Bandi River", "type": "river", "bbox": (73.27, 25.73, 73.39, 25.81)},
            {"name": "Luni", "type": "river", "bbox": (73.27, 25.73, 73.39, 25.81)},
        ],
        "Banswara": [
            {"name": "Mahi River", "type": "river", "bbox": (74.38, 23.51, 74.5, 23.59)},
        ],
        "Dungarpur": [
            {"name": "Mahi River", "type": "river", "bbox": (73.65, 23.8, 73.77, 23.88)},
            {"name": "Som River", "type": "river", "bbox": (73.65, 23.8, 73.77, 23.88)},
        ],
        "Tonk": [
            {"name": "Banas River", "type": "river", "bbox": (75.73, 26.13, 75.85, 26.21)},
        ],
        "Bundi": [
            {"name": "Chambal tributaries", "type": "river", "bbox": (75.58, 25.4, 75.7, 25.48)},
        ],
        "Sawai Madhopur": [
            {"name": "Chambal", "type": "river", "bbox": (76.29, 25.98, 76.41, 26.06)},
            {"name": "Banas", "type": "river", "bbox": (76.29, 25.98, 76.41, 26.06)},
        ],
        "Dholpur": [
            {"name": "Chambal River", "type": "river", "bbox": (77.84, 26.66, 77.96, 26.74)},
        ],
        "Pratapgarh": [
            {"name": "Jakham", "type": "river", "bbox": (75.82, 26.88, 75.94, 26.96)},
            {"name": "Mahi tributaries", "type": "river", "bbox": (75.82, 26.88, 75.94, 26.96)},
        ],
        "Jhalawar": [
            {"name": "Kali Sindh", "type": "river", "bbox": (76.11, 24.56, 76.23, 24.64)},
        ],
        "Barmer": [
            {"name": "Luni", "type": "river", "bbox": (71.33, 25.71, 71.45, 25.79)},
        ],
        "Sirohi": [
            {"name": "West Banas", "type": "river", "bbox": (72.8, 24.85, 72.92, 24.93)},
        ],
        "Mount Abu": [
            {"name": "Nakki Lake", "type": "lake", "bbox": (72.68, 24.57, 72.74, 24.61)},
        ],
        "Nathdwara": [
            {"name": "Banas River", "type": "river", "bbox": (75.81, 26.86, 75.93, 26.94)},
        ],
        "Pushkar": [
            {"name": "Pushkar Lake", "type": "lake", "bbox": (74.52, 26.47, 74.58, 26.51)},
        ],
        "Jaisalmer": [
            {"name": "No major river", "type": "river", "bbox": (70.86, 26.87, 70.98, 26.95)},
            {"name": "Gadisar Lake", "type": "lake", "bbox": (70.89, 26.89, 70.95, 26.93)},
        ],
        "Hanumangarh": [
            {"name": "Ghaggar River", "type": "river", "bbox": (74.27, 29.54, 74.39, 29.62)},
        ],
        "Sri Ganganagar": [
            {"name": "Ghaggar area", "type": "river", "bbox": (73.82, 29.87, 73.94, 29.95)},
            {"name": "canal-fed", "type": "river", "bbox": (73.82, 29.87, 73.94, 29.95)},
        ],
        "Rajsamand": [
            {"name": "Rajsamand Lake", "type": "lake", "bbox": (73.85, 25.05, 73.91, 25.09)},
        ],
        "Beawar": [
            {"name": "Banas tributaries", "type": "river", "bbox": (75.75, 26.78, 75.87, 26.86)},
        ],
        "Kishangarh": [
            {"name": "Banas tributaries", "type": "river", "bbox": (75.64, 26.84, 75.76, 26.92)},
        ],
        "Baran": [
            {"name": "Parbati", "type": "river", "bbox": (76.45, 25.06, 76.57, 25.14)},
        ],
        "Dausa": [
            {"name": "Banganga area", "type": "river", "bbox": (76.28, 26.84, 76.4, 26.92)},
        ],
        "Karauli": [
            {"name": "Chambal area", "type": "river", "bbox": (76.96, 26.46, 77.08, 26.54)},
        ],
        "Sambhar": [
            {"name": "Sambhar Salt Lake", "type": "lake", "bbox": (75.8, 26.82, 75.86, 26.86)},
        ],
        "Rawatbhata": [
            {"name": "Chambal River", "type": "river", "bbox": (75.71, 26.86, 75.83, 26.94)},
        ],
    },

    # -------------------------------------------------------------------------
    # 22. SIKKIM
    # -------------------------------------------------------------------------
    "Sikkim": {
        "Gangtok": [
            {"name": "Teesta", "type": "river", "bbox": (88.56, 27.29, 88.68, 27.37)},
            {"name": "Rani Khola", "type": "river", "bbox": (88.56, 27.29, 88.68, 27.37)},
        ],
        "Namchi": [
            {"name": "Rangit River", "type": "river", "bbox": (88.29, 27.13, 88.41, 27.21)},
        ],
        "Mangan": [
            {"name": "Teesta River", "type": "river", "bbox": (88.47, 27.47, 88.59, 27.55)},
        ],
        "Gyalshing (Geyzing)": [
            {"name": "Rathong Chu", "type": "river", "bbox": (88.2, 27.25, 88.32, 27.33)},
            {"name": "Rangit", "type": "river", "bbox": (88.2, 27.25, 88.32, 27.33)},
        ],
        "Rangpo": [
            {"name": "Rangpo Chu-Teesta confluence", "type": "river", "bbox": (88.47, 27.14, 88.59, 27.22)},
        ],
        "Jorethang": [
            {"name": "Rangit-Teesta confluence", "type": "river", "bbox": (88.26, 27.06, 88.38, 27.14)},
        ],
        "Singtam": [
            {"name": "Teesta River", "type": "river", "bbox": (88.45, 27.2, 88.57, 27.28)},
        ],
        "Ravangla": [
            {"name": "Rangit tributaries", "type": "river", "bbox": (88.31, 27.27, 88.43, 27.35)},
        ],
        "Lachung": [
            {"name": "Lachung Chu", "type": "river", "bbox": (88.69, 27.65, 88.81, 27.73)},
        ],
        "Lachen": [
            {"name": "Lachen Chu", "type": "river", "bbox": (88.57, 27.26, 88.69, 27.34)},
        ],
        "Pelling": [
            {"name": "Rimbi River", "type": "river", "bbox": (88.18, 27.26, 88.3, 27.34)},
        ],
        "Yuksom": [
            {"name": "Rathong Chu", "type": "river", "bbox": (88.16, 27.33, 88.28, 27.41)},
        ],
        "Chungthang": [
            {"name": "Teesta", "type": "river", "bbox": (88.65, 27.27, 88.77, 27.35)},
            {"name": "Lachung Chu + Lachen Chu confluence", "type": "river", "bbox": (88.65, 27.27, 88.77, 27.35)},
        ],
        "Rongli": [
            {"name": "Rangpo Chu area", "type": "river", "bbox": (88.53, 27.3, 88.65, 27.38)},
        ],
        "Dikchu": [
            {"name": "Teesta River", "type": "river", "bbox": (88.66, 27.32, 88.78, 27.4)},
        ],
    },

    # -------------------------------------------------------------------------
    # 23. TAMIL NADU
    # -------------------------------------------------------------------------
    "Tamil Nadu": {
        "Chennai": [
            {"name": "Cooum River", "type": "river", "bbox": (80.21, 13.04, 80.33, 13.12)},
            {"name": "Adyar River", "type": "river", "bbox": (80.21, 13.04, 80.33, 13.12)},
            {"name": "Kosasthalaiyar River", "type": "river", "bbox": (80.21, 13.04, 80.33, 13.12)},
            {"name": "Chembarambakkam Lake", "type": "lake", "bbox": (80.24, 13.06, 80.3, 13.1)},
            {"name": "Puzhal Lake", "type": "lake", "bbox": (80.24, 13.06, 80.3, 13.1)},
            {"name": "Sholavaram Lake", "type": "lake", "bbox": (80.24, 13.06, 80.3, 13.1)},
        ],
        "Madurai": [
            {"name": "Vaigai River", "type": "river", "bbox": (78.06, 9.89, 78.18, 9.97)},
        ],
        "Tiruchirappalli (Trichy)": [
            {"name": "Kaveri River", "type": "river", "bbox": (78.63, 10.75, 78.75, 10.83)},
        ],
        "Coimbatore": [
            {"name": "Noyyal River", "type": "river", "bbox": (76.9, 10.98, 77.02, 11.06)},
        ],
        "Salem": [
            {"name": "Thirumanimuthar River", "type": "river", "bbox": (78.09, 11.62, 78.21, 11.7)},
        ],
        "Erode": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.67, 11.3, 77.79, 11.38)},
            {"name": "Bhavani River", "type": "river", "bbox": (77.67, 11.3, 77.79, 11.38)},
        ],
        "Tirunelveli": [
            {"name": "Thamiraparani River", "type": "river", "bbox": (77.64, 8.69, 77.76, 8.77)},
        ],
        "Thanjavur": [
            {"name": "Kaveri Delta", "type": "river", "bbox": (79.08, 10.75, 79.2, 10.83)},
            {"name": "Grand Anicut", "type": "river", "bbox": (79.08, 10.75, 79.2, 10.83)},
        ],
        "Vellore": [
            {"name": "Palar River", "type": "river", "bbox": (79.07, 12.88, 79.19, 12.96)},
        ],
        "Kumbakonam": [
            {"name": "Between Kaveri and Kollidam", "type": "lake", "bbox": (79.35, 10.94, 79.41, 10.98)},
        ],
        "Srirangam": [
            {"name": "Between Kaveri and Kollidam", "type": "lake", "bbox": (78.66, 10.84, 78.72, 10.88)},
            {"name": "island", "type": "river", "bbox": (78.63, 10.82, 78.75, 10.9)},
        ],
        "Dindigul": [
            {"name": "Kodaganar", "type": "river", "bbox": (77.92, 10.33, 78.04, 10.41)},
            {"name": "Vaigai tributaries", "type": "river", "bbox": (77.92, 10.33, 78.04, 10.41)},
        ],
        "Theni": [
            {"name": "Suruli", "type": "river", "bbox": (77.42, 9.97, 77.54, 10.05)},
            {"name": "Vaigai tributaries", "type": "river", "bbox": (77.42, 9.97, 77.54, 10.05)},
        ],
        "Kancheepuram": [
            {"name": "Palar River", "type": "river", "bbox": (80.13, 13.01, 80.25, 13.09)},
            {"name": "Vegavathi River", "type": "river", "bbox": (80.13, 13.01, 80.25, 13.09)},
        ],
        "Tiruvannamalai": [
            {"name": "Cheyyar River", "type": "river", "bbox": (79.01, 12.19, 79.13, 12.27)},
        ],
        "Cuddalore": [
            {"name": "Ponnaiyar", "type": "river", "bbox": (79.71, 11.71, 79.83, 11.79)},
            {"name": "Paravanar", "type": "river", "bbox": (79.71, 11.71, 79.83, 11.79)},
        ],
        "Nagapattinam": [
            {"name": "Kaveri Delta", "type": "river", "bbox": (79.78, 10.73, 79.9, 10.81)},
        ],
        "Karur": [
            {"name": "Amaravathi River", "type": "river", "bbox": (78.02, 10.92, 78.14, 11.0)},
        ],
        "Namakkal": [
            {"name": "Kaveri area", "type": "river", "bbox": (78.11, 11.18, 78.23, 11.26)},
        ],
        "Dharmapuri": [
            {"name": "Ponnaiyar", "type": "river", "bbox": (78.1, 12.09, 78.22, 12.17)},
            {"name": "Cauvery", "type": "river", "bbox": (78.1, 12.09, 78.22, 12.17)},
        ],
        "Krishnagiri": [
            {"name": "Ponnaiyar", "type": "river", "bbox": (78.15, 12.49, 78.27, 12.57)},
        ],
        "Mettur": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.74, 11.74, 77.86, 11.82)},
            {"name": "Stanley Reservoir", "type": "lake", "bbox": (77.77, 11.76, 77.83, 11.8)},
            {"name": "Mettur Dam", "type": "lake", "bbox": (77.77, 11.76, 77.83, 11.8)},
        ],
        "Hogenakkal": [
            {"name": "Kaveri River", "type": "river", "bbox": (77.72, 12.08, 77.84, 12.16)},
            {"name": "falls", "type": "river", "bbox": (77.72, 12.08, 77.84, 12.16)},
        ],
        "Papanasam": [
            {"name": "Thamiraparani River", "type": "river", "bbox": (80.17, 13.09, 80.29, 13.17)},
        ],
        "Tiruvarur": [
            {"name": "Kaveri Delta", "type": "river", "bbox": (79.58, 10.73, 79.7, 10.81)},
        ],
        "Mayiladuthurai": [
            {"name": "Kaveri River", "type": "river", "bbox": (79.59, 11.06, 79.71, 11.14)},
        ],
        "Sivaganga": [
            {"name": "Vaigai area", "type": "river", "bbox": (78.42, 10.1, 78.54, 10.18)},
        ],
        "Ramanathapuram": [
            {"name": "coast", "type": "river", "bbox": (78.77, 9.33, 78.89, 9.41)},
        ],
        "Thoothukudi (Tuticorin)": [
            {"name": "coast", "type": "river", "bbox": (78.07, 8.72, 78.19, 8.8)},
        ],
        "Nagercoil": [
            {"name": "Pazhayar River", "type": "river", "bbox": (80.27, 13.06, 80.39, 13.14)},
        ],
        "Pollachi": [
            {"name": "Aliyar", "type": "river", "bbox": (80.25, 12.96, 80.37, 13.04)},
            {"name": "Parambikulam rivers", "type": "river", "bbox": (80.25, 12.96, 80.37, 13.04)},
        ],
        "Palani": [
            {"name": "Shanmuganadi", "type": "river", "bbox": (80.2, 12.97, 80.32, 13.05)},
        ],
        "Kodaikanal": [
            {"name": "Kodaikanal Lake", "type": "lake", "bbox": (77.46, 10.22, 77.52, 10.26)},
            {"name": "Berijam Lake", "type": "lake", "bbox": (77.46, 10.22, 77.52, 10.26)},
        ],
        "Ooty (Udhagamandalam)": [
            {"name": "Moyar area", "type": "river", "bbox": (80.27, 12.98, 80.39, 13.06)},
            {"name": "Ooty Lake", "type": "lake", "bbox": (80.3, 13.0, 80.36, 13.04)},
        ],
        "Yercaud": [
            {"name": "Yercaud Lake", "type": "lake", "bbox": (80.29, 13.07, 80.35, 13.11)},
        ],
        "Hosur": [
            {"name": "Ponnaiyar area", "type": "river", "bbox": (80.15, 13.05, 80.27, 13.13)},
        ],
        "Ranipet": [
            {"name": "Palar River", "type": "river", "bbox": (79.27, 12.89, 79.39, 12.97)},
        ],
        "Ambur": [
            {"name": "Palar River", "type": "river", "bbox": (80.26, 13.09, 80.38, 13.17)},
        ],
        "Vaniyambadi": [
            {"name": "Palar River", "type": "river", "bbox": (80.25, 13.0, 80.37, 13.08)},
        ],
        "Villupuram": [
            {"name": "Ponnaiyar", "type": "river", "bbox": (79.43, 11.9, 79.55, 11.98)},
        ],
        "Chidambaram": [
            {"name": "Kollidam", "type": "lake", "bbox": (79.66, 11.38, 79.72, 11.42)},
            {"name": "Vellar", "type": "river", "bbox": (79.63, 11.36, 79.75, 11.44)},
        ],
        "Thiruvaiyaru": [
            {"name": "Kaveri River", "type": "river", "bbox": (80.24, 13.09, 80.36, 13.17)},
        ],
        "Bhavani (town)": [
            {"name": "Bhavani River-Kaveri confluence", "type": "river", "bbox": (80.11, 12.95, 80.23, 13.03)},
        ],
        "Gobichettipalayam": [
            {"name": "Bhavani area", "type": "river", "bbox": (80.12, 12.96, 80.24, 13.04)},
        ],
        "Tiruppur": [
            {"name": "Noyyal", "type": "river", "bbox": (80.21, 13.06, 80.33, 13.14)},
        ],
        "Gudiyatham": [
            {"name": "Palar River", "type": "river", "bbox": (80.22, 13.07, 80.34, 13.15)},
        ],
        "Chengalpattu": [
            {"name": "Palar", "type": "river", "bbox": (80.31, 13.1, 80.43, 13.18)},
        ],
    },

    # -------------------------------------------------------------------------
    # 24. TELANGANA
    # -------------------------------------------------------------------------
    "Telangana": {
        "Hyderabad": [
            {"name": "Musi River", "type": "river", "bbox": (78.41, 17.34, 78.53, 17.42)},
            {"name": "Hussain Sagar", "type": "lake", "bbox": (78.44, 17.36, 78.5, 17.4)},
            {"name": "Osman Sagar", "type": "lake", "bbox": (78.44, 17.36, 78.5, 17.4)},
            {"name": "Himayat Sagar", "type": "lake", "bbox": (78.44, 17.36, 78.5, 17.4)},
            {"name": "Durgam Cheruvu", "type": "river", "bbox": (78.41, 17.34, 78.53, 17.42)},
        ],
        "Warangal": [
            {"name": "Bhadrakali Lake", "type": "lake", "bbox": (79.56, 17.96, 79.62, 18.0)},
        ],
        "Karimnagar": [
            {"name": "Manair River", "type": "river", "bbox": (79.07, 18.4, 79.19, 18.48)},
        ],
        "Nizamabad": [
            {"name": "Manjira River", "type": "river", "bbox": (78.03, 18.63, 78.15, 18.71)},
        ],
        "Khammam": [
            {"name": "Munneru River", "type": "river", "bbox": (80.09, 17.21, 80.21, 17.29)},
        ],
        "Nalgonda": [
            {"name": "Musi area", "type": "river", "bbox": (79.21, 17.01, 79.33, 17.09)},
        ],
        "Mahbubnagar (Palamuru)": [
            {"name": "Krishna area", "type": "river", "bbox": (77.93, 16.7, 78.05, 16.78)},
        ],
        "Ramagundam": [
            {"name": "Godavari River", "type": "river", "bbox": (79.41, 18.72, 79.53, 18.8)},
        ],
        "Siddipet": [
            {"name": "Manjira area", "type": "river", "bbox": (78.79, 18.06, 78.91, 18.14)},
        ],
        "Medak": [
            {"name": "Manjira", "type": "river", "bbox": (78.2, 18.01, 78.32, 18.09)},
        ],
        "Adilabad": [
            {"name": "Penganga River", "type": "river", "bbox": (78.47, 19.63, 78.59, 19.71)},
        ],
        "Mancherial": [
            {"name": "Godavari-Pranahita confluence area", "type": "river", "bbox": (79.38, 18.83, 79.5, 18.91)},
        ],
        "Suryapet": [
            {"name": "Krishna area", "type": "river", "bbox": (79.56, 17.1, 79.68, 17.18)},
        ],
        "Miryalaguda": [
            {"name": "Krishna", "type": "river", "bbox": (78.36, 17.3, 78.48, 17.38)},
            {"name": "Nagarjuna Sagar", "type": "lake", "bbox": (78.39, 17.32, 78.45, 17.36)},
        ],
        "Sangareddy": [
            {"name": "Manjira", "type": "river", "bbox": (78.03, 17.58, 78.15, 17.66)},
        ],
        "Bhongir (Yadadri-Bhuvanagiri)": [
            {"name": "rivers", "type": "river", "bbox": (78.45, 17.29, 78.57, 17.37)},
        ],
        "Kothagudem": [
            {"name": "Kinnerasani River", "type": "river", "bbox": (78.34, 17.39, 78.46, 17.47)},
        ],
        "Bhadrachalam": [
            {"name": "Godavari River", "type": "river", "bbox": (80.82, 17.63, 80.94, 17.71)},
        ],
        "Gadwal (Jogulamba)": [
            {"name": "Krishna-Tungabhadra area", "type": "river", "bbox": (77.75, 16.2, 77.87, 16.28)},
        ],
        "Wanaparthy": [
            {"name": "Krishna area", "type": "river", "bbox": (78.0, 16.32, 78.12, 16.4)},
        ],
        "Nirmal": [
            {"name": "Godavari", "type": "river", "bbox": (78.29, 19.06, 78.41, 19.14)},
            {"name": "Penganga", "type": "river", "bbox": (78.29, 19.06, 78.41, 19.14)},
        ],
        "Kamareddy": [
            {"name": "Manjira", "type": "river", "bbox": (78.28, 18.28, 78.4, 18.36)},
        ],
        "Jangaon": [
            {"name": "rivers", "type": "river", "bbox": (79.09, 17.69, 79.21, 17.77)},
        ],
        "Narayanpet": [
            {"name": "Krishna area", "type": "river", "bbox": (78.33, 17.38, 78.45, 17.46)},
        ],
        "Bodhan": [
            {"name": "Godavari River", "type": "river", "bbox": (78.41, 17.31, 78.53, 17.39)},
        ],
        "Bellampalli": [
            {"name": "Godavari", "type": "river", "bbox": (78.43, 17.43, 78.55, 17.51)},
            {"name": "Pranahita", "type": "river", "bbox": (78.43, 17.43, 78.55, 17.51)},
        ],
        "Sircilla": [
            {"name": "Manair", "type": "river", "bbox": (78.36, 17.42, 78.48, 17.5)},
        ],
        "Jagtial": [
            {"name": "Godavari", "type": "river", "bbox": (78.85, 18.75, 78.97, 18.83)},
        ],
        "Peddapalli": [
            {"name": "Godavari", "type": "river", "bbox": (79.32, 18.58, 79.44, 18.66)},
        ],
        "Kalwakurthy": [
            {"name": "Krishna", "type": "river", "bbox": (78.39, 17.27, 78.51, 17.35)},
        ],
        "Alampur": [
            {"name": "Krishna-Tungabhadra confluence", "type": "river", "bbox": (78.07, 15.84, 78.19, 15.92)},
        ],
        "Basara": [
            {"name": "Godavari River", "type": "river", "bbox": (78.5, 17.31, 78.62, 17.39)},
        ],
    },

    # -------------------------------------------------------------------------
    # 25. TRIPURA
    # -------------------------------------------------------------------------
    "Tripura": {
        "Agartala": [
            {"name": "Haora River", "type": "river", "bbox": (91.22, 23.79, 91.34, 23.87)},
        ],
        "Udaipur": [
            {"name": "Gomati River", "type": "river", "bbox": (73.65, 24.55, 73.77, 24.63)},
        ],
        "Dharmanagar": [
            {"name": "Deo River", "type": "river", "bbox": (92.11, 24.33, 92.23, 24.41)},
        ],
        "Kailashahar": [
            {"name": "Manu River", "type": "river", "bbox": (91.94, 24.29, 92.06, 24.37)},
        ],
        "Ambassa": [
            {"name": "Dhalai River", "type": "river", "bbox": (91.79, 23.88, 91.91, 23.96)},
        ],
        "Belonia": [
            {"name": "Muhuri River", "type": "river", "bbox": (91.39, 23.21, 91.51, 23.29)},
        ],
        "Kamalpur": [
            {"name": "Khowai River", "type": "river", "bbox": (91.76, 24.16, 91.88, 24.24)},
        ],
        "Sabroom": [
            {"name": "Feni River", "type": "river", "bbox": (91.66, 22.96, 91.78, 23.04)},
        ],
        "Sonamura": [
            {"name": "Gomati", "type": "river", "bbox": (91.26, 23.66, 91.38, 23.74)},
        ],
        "Khowai": [
            {"name": "Khowai River", "type": "river", "bbox": (91.54, 24.03, 91.66, 24.11)},
        ],
        "Bishalgarh": [
            {"name": "Gomati", "type": "river", "bbox": (91.32, 23.59, 91.44, 23.67)},
        ],
        "Melaghar": [
            {"name": "Gomati", "type": "river", "bbox": (91.28, 23.78, 91.4, 23.86)},
        ],
        "Amarpur": [
            {"name": "Gomati tributaries", "type": "river", "bbox": (91.17, 23.73, 91.3, 23.81)},
        ],
        "Kumarghat": [
            {"name": "Dhalai", "type": "river", "bbox": (91.32, 23.73, 91.44, 23.81)},
            {"name": "Juri", "type": "river", "bbox": (91.32, 23.73, 91.44, 23.81)},
        ],
        "Teliamura": [
            {"name": "Khowai", "type": "river", "bbox": (91.13, 23.79, 91.25, 23.87)},
        ],
    },

    # -------------------------------------------------------------------------
    # 26. UTTAR PRADESH
    # -------------------------------------------------------------------------
    "Uttar Pradesh": {
        "Lucknow": [
            {"name": "Gomti River", "type": "river", "bbox": (80.89, 26.81, 81.01, 26.89)},
        ],
        "Varanasi (Kashi)": [
            {"name": "Ganga River", "type": "river", "bbox": (82.95, 25.28, 83.07, 25.36)},
            {"name": "Varuna River", "type": "river", "bbox": (82.95, 25.28, 83.07, 25.36)},
            {"name": "Assi River", "type": "river", "bbox": (82.95, 25.28, 83.07, 25.36)},
        ],
        "Agra": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.96, 27.14, 78.08, 27.22)},
            {"name": "Keetham", "type": "river", "bbox": (77.96, 27.14, 78.08, 27.22)},
            {"name": "Sur Sarovar", "type": "lake", "bbox": (77.99, 27.16, 78.05, 27.2)},
        ],
        "Kanpur": [
            {"name": "Ganga River", "type": "river", "bbox": (80.29, 26.41, 80.41, 26.49)},
        ],
        "Prayagraj (Allahabad)": [
            {"name": "Ganga-Yamuna-Saraswati Triveni Sangam", "type": "river", "bbox": (81.79, 25.39, 81.91, 25.47)},
        ],
        "Meerut": [
            {"name": "Hindon River", "type": "river", "bbox": (77.65, 28.94, 77.77, 29.02)},
            {"name": "Kali River", "type": "river", "bbox": (77.65, 28.94, 77.77, 29.02)},
        ],
        "Ghaziabad": [
            {"name": "Hindon River", "type": "river", "bbox": (77.36, 28.63, 77.48, 28.71)},
        ],
        "Noida": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.33, 28.5, 77.45, 28.58)},
            {"name": "Hindon River", "type": "river", "bbox": (77.33, 28.5, 77.45, 28.58)},
        ],
        "Mathura": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.61, 27.45, 77.73, 27.53)},
        ],
        "Vrindavan": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.64, 27.54, 77.76, 27.62)},
        ],
        "Aligarh": [
            {"name": "Ganga-Yamuna doab", "type": "river", "bbox": (78.02, 27.84, 78.14, 27.92)},
        ],
        "Moradabad": [
            {"name": "Ramganga River", "type": "river", "bbox": (78.72, 28.79, 78.84, 28.87)},
        ],
        "Bareilly": [
            {"name": "Ramganga", "type": "river", "bbox": (79.36, 28.33, 79.48, 28.41)},
        ],
        "Gorakhpur": [
            {"name": "Rapti River", "type": "river", "bbox": (83.31, 26.72, 83.43, 26.8)},
            {"name": "Ramgarh Tal", "type": "lake", "bbox": (83.34, 26.74, 83.4, 26.78)},
        ],
        "Ayodhya (Faizabad)": [
            {"name": "Saryu River", "type": "river", "bbox": (82.14, 26.76, 82.26, 26.84)},
            {"name": "Ghaghra", "type": "river", "bbox": (82.14, 26.76, 82.26, 26.84)},
        ],
        "Jhansi": [
            {"name": "Betwa River", "type": "river", "bbox": (78.51, 25.41, 78.63, 25.49)},
            {"name": "Pahuj River", "type": "river", "bbox": (78.51, 25.41, 78.63, 25.49)},
        ],
        "Mirzapur": [
            {"name": "Ganga River", "type": "river", "bbox": (82.51, 25.11, 82.63, 25.19)},
        ],
        "Sultanpur": [
            {"name": "Gomti River", "type": "river", "bbox": (82.01, 26.22, 82.13, 26.3)},
        ],
        "Jaunpur": [
            {"name": "Gomti River", "type": "river", "bbox": (82.62, 25.71, 82.74, 25.79)},
        ],
        "Ballia": [
            {"name": "Ganga River", "type": "river", "bbox": (84.09, 25.72, 84.21, 25.8)},
            {"name": "Ghaghra River", "type": "river", "bbox": (84.09, 25.72, 84.21, 25.8)},
            {"name": "Surha Tal", "type": "lake", "bbox": (84.12, 25.74, 84.18, 25.78)},
        ],
        "Bijnor": [
            {"name": "Ganga River", "type": "river", "bbox": (78.08, 29.33, 78.2, 29.41)},
        ],
        "Farrukhabad": [
            {"name": "Ganga River", "type": "river", "bbox": (79.52, 27.35, 79.64, 27.43)},
        ],
        "Etawah": [
            {"name": "Yamuna River", "type": "river", "bbox": (78.96, 26.74, 79.08, 26.82)},
            {"name": "Chambal River", "type": "river", "bbox": (78.96, 26.74, 79.08, 26.82)},
        ],
        "Banda": [
            {"name": "Ken River", "type": "river", "bbox": (80.28, 25.43, 80.4, 25.51)},
        ],
        "Hamirpur": [
            {"name": "Yamuna River", "type": "river", "bbox": (80.88, 26.76, 81.0, 26.84)},
            {"name": "Betwa River", "type": "river", "bbox": (80.88, 26.76, 81.0, 26.84)},
        ],
        "Chitrakoot": [
            {"name": "Mandakini River", "type": "river", "bbox": (80.84, 25.16, 80.96, 25.24)},
        ],
        "Rae Bareli": [
            {"name": "Sai River", "type": "river", "bbox": (81.17, 26.19, 81.29, 26.27)},
        ],
        "Unnao": [
            {"name": "Ganga", "type": "river", "bbox": (80.43, 26.51, 80.55, 26.59)},
        ],
        "Fatehpur": [
            {"name": "Ganga-Yamuna doab", "type": "river", "bbox": (80.75, 25.89, 80.87, 25.97)},
        ],
        "Shahjahanpur": [
            {"name": "Gomti", "type": "river", "bbox": (79.85, 27.84, 79.97, 27.92)},
            {"name": "Garra", "type": "river", "bbox": (79.85, 27.84, 79.97, 27.92)},
            {"name": "Khannaut", "type": "river", "bbox": (79.85, 27.84, 79.97, 27.92)},
        ],
        "Bahraich": [
            {"name": "Ghaghra", "type": "river", "bbox": (81.54, 27.53, 81.66, 27.61)},
        ],
        "Gonda": [
            {"name": "Ghaghra area", "type": "river", "bbox": (80.95, 26.84, 81.07, 26.92)},
        ],
        "Basti": [
            {"name": "Kuwano River", "type": "river", "bbox": (82.7, 26.76, 82.82, 26.84)},
        ],
        "Deoria": [
            {"name": "Ghaghra", "type": "river", "bbox": (83.73, 26.46, 83.85, 26.54)},
            {"name": "Rapti", "type": "river", "bbox": (83.73, 26.46, 83.85, 26.54)},
        ],
        "Azamgarh": [
            {"name": "Tamsa River", "type": "river", "bbox": (83.13, 26.03, 83.25, 26.11)},
            {"name": "Tons", "type": "river", "bbox": (83.13, 26.03, 83.25, 26.11)},
        ],
        "Mau": [
            {"name": "Tamsa", "type": "river", "bbox": (83.5, 25.9, 83.62, 25.98)},
        ],
        "Pratapgarh": [
            {"name": "Sai River", "type": "river", "bbox": (80.98, 26.82, 81.1, 26.9)},
        ],
        "Barabanki": [
            {"name": "Gomti area", "type": "river", "bbox": (80.91, 26.74, 81.03, 26.82)},
        ],
        "Sitapur": [
            {"name": "Gomti", "type": "river", "bbox": (80.62, 27.53, 80.74, 27.61)},
            {"name": "Sarayan", "type": "river", "bbox": (80.62, 27.53, 80.74, 27.61)},
        ],
        "Hardoi": [
            {"name": "Ganga-Gomti area", "type": "river", "bbox": (80.07, 27.36, 80.19, 27.44)},
        ],
        "Lakhimpur Kheri": [
            {"name": "Sharda", "type": "river", "bbox": (80.72, 27.91, 80.84, 27.99)},
            {"name": "Ghaghra", "type": "river", "bbox": (80.72, 27.91, 80.84, 27.99)},
        ],
        "Pilibhit": [
            {"name": "Sharda", "type": "river", "bbox": (79.75, 28.59, 79.87, 28.67)},
            {"name": "Gomti origin", "type": "river", "bbox": (79.75, 28.59, 79.87, 28.67)},
        ],
        "Rampur": [
            {"name": "Kosi River", "type": "river", "bbox": (78.96, 28.77, 79.08, 28.85)},
        ],
        "Saharanpur": [
            {"name": "Yamuna", "type": "river", "bbox": (77.48, 29.93, 77.6, 30.01)},
            {"name": "Hindon", "type": "river", "bbox": (77.48, 29.93, 77.6, 30.01)},
        ],
        "Muzaffarnagar": [
            {"name": "Ganga", "type": "river", "bbox": (77.65, 29.43, 77.77, 29.51)},
            {"name": "Hindon", "type": "river", "bbox": (77.65, 29.43, 77.77, 29.51)},
        ],
        "Bulandshahr": [
            {"name": "Ganga-Yamuna doab", "type": "river", "bbox": (77.79, 28.37, 77.91, 28.45)},
        ],
        "Amroha": [
            {"name": "Ganga area", "type": "river", "bbox": (78.41, 28.86, 78.53, 28.94)},
        ],
        "Budaun": [
            {"name": "Ganga River", "type": "river", "bbox": (79.06, 28.0, 79.18, 28.08)},
            {"name": "Sot River", "type": "river", "bbox": (79.06, 28.0, 79.18, 28.08)},
        ],
        "Mainpuri": [
            {"name": "Isan River", "type": "river", "bbox": (78.96, 27.19, 79.08, 27.27)},
        ],
        "Firozabad": [
            {"name": "Yamuna area", "type": "river", "bbox": (78.33, 27.11, 78.45, 27.19)},
        ],
        "Hathras": [
            {"name": "Yamuna area", "type": "river", "bbox": (77.99, 27.56, 78.11, 27.64)},
        ],
        "Kasganj": [
            {"name": "Ganga River", "type": "river", "bbox": (78.59, 27.77, 78.71, 27.85)},
            {"name": "Kali River", "type": "river", "bbox": (78.59, 27.77, 78.71, 27.85)},
        ],
        "Auraiya": [
            {"name": "Yamuna River", "type": "river", "bbox": (79.45, 26.43, 79.57, 26.51)},
        ],
        "Kannauj": [
            {"name": "Ganga River", "type": "river", "bbox": (79.86, 27.01, 79.98, 27.09)},
        ],
        "Orai": [
            {"name": "Betwa area", "type": "river", "bbox": (80.92, 26.81, 81.04, 26.89)},
        ],
        "Mahoba": [
            {"name": "Ken", "type": "river", "bbox": (79.81, 25.25, 79.93, 25.33)},
            {"name": "Urmil", "type": "river", "bbox": (79.81, 25.25, 79.93, 25.33)},
        ],
        "Lalitpur": [
            {"name": "Betwa tributaries", "type": "river", "bbox": (78.36, 24.65, 78.48, 24.73)},
        ],
        "Sonbhadra": [
            {"name": "Son River", "type": "river", "bbox": (83.01, 24.65, 83.13, 24.73)},
        ],
        "Chunar": [
            {"name": "Ganga River", "type": "river", "bbox": (80.93, 26.86, 81.05, 26.94)},
        ],
        "Ghazipur": [
            {"name": "Ganga River", "type": "river", "bbox": (83.52, 25.54, 83.64, 25.62)},
        ],
        "Balrampur": [
            {"name": "Rapti", "type": "river", "bbox": (80.87, 26.8, 80.99, 26.88)},
        ],
        "Kushinagar": [
            {"name": "Gandak", "type": "river", "bbox": (83.83, 26.7, 83.95, 26.78)},
        ],
        "Bhadohi": [
            {"name": "Ganga", "type": "river", "bbox": (80.84, 26.75, 80.96, 26.83)},
        ],
        "Chandauli": [
            {"name": "Ganga", "type": "river", "bbox": (83.21, 25.22, 83.33, 25.3)},
        ],
        "Jalaun": [
            {"name": "Yamuna", "type": "river", "bbox": (80.82, 26.76, 80.94, 26.84)},
            {"name": "Betwa", "type": "river", "bbox": (80.82, 26.76, 80.94, 26.84)},
        ],
        "Baghpat": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.16, 28.91, 77.28, 28.99)},
        ],
        "Bithoor": [
            {"name": "Ganga River", "type": "river", "bbox": (80.8, 26.72, 80.92, 26.8)},
        ],
        "Dalmau": [
            {"name": "Ganga River", "type": "river", "bbox": (80.79, 26.72, 80.91, 26.8)},
        ],
        "Garh Mukteshwar": [
            {"name": "Ganga River", "type": "river", "bbox": (80.89, 26.86, 81.01, 26.94)},
        ],
    },

    # -------------------------------------------------------------------------
    # 27. UTTARAKHAND
    # -------------------------------------------------------------------------
    "Uttarakhand": {
        "Dehradun": [
            {"name": "Song River", "type": "river", "bbox": (77.97, 30.28, 78.09, 30.36)},
            {"name": "Tons area", "type": "river", "bbox": (77.97, 30.28, 78.09, 30.36)},
            {"name": "Rispana River", "type": "river", "bbox": (77.97, 30.28, 78.09, 30.36)},
            {"name": "Bindal River", "type": "river", "bbox": (77.97, 30.28, 78.09, 30.36)},
            {"name": "Asan River", "type": "river", "bbox": (77.97, 30.28, 78.09, 30.36)},
        ],
        "Haridwar": [
            {"name": "Ganga River", "type": "river", "bbox": (78.1, 29.91, 78.22, 29.99)},
        ],
        "Rishikesh": [
            {"name": "Ganga River", "type": "river", "bbox": (78.21, 30.05, 78.33, 30.13)},
        ],
        "Nainital": [
            {"name": "Naini Lake", "type": "lake", "bbox": (79.43, 29.36, 79.49, 29.4)},
        ],
        "Haldwani": [
            {"name": "Gaula River", "type": "river", "bbox": (79.46, 29.18, 79.58, 29.26)},
        ],
        "Kashipur": [
            {"name": "Ramganga area", "type": "river", "bbox": (78.9, 29.17, 79.02, 29.25)},
        ],
        "Roorkee": [
            {"name": "Solani River", "type": "river", "bbox": (77.83, 29.83, 77.95, 29.91)},
            {"name": "Ganga canal area", "type": "river", "bbox": (77.83, 29.83, 77.95, 29.91)},
        ],
        "Rudraprayag": [
            {"name": "Mandakini-Alaknanda confluence", "type": "river", "bbox": (78.92, 30.24, 79.04, 30.32)},
        ],
        "Devprayag": [
            {"name": "Bhagirathi-Alaknanda confluence", "type": "river", "bbox": (78.54, 30.11, 78.66, 30.19)},
            {"name": "Ganga origin", "type": "river", "bbox": (78.54, 30.11, 78.66, 30.19)},
        ],
        "Srinagar (Garhwal)": [
            {"name": "Alaknanda River", "type": "river", "bbox": (74.74, 34.04, 74.86, 34.12)},
        ],
        "Almora": [
            {"name": "Kosi River", "type": "river", "bbox": (79.6, 29.56, 79.72, 29.64)},
        ],
        "Pithoragarh": [
            {"name": "Ramganga", "type": "river", "bbox": (80.16, 29.54, 80.28, 29.62)},
            {"name": "East", "type": "river", "bbox": (80.16, 29.54, 80.28, 29.62)},
            {"name": "Gori Ganga area", "type": "river", "bbox": (80.16, 29.54, 80.28, 29.62)},
        ],
        "Uttarkashi": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (78.38, 30.69, 78.5, 30.77)},
        ],
        "Bageshwar": [
            {"name": "Saryu-Gomti confluence", "type": "river", "bbox": (79.71, 29.8, 79.83, 29.88)},
        ],
        "Champawat": [
            {"name": "Lohawati River", "type": "river", "bbox": (80.03, 29.29, 80.15, 29.37)},
        ],
        "Pauri": [
            {"name": "Nayar River", "type": "river", "bbox": (78.72, 30.11, 78.84, 30.19)},
        ],
        "Joshimath": [
            {"name": "Alaknanda River", "type": "river", "bbox": (78.05, 30.19, 78.17, 30.27)},
            {"name": "Dhauliganga River", "type": "river", "bbox": (78.05, 30.19, 78.17, 30.27)},
        ],
        "Kotdwar": [
            {"name": "Khoh River", "type": "river", "bbox": (78.47, 29.71, 78.59, 29.79)},
        ],
        "Ramnagar": [
            {"name": "Kosi River", "type": "river", "bbox": (79.07, 29.35, 79.19, 29.43)},
        ],
        "Tanakpur": [
            {"name": "Mahakali River", "type": "river", "bbox": (80.05, 29.03, 80.17, 29.11)},
            {"name": "Sharda", "type": "river", "bbox": (80.05, 29.03, 80.17, 29.11)},
        ],
        "Gopeshwar": [
            {"name": "Alaknanda area", "type": "river", "bbox": (77.92, 30.33, 78.04, 30.41)},
        ],
        "Karnaprayag": [
            {"name": "Alaknanda-Pindar confluence", "type": "river", "bbox": (77.92, 30.34, 78.04, 30.42)},
        ],
        "Nandprayag": [
            {"name": "Alaknanda-Nandakini confluence", "type": "river", "bbox": (77.93, 30.26, 78.05, 30.34)},
        ],
        "Vishnuprayag": [
            {"name": "Alaknanda-Dhauliganga confluence", "type": "river", "bbox": (77.91, 30.35, 78.03, 30.43)},
        ],
        "Tehri": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (78.42, 30.35, 78.54, 30.43)},
            {"name": "Tehri Dam Lake", "type": "lake", "bbox": (78.45, 30.37, 78.51, 30.41)},
        ],
        "New Tehri": [
            {"name": "Tehri Dam Lake", "type": "lake", "bbox": (78.08, 30.33, 78.14, 30.37)},
        ],
        "Mussoorie": [
            {"name": "Yamuna area", "type": "river", "bbox": (78.01, 30.41, 78.13, 30.49)},
        ],
        "Ranikhet": [
            {"name": "Kosi area", "type": "river", "bbox": (77.89, 30.34, 78.01, 30.42)},
        ],
        "Munsiari": [
            {"name": "Goriganga", "type": "river", "bbox": (77.97, 30.34, 78.09, 30.42)},
        ],
        "Dharchula": [
            {"name": "Mahakali", "type": "river", "bbox": (78.02, 30.32, 78.14, 30.4)},
            {"name": "Goriganga", "type": "river", "bbox": (78.02, 30.32, 78.14, 30.4)},
        ],
        "Gangotri": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (78.88, 30.95, 79.0, 31.03)},
            {"name": "origin", "type": "river", "bbox": (78.88, 30.95, 79.0, 31.03)},
        ],
        "Kedarnath": [
            {"name": "Mandakini River", "type": "river", "bbox": (79.01, 30.69, 79.13, 30.77)},
            {"name": "origin", "type": "river", "bbox": (79.01, 30.69, 79.13, 30.77)},
        ],
        "Badrinath": [
            {"name": "Alaknanda River", "type": "river", "bbox": (79.43, 30.7, 79.55, 30.78)},
        ],
        "Kausani": [
            {"name": "Kosi", "type": "river", "bbox": (78.07, 30.34, 78.19, 30.42)},
            {"name": "Gomti", "type": "river", "bbox": (78.07, 30.34, 78.19, 30.42)},
        ],
        "Lohaghat": [
            {"name": "Lohawati River", "type": "river", "bbox": (78.06, 30.31, 78.18, 30.39)},
        ],
        "Banbasa": [
            {"name": "Sharda River", "type": "river", "bbox": (77.96, 30.38, 78.08, 30.46)},
        ],
        "Rudrapur": [
            {"name": "Gaula", "type": "river", "bbox": (77.91, 30.22, 78.03, 30.3)},
        ],
        "Sitarganj": [
            {"name": "Sharda", "type": "river", "bbox": (77.95, 30.2, 78.07, 30.28)},
        ],
        "Vikasnagar": [
            {"name": "Asan", "type": "river", "bbox": (77.94, 30.33, 78.06, 30.41)},
            {"name": "Yamuna", "type": "river", "bbox": (77.94, 30.33, 78.06, 30.41)},
        ],
    },

    # -------------------------------------------------------------------------
    # 28. WEST BENGAL
    # -------------------------------------------------------------------------
    "West Bengal": {
        "Kolkata": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.3, 22.53, 88.42, 22.61)},
            {"name": "East Kolkata Wetlands", "type": "lake", "bbox": (88.33, 22.55, 88.39, 22.59)},
            {"name": "Rabindra Sarobar", "type": "river", "bbox": (88.3, 22.53, 88.42, 22.61)},
        ],
        "Howrah": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.2, 22.55, 88.32, 22.63)},
        ],
        "Siliguri": [
            {"name": "Mahananda", "type": "river", "bbox": (88.37, 26.67, 88.49, 26.75)},
            {"name": "Teesta", "type": "river", "bbox": (88.37, 26.67, 88.49, 26.75)},
        ],
        "Darjeeling": [
            {"name": "Teesta tributaries", "type": "river", "bbox": (88.2, 27.0, 88.32, 27.08)},
            {"name": "Senchal Lake", "type": "lake", "bbox": (88.23, 27.02, 88.29, 27.06)},
        ],
        "Asansol": [
            {"name": "Damodar", "type": "lake", "bbox": (86.92, 23.67, 86.98, 23.71)},
            {"name": "Ajay", "type": "river", "bbox": (86.89, 23.65, 87.01, 23.73)},
        ],
        "Durgapur": [
            {"name": "Damodar River", "type": "lake", "bbox": (87.29, 23.53, 87.35, 23.57)},
        ],
        "Bardhaman (Burdwan)": [
            {"name": "Damodar River", "type": "lake", "bbox": (88.4, 22.54, 88.46, 22.58)},
            {"name": "Banka River", "type": "river", "bbox": (88.37, 22.52, 88.49, 22.6)},
        ],
        "Murshidabad": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (88.39, 22.52, 88.51, 22.6)},
        ],
        "Baharampur (Berhampur)": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (88.19, 24.06, 88.31, 24.14)},
        ],
        "Malda (English Bazar)": [
            {"name": "Mahananda River", "type": "river", "bbox": (88.08, 24.96, 88.2, 25.04)},
        ],
        "Cooch Behar": [
            {"name": "Torsa River", "type": "river", "bbox": (89.39, 26.28, 89.51, 26.36)},
        ],
        "Jalpaiguri": [
            {"name": "Teesta River", "type": "river", "bbox": (88.67, 26.48, 88.79, 26.56)},
        ],
        "Alipurduar": [
            {"name": "Torsa River area", "type": "river", "bbox": (89.46, 26.45, 89.58, 26.53)},
        ],
        "Bankura": [
            {"name": "Dwarakeswar River", "type": "river", "bbox": (87.01, 23.19, 87.13, 23.27)},
        ],
        "Midnapore (Medinipur)": [
            {"name": "Kangsabati River", "type": "river", "bbox": (87.26, 22.38, 87.38, 22.46)},
        ],
        "Haldia": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.0, 22.02, 88.12, 22.1)},
            {"name": "Rupnarayan River", "type": "river", "bbox": (88.0, 22.02, 88.12, 22.1)},
        ],
        "Diamond Harbour": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.13, 22.15, 88.25, 22.23)},
        ],
        "Nabadwip": [
            {"name": "Ganga", "type": "river", "bbox": (88.31, 23.37, 88.43, 23.45)},
            {"name": "Bhagirathi-Jalangi confluence", "type": "river", "bbox": (88.31, 23.37, 88.43, 23.45)},
        ],
        "Krishnanagar": [
            {"name": "Jalangi River", "type": "river", "bbox": (88.44, 23.36, 88.56, 23.44)},
        ],
        "Barrackpore": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.31, 22.72, 88.43, 22.8)},
        ],
        "Hooghly/Chinsurah": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.25, 22.45, 88.37, 22.53)},
        ],
        "Chandernagore": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.28, 22.45, 88.4, 22.53)},
        ],
        "Serampore": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.28, 22.71, 88.4, 22.79)},
        ],
        "Balurghat": [
            {"name": "Atrai River", "type": "river", "bbox": (88.71, 25.18, 88.83, 25.26)},
        ],
        "Raiganj": [
            {"name": "Kulik River", "type": "river", "bbox": (88.06, 25.58, 88.18, 25.66)},
        ],
        "Jangipur": [
            {"name": "Bhagirathi River", "type": "river", "bbox": (88.28, 22.48, 88.4, 22.56)},
        ],
        "Katwa": [
            {"name": "Ajay-Bhagirathi confluence", "type": "river", "bbox": (88.24, 22.56, 88.36, 22.64)},
        ],
        "Tamluk": [
            {"name": "Rupnarayan River", "type": "river", "bbox": (88.37, 22.45, 88.49, 22.53)},
        ],
        "Jhargram": [
            {"name": "Subarnarekha", "type": "river", "bbox": (88.34, 22.59, 88.46, 22.67)},
            {"name": "Kangsabati", "type": "river", "bbox": (88.34, 22.59, 88.46, 22.67)},
        ],
        "Bishnupur": [
            {"name": "Dwarakeswar area", "type": "river", "bbox": (93.72, 24.59, 93.84, 24.67)},
        ],
        "Ranaghat": [
            {"name": "Churni River", "type": "river", "bbox": (88.28, 22.59, 88.4, 22.67)},
        ],
        "Shantipur": [
            {"name": "Hooghly", "type": "river", "bbox": (88.27, 22.57, 88.39, 22.65)},
        ],
        "Kalyani": [
            {"name": "Hooghly", "type": "river", "bbox": (88.36, 22.57, 88.48, 22.65)},
        ],
        "Basirhat": [
            {"name": "Ichamati River", "type": "river", "bbox": (88.39, 22.5, 88.51, 22.58)},
        ],
        "Bangaon": [
            {"name": "Ichamati River", "type": "river", "bbox": (88.23, 22.51, 88.35, 22.59)},
        ],
        "Budge Budge": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.23, 22.54, 88.35, 22.62)},
        ],
        "Uluberia": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.29, 22.54, 88.41, 22.62)},
        ],
        "Rishra": [
            {"name": "Hooghly River", "type": "river", "bbox": (88.37, 22.61, 88.49, 22.69)},
        ],
        "Bolpur/Santiniketan": [
            {"name": "Ajay", "type": "river", "bbox": (88.27, 22.5, 88.39, 22.58)},
            {"name": "Kopai", "type": "river", "bbox": (88.27, 22.5, 88.39, 22.58)},
        ],
        "Suri": [
            {"name": "Mayurakshi", "type": "river", "bbox": (88.35, 22.45, 88.47, 22.53)},
        ],
        "Rampurhat": [
            {"name": "Mayurakshi", "type": "river", "bbox": (88.26, 22.48, 88.38, 22.56)},
        ],
        "Purulia": [
            {"name": "Kangsabati", "type": "river", "bbox": (86.3, 23.29, 86.42, 23.37)},
            {"name": "Kumari", "type": "river", "bbox": (86.3, 23.29, 86.42, 23.37)},
        ],
        "Ghatal": [
            {"name": "Shilabati River", "type": "river", "bbox": (88.29, 22.56, 88.41, 22.64)},
        ],
        "Arambagh": [
            {"name": "Damodar", "type": "lake", "bbox": (88.42, 22.54, 88.48, 22.58)},
            {"name": "Dwarakeswar", "type": "river", "bbox": (88.39, 22.52, 88.51, 22.6)},
        ],
        "Kharagpur": [
            {"name": "Kangsabati", "type": "river", "bbox": (88.33, 22.61, 88.45, 22.69)},
            {"name": "Keleghai", "type": "river", "bbox": (88.33, 22.61, 88.45, 22.69)},
        ],
        "Kalimpong": [
            {"name": "Teesta", "type": "river", "bbox": (88.27, 22.53, 88.39, 22.61)},
        ],
        "Kurseong": [
            {"name": "Teesta area", "type": "river", "bbox": (88.36, 22.56, 88.48, 22.64)},
            {"name": "Mahananda", "type": "river", "bbox": (88.36, 22.56, 88.48, 22.64)},
        ],
        "Mirik": [
            {"name": "Mirik", "type": "river", "bbox": (88.24, 22.54, 88.36, 22.62)},
            {"name": "Sumendu Lake", "type": "lake", "bbox": (88.27, 22.56, 88.33, 22.6)},
        ],
        "Dinhata": [
            {"name": "Torsa", "type": "river", "bbox": (88.29, 22.58, 88.41, 22.66)},
        ],
        "Sundarbans area": [
            {"name": "Hooghly distributaries", "type": "river", "bbox": (88.24, 22.52, 88.36, 22.6)},
            {"name": "Matla", "type": "river", "bbox": (88.24, 22.52, 88.36, 22.6)},
            {"name": "Gosaba", "type": "river", "bbox": (88.24, 22.52, 88.36, 22.6)},
        ],
    },

    # =========================================================================
    # 8 UNION TERRITORIES
    # =========================================================================

    # -------------------------------------------------------------------------
    # 29. ANDAMAN & NICOBAR ISLANDS
    # -------------------------------------------------------------------------
    "Andaman & Nicobar Islands": {
        "Port Blair": [
            {"name": "Small streams", "type": "river", "bbox": (92.68, 11.63, 92.8, 11.71)},
            {"name": "coastal", "type": "lake", "bbox": (92.71, 11.65, 92.77, 11.69)},
        ],
        "Diglipur": [
            {"name": "Small rivers", "type": "river", "bbox": (92.94, 13.23, 93.06, 13.31)},
        ],
        "Mayabunder": [
            {"name": "Streams", "type": "river", "bbox": (92.84, 12.81, 92.96, 12.89)},
        ],
        "Rangat": [
            {"name": "Streams", "type": "river", "bbox": (92.86, 12.46, 92.98, 12.54)},
        ],
    },

    # -------------------------------------------------------------------------
    # 30. CHANDIGARH
    # -------------------------------------------------------------------------
    "Chandigarh": {
        "Chandigarh": [
            {"name": "Ghaggar River", "type": "river", "bbox": (76.72, 30.69, 76.84, 30.77)},
            {"name": "Patiali-ki-Rao", "type": "river", "bbox": (76.72, 30.69, 76.84, 30.77)},
            {"name": "Sukhna Choe", "type": "river", "bbox": (76.72, 30.69, 76.84, 30.77)},
            {"name": "Sukhna Lake", "type": "lake", "bbox": (76.75, 30.71, 76.81, 30.75)},
        ],
    },

    # -------------------------------------------------------------------------
    # 31. DADRA & NAGAR HAVELI AND DAMAN & DIU
    # -------------------------------------------------------------------------
    "Dadra & Nagar Haveli and Daman & Diu": {
        "Silvassa": [
            {"name": "Damanganga River", "type": "lake", "bbox": (72.98, 20.25, 73.04, 20.29)},
            {"name": "Dudhni Lake", "type": "lake", "bbox": (72.98, 20.25, 73.04, 20.29)},
        ],
        "Daman": [
            {"name": "Damanganga River mouth", "type": "lake", "bbox": (72.82, 20.39, 72.88, 20.43)},
        ],
        "Diu": [
            {"name": "coast", "type": "river", "bbox": (70.92, 20.67, 71.04, 20.75)},
        ],
    },

    # -------------------------------------------------------------------------
    # 32. DELHI (NCT)
    # -------------------------------------------------------------------------
    "Delhi (NCT)": {
        "New Delhi": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.15, 28.57, 77.27, 28.65)},
        ],
        "Old Delhi": [
            {"name": "Yamuna River", "type": "river", "bbox": (77.17, 28.62, 77.29, 28.7)},
        ],
    },

    # -------------------------------------------------------------------------
    # 33. JAMMU & KASHMIR
    # -------------------------------------------------------------------------
    "Jammu & Kashmir": {
        "Srinagar": [
            {"name": "Jhelum River", "type": "river", "bbox": (74.74, 34.04, 74.86, 34.12)},
            {"name": "Dal Lake", "type": "lake", "bbox": (74.77, 34.06, 74.83, 34.1)},
            {"name": "Nigeen Lake", "type": "lake", "bbox": (74.77, 34.06, 74.83, 34.1)},
        ],
        "Jammu": [
            {"name": "Tawi River", "type": "river", "bbox": (74.81, 32.69, 74.93, 32.77)},
        ],
        "Anantnag": [
            {"name": "Lidder River", "type": "river", "bbox": (75.09, 33.69, 75.21, 33.77)},
            {"name": "Jhelum River", "type": "river", "bbox": (75.09, 33.69, 75.21, 33.77)},
        ],
        "Baramulla": [
            {"name": "Jhelum River", "type": "river", "bbox": (74.28, 34.16, 74.4, 34.24)},
        ],
        "Kathua": [
            {"name": "Ujh River", "type": "river", "bbox": (75.45, 32.35, 75.57, 32.43)},
            {"name": "Basantar River", "type": "river", "bbox": (75.45, 32.35, 75.57, 32.43)},
        ],
        "Udhampur": [
            {"name": "Devak", "type": "river", "bbox": (75.08, 32.88, 75.2, 32.96)},
            {"name": "Tawi tributaries", "type": "river", "bbox": (75.08, 32.88, 75.2, 32.96)},
        ],
        "Rajouri": [
            {"name": "Ans", "type": "river", "bbox": (74.25, 33.34, 74.37, 33.42)},
            {"name": "Tawi tributaries", "type": "river", "bbox": (74.25, 33.34, 74.37, 33.42)},
        ],
        "Poonch": [
            {"name": "Poonch River", "type": "river", "bbox": (74.03, 33.73, 74.15, 33.81)},
        ],
        "Sopore": [
            {"name": "Jhelum River", "type": "river", "bbox": (74.41, 34.26, 74.53, 34.34)},
            {"name": "Wular Lake", "type": "lake", "bbox": (74.44, 34.28, 74.5, 34.32)},
        ],
        "Pahalgam": [
            {"name": "Lidder River", "type": "river", "bbox": (75.25, 33.97, 75.37, 34.05)},
        ],
        "Kishtwar": [
            {"name": "Chenab River", "type": "river", "bbox": (75.71, 33.27, 75.83, 33.35)},
        ],
        "Doda": [
            {"name": "Chenab area", "type": "river", "bbox": (75.49, 33.11, 75.61, 33.19)},
        ],
        "Kulgam": [
            {"name": "Jhelum tributaries", "type": "river", "bbox": (74.96, 33.59, 75.08, 33.67)},
        ],
        "Shopian": [
            {"name": "Jhelum tributaries", "type": "river", "bbox": (74.77, 33.68, 74.89, 33.76)},
        ],
        "Pulwama": [
            {"name": "Jhelum area", "type": "river", "bbox": (74.83, 33.83, 74.95, 33.91)},
        ],
        "Budgam": [
            {"name": "Jhelum area", "type": "river", "bbox": (74.67, 33.89, 74.79, 33.97)},
        ],
        "Ganderbal": [
            {"name": "Sindh River", "type": "river", "bbox": (74.72, 34.19, 74.84, 34.27)},
            {"name": "Manasbal Lake", "type": "lake", "bbox": (74.75, 34.21, 74.81, 34.25)},
        ],
        "Bandipora": [
            {"name": "Wular Lake", "type": "lake", "bbox": (74.72, 34.05, 74.78, 34.09)},
        ],
        "Kupwara": [
            {"name": "Kishanganga", "type": "river", "bbox": (74.2, 34.49, 74.32, 34.57)},
        ],
        "Sonmarg": [
            {"name": "Sindh River", "type": "river", "bbox": (74.66, 34.0, 74.78, 34.08)},
        ],
        "Verinag": [
            {"name": "Jhelum River", "type": "river", "bbox": (74.71, 34.07, 74.83, 34.15)},
            {"name": "spring origin", "type": "river", "bbox": (74.71, 34.07, 74.83, 34.15)},
        ],
        "Akhnoor": [
            {"name": "Chenab River", "type": "river", "bbox": (74.68, 34.04, 74.8, 34.12)},
        ],
        "Ramban": [
            {"name": "Chenab River", "type": "river", "bbox": (75.18, 33.2, 75.3, 33.28)},
        ],
        "Reasi": [
            {"name": "Chenab River", "type": "river", "bbox": (74.77, 33.04, 74.89, 33.12)},
        ],
    },

    # -------------------------------------------------------------------------
    # 34. LADAKH
    # -------------------------------------------------------------------------
    "Ladakh": {
        "Leh": [
            {"name": "Indus River", "type": "river", "bbox": (77.52, 34.12, 77.64, 34.2)},
        ],
        "Kargil": [
            {"name": "Suru River", "type": "river", "bbox": (76.07, 34.51, 76.19, 34.59)},
        ],
        "Diskit (Nubra)": [
            {"name": "Nubra River", "type": "river", "bbox": (77.5, 34.03, 77.62, 34.11)},
            {"name": "Shyok River", "type": "river", "bbox": (77.5, 34.03, 77.62, 34.11)},
        ],
        "Padum (Zanskar)": [
            {"name": "Zanskar River", "type": "river", "bbox": (77.53, 34.02, 77.65, 34.1)},
        ],
        "Dras": [
            {"name": "Dras River", "type": "river", "bbox": (77.6, 34.12, 77.72, 34.2)},
        ],
        "Nyoma": [
            {"name": "Indus River", "type": "river", "bbox": (78.59, 33.2, 78.71, 33.28)},
        ],
        "Hanle": [
            {"name": "Indus tributaries", "type": "river", "bbox": (78.91, 32.74, 79.03, 32.82)},
        ],
        "Turtuk": [
            {"name": "Shyok River", "type": "river", "bbox": (77.49, 34.13, 77.61, 34.21)},
        ],
    },

    # -------------------------------------------------------------------------
    # 35. LAKSHADWEEP
    # -------------------------------------------------------------------------
    "Lakshadweep": {
        "Kavaratti": [
            {"name": "Lagoon only", "type": "lake", "bbox": (72.61, 10.55, 72.67, 10.59)},
        ],
        "Minicoy": [
            {"name": "Lagoon only", "type": "lake", "bbox": (73.02, 8.25, 73.08, 8.29)},
        ],
        "Agatti": [
            {"name": "Lagoon only", "type": "lake", "bbox": (72.16, 10.84, 72.22, 10.88)},
        ],
    },

    # -------------------------------------------------------------------------
    # 36. PUDUCHERRY
    # -------------------------------------------------------------------------
    "Puducherry": {
        "Puducherry (Pondicherry)": [
            {"name": "Chunnambar River", "type": "river", "bbox": (79.77, 11.89, 79.89, 11.97)},
            {"name": "Sankaraparani", "type": "river", "bbox": (79.77, 11.89, 79.89, 11.97)},
            {"name": "Ousteri", "type": "river", "bbox": (79.77, 11.89, 79.89, 11.97)},
            {"name": "Oussudu Lake", "type": "lake", "bbox": (79.8, 11.91, 79.86, 11.95)},
        ],
        "Karaikal": [
            {"name": "Kaveri distributaries", "type": "river", "bbox": (79.78, 10.88, 79.9, 10.96)},
            {"name": "Arasalar", "type": "river", "bbox": (79.78, 10.88, 79.9, 10.96)},
            {"name": "Adappar", "type": "river", "bbox": (79.78, 10.88, 79.9, 10.96)},
        ],
        "Mahe": [
            {"name": "Mahe River", "type": "river", "bbox": (75.48, 11.66, 75.6, 11.74)},
            {"name": "Mayyazhi Puzha", "type": "river", "bbox": (75.48, 11.66, 75.6, 11.74)},
        ],
        "Yanam": [
            {"name": "Godavari distributary", "type": "river", "bbox": (82.16, 16.69, 82.28, 16.77)},
            {"name": "Coringa", "type": "river", "bbox": (82.16, 16.69, 82.28, 16.77)},
        ],
    },

}


# =============================================================================
# NAVIGATION FUNCTIONS
# =============================================================================

def get_states():
    """
    Return a sorted list of all state/UT names in the geo database.

    Returns:
        list[str]: Alphabetically sorted list of Indian state/UT names.
    """
    return sorted(INDIA_GEO_DATABASE.keys())


def get_cities(state):
    """
    Return a sorted list of city names within a given state/UT.

    Args:
        state (str): Name of the Indian state or Union Territory.

    Returns:
        list[str]: Alphabetically sorted list of city names.

    Raises:
        KeyError: If the state is not found in the database.
    """
    if state not in INDIA_GEO_DATABASE:
        raise KeyError(
            f"State '{state}' not found in database. "
            f"Available states: {', '.join(get_states())}"
        )
    return sorted(INDIA_GEO_DATABASE[state].keys())


def get_water_bodies(state, city):
    """
    Return a list of water body records for a given state and city.

    Each record is a dict with keys: name, type, bbox.

    Args:
        state (str): Name of the Indian state or Union Territory.
        city (str): Name of the city within that state.

    Returns:
        list[dict]: List of water body dictionaries, each containing:
            - name (str): Name of the water body
            - type (str): "river" or "lake"
            - bbox (tuple): (lon_min, lat_min, lon_max, lat_max)

    Raises:
        KeyError: If the state or city is not found in the database.
    """
    if state not in INDIA_GEO_DATABASE:
        raise KeyError(
            f"State '{state}' not found in database. "
            f"Available states: {', '.join(get_states())}"
        )
    cities = INDIA_GEO_DATABASE[state]
    if city not in cities:
        raise KeyError(
            f"City '{city}' not found in state '{state}'. "
            f"Available cities: {', '.join(sorted(cities.keys()))}"
        )
    return list(cities[city])


def get_rivers_only(state, city):
    """
    Return only river-type water bodies for a given state and city.

    Filters out lakes, reservoirs, and ponds — returns only entries
    where type == "river".  Used by RIVER_ONLY_MODE to ensure the
    entire pipeline operates exclusively on rivers.

    Args:
        state (str): Name of the Indian state or Union Territory.
        city (str): Name of the city within that state.

    Returns:
        list[str]: Names of river water bodies only.
    """
    all_wb = get_water_bodies(state, city)
    rivers = [wb["name"] for wb in all_wb if wb.get("type", "").lower() == "river"]
    if not rivers:
        # Fallback: return all if no rivers found (some entries may lack type)
        rivers = [wb["name"] for wb in all_wb]
    return rivers


def get_roi(state, city, water_body_name):
    """
    Build and return a Region-of-Interest dictionary compatible with the
    Aqua-Sentinel AI config.py ROI format.

    Args:
        state (str): Name of the Indian state or Union Territory.
        city (str): Name of the city within that state.
        water_body_name (str): Exact name of the water body.

    Returns:
        dict: ROI dictionary with keys:
            - name (str): Composite label "<water_body>, <city>"
            - state (str): State name
            - city (str): City name
            - water_body (str): Water body name
            - water_type (str): "river" or "lake"
            - lon_min (float): Western longitude boundary
            - lat_min (float): Southern latitude boundary
            - lon_max (float): Eastern longitude boundary
            - lat_max (float): Northern latitude boundary

    Raises:
        KeyError: If the state, city, or water body is not found.
    """
    water_bodies = get_water_bodies(state, city)
    for wb in water_bodies:
        if wb["name"] == water_body_name:
            lon_min, lat_min, lon_max, lat_max = wb["bbox"]
            return {
                "name": f"{water_body_name}, {city}",
                "state": state,
                "city": city,
                "water_body": water_body_name,
                "water_type": wb["type"],
                "lon_min": lon_min,
                "lat_min": lat_min,
                "lon_max": lon_max,
                "lat_max": lat_max,
            }
    available = [wb["name"] for wb in water_bodies]
    raise KeyError(
        f"Water body '{water_body_name}' not found in {city}, {state}. "
        f"Available water bodies: {', '.join(available)}"
    )


def search_water_body(query):
    """
    Perform a fuzzy (case-insensitive substring) search across all water bodies
    in the database.

    Args:
        query (str): Search string to match against water body names.

    Returns:
        list[dict]: List of matching results, each containing:
            - name (str): Water body name
            - type (str): "river" or "lake"
            - city (str): City where the water body is located
            - state (str): State where the city is located
            - bbox (tuple): Bounding box coordinates

        Results are sorted alphabetically by water body name.
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return []

    matches = []
    for state, cities in INDIA_GEO_DATABASE.items():
        for city, water_bodies in cities.items():
            for wb in water_bodies:
                if query_lower in wb["name"].lower():
                    matches.append({
                        "name": wb["name"],
                        "type": wb["type"],
                        "city": city,
                        "state": state,
                        "bbox": wb["bbox"],
                    })

    matches.sort(key=lambda m: m["name"])
    return matches


def get_nearest_location(lat, lon):
    """
    Find the nearest known water body to a given latitude/longitude coordinate
    using the Haversine formula for great-circle distance.

    Loops through every water body in the database, computes the distance from
    (lat, lon) to the centre of each water body's bounding box, and returns the
    closest match.

    Args:
        lat (float): Latitude in decimal degrees (e.g. 28.61 for Delhi).
        lon (float): Longitude in decimal degrees (e.g. 77.23 for Delhi).

    Returns:
        dict: Dictionary with keys:
            - state (str): State/UT name
            - city (str): City name
            - water_body (str): Name of the nearest water body
            - water_type (str): "river" or "lake"
            - distance_km (float): Distance in kilometres (rounded to 2 dp)
            - locality_name (str): Formatted string
              "Near <water_body>, <city>, <state>"

        Returns None if the database is empty.
    """

    def _haversine(lat1, lon1, lat2, lon2):
        """Return distance in km between two points on Earth."""
        R = 6371.0  # Earth radius in kilometres
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    best = None
    best_dist = float("inf")

    for state, cities in INDIA_GEO_DATABASE.items():
        for city, water_bodies in cities.items():
            for wb in water_bodies:
                lon_min, lat_min, lon_max, lat_max = wb["bbox"]
                centre_lat = (lat_min + lat_max) / 2.0
                centre_lon = (lon_min + lon_max) / 2.0
                dist = _haversine(lat, lon, centre_lat, centre_lon)
                if dist < best_dist:
                    best_dist = dist
                    best = {
                        "state": state,
                        "city": city,
                        "water_body": wb["name"],
                        "water_type": wb["type"],
                        "distance_km": round(dist, 2),
                        "locality_name": f"Near {wb['name']}, {city}, {state}",
                    }

    return best


# =============================================================================
# UTILITY / SUMMARY FUNCTIONS
# =============================================================================

def summary():
    """
    Print a human-readable summary of the entire geo database.

    Returns:
        str: Formatted multi-line summary string.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("  Aqua-Sentinel AI - Geographic Hierarchy Summary")
    lines.append("=" * 70)

    total_states = 0
    total_cities = 0
    total_water_bodies = 0

    for state in sorted(INDIA_GEO_DATABASE.keys()):
        cities = INDIA_GEO_DATABASE[state]
        total_states += 1
        lines.append(f"\n  {state}")
        lines.append("  " + "-" * (len(state)))
        for city in sorted(cities.keys()):
            total_cities += 1
            water_bodies = cities[city]
            wb_names = ", ".join(wb["name"] for wb in water_bodies)
            total_water_bodies += len(water_bodies)
            lines.append(f"    {city}: {wb_names}")

    lines.append("\n" + "=" * 70)
    lines.append(
        f"  Total: {total_states} states/UTs, {total_cities} cities, "
        f"{total_water_bodies} water bodies"
    )
    lines.append("=" * 70)

    output = "\n".join(lines)
    return output


# =============================================================================
# MODULE SELF-TEST
# =============================================================================

if __name__ == "__main__":
    print(summary())
    print()

    # Demonstrate core navigation functions
    print("--- States/UTs ---")
    for s in get_states():
        print(f"  {s}")

    print(f"\n--- Total states/UTs: {len(get_states())} ---")

    print("\n--- Cities in Maharashtra ---")
    for c in get_cities("Maharashtra"):
        print(f"  {c}")

    print("\n--- Water Bodies in Mumbai, Maharashtra ---")
    for wb in get_water_bodies("Maharashtra", "Mumbai"):
        print(f"  {wb['name']} ({wb['type']}) -> bbox: {wb['bbox']}")

    print("\n--- Search: 'yamuna' ---")
    results = search_water_body("yamuna")
    for r in results:
        print(f"  {r['name']} in {r['city']}, {r['state']} ({r['type']})")

    print("\n--- Search: 'lake' ---")
    results = search_water_body("lake")
    for r in results:
        print(f"  {r['name']} in {r['city']}, {r['state']} ({r['type']})")

    print("\n--- Nearest location to (28.61, 77.23) [Delhi area] ---")
    nearest = get_nearest_location(28.61, 77.23)
    if nearest:
        for k, v in nearest.items():
            print(f"  {k}: {v}")

    print("\n--- Nearest location to (19.07, 72.87) [Mumbai area] ---")
    nearest = get_nearest_location(19.07, 72.87)
    if nearest:
        for k, v in nearest.items():
            print(f"  {k}: {v}")

    print("\n--- Nearest location to (34.08, 74.80) [Srinagar area] ---")
    nearest = get_nearest_location(34.08, 74.80)
    if nearest:
        for k, v in nearest.items():
            print(f"  {k}: {v}")
