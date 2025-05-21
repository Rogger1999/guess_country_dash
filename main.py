import json
import random
import pandas as pd
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc

###############################################################################
# 1) LOAD DATA
###############################################################################
# Fix file paths to match actual files
with open("europe.json", "r", encoding="utf-8") as f:
    europe_data_raw = json.load(f)
with open("asia_oceania.json", "r", encoding="utf-8") as f:
    asia_oceania_data_raw = json.load(f)
with open("africa.json", "r", encoding="utf-8") as f:
    africa_data_raw = json.load(f)
with open("north_america.json", "r", encoding="utf-8") as f:
    north_america_data_raw = json.load(f)
with open("south_america.json", "r", encoding="utf-8") as f:
    south_america_data_raw = json.load(f)
    
# Load GeoJSON data for country shapes
with open("geo.json", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Create country name mappings (German to English and vice versa)
# This is a simplified mapping, expand as needed
COUNTRY_MAP = {
    "Italien": "Italy",
    "Deutschland": "Germany",
    "Spanien": "Spain",
    "Frankreich": "France",
    "Portugal": "Portugal",
    "Belgien": "Belgium",
    "Niederlande": "Netherlands",
    "Vereinigtes Königreich": "United Kingdom",
    "Grossbritannien": "United Kingdom",
    "Irland": "Ireland",
    "Island": "Iceland",
    "Norwegen": "Norway",
    "Schweden": "Sweden",
    "Finnland": "Finland",
    "Dänemark": "Denmark",
    "Schweiz": "Switzerland",
    "Italien": "Italy",
    "Österreich": "Austria",
    "Ungarn": "Hungary",
    "Tschechien": "Czech Republic",
    "Slowakei": "Slovakia",
    "Polen": "Poland",
    "Russland (Teil)": "Russia",
    "Belarus": "Belarus",
    "Ukraine": "Ukraine",
    "Moldova": "Moldova",
    "Rumänien": "Romania",
    "Bulgarien": "Bulgaria",
    "Türkei (Teil)": "Turkey",
    "Slowenien": "Slovenia",
    "Kroatien": "Croatia",
    "Bosnien-Herzegowina": "Bosnia and Herzegovina",
    "Serbien": "Serbia",
    "Nordmazedonien": "North Macedonia",
    "Montenegro": "Montenegro",
    "Kosovo": "Kosovo",  # may require feature-id "XKX"
    "Albanien": "Albania",
    "Griechenland": "Greece",
    "Malta": "Malta",
    "Andorra": "Andorra",
    "Monaco": "Monaco",
    "Liechtenstein": "Liechtenstein",
    "Vatikanstadt": "Vatican City",
    "San Marino": "San Marino",
    "Luxemburg": "Luxembourg",
    "Estland": "Estonia",
    "Lettland": "Latvia",
    "Litauen": "Lithuania",
    # Add more mappings as needed
}

COUNTRY_MAP.update({
    "Äthiopien": "Ethiopia",
    "Tunesien": "Tunisia",
    "Syrien": "Syria",
    "Bangladesch": "Bangladesh",
    "Pakistan": "Pakistan",
    "Madagaskar": "Madagascar",
    "Mali": "Mali",
    "Südafrika": "South Africa",
    "Brasilien": "Brazil",
    "Kolumbien": "Colombia",
    "Argentinien": "Argentina",
    "Bolivien": "Bolivia",
    "Irak": "Iraq",
    "Ägypten": "Egypt",
    "Peru": "Peru",
    "Iran": "Iran",
    "Afghanistan": "Afghanistan",
    "Korea": "South Korea"
})

COUNTRY_MAP.update({
    # ...existing entries...
    "Australien": "Australia",
    "Neuseeland": "New Zealand",
    "Kanada": "Canada",
    "USA": "United States",
    "Vereinigte Staaten": "United States",
    "Mexiko": "Mexico"
})

COUNTRY_MAP.update({
    # ...existing entries...
    "Venezuela": "Venezuela",
    "Ecuador": "Ecuador",
    "Chile": "Chile",
    "Ghana": "Ghana",
    "Kongo": "Democratic Republic of the Congo",
    "Somalia": "Somalia",
    "Eritrea": "Eritrea"
})

COUNTRY_MAP.update({
    "Kuba": "Cuba",
    "Jamaika": "Jamaica",
    "Namibia": "Namibia",
    "Libyen": "Libya",
    "Marokko": "Morocco",
    "Nigeria": "Nigeria",
    "Kenia": "Kenya",
    "Algerien": "Algeria",
    "Indonesien": "Indonesia",
    "China": "China",
    "Thailand": "Thailand",
    "Philippinen": "Philippines",
    "Indien": "India",
    "Japan": "Japan",
    "Malaysia": "Malaysia",
    "Saudi-Arabien": "Saudi Arabia"
})

# Define European microstates
# Names as they appear in df['country'] (likely German from your JSONs)
EUROPEAN_MICROSTATES_DF_KEYS = ["Andorra", "Monaco", "Liechtenstein", "Vatikanstadt", "San Marino", "Kosovo", "Malta"]
# Corresponding English names for checking against the 'eng_name' variable
EUROPEAN_MICROSTATES_ENGLISH_CHECK = ["Andorra", "Monaco", "Liechtenstein", "Vatican City", "San Marino", "Kosovo", "Malta"]

# Create a reverse lookup from English to German
REVERSE_COUNTRY_MAP = {v: k for k, v in COUNTRY_MAP.items()}

# Create mapping from country code to GeoJSON feature
country_code_to_feature = {}
for feature in geojson_data['features']:
    if 'id' in feature and feature['id'] not in country_code_to_feature:
        country_code_to_feature[feature['id']] = feature

# Additional mapping from country name to country code
COUNTRY_TO_CODE = {
    "Italy": "ITA",
    "Germany": "DEU",
    "Spain": "ESP",
    "France": "FRA",
    "Portugal": "PRT",
    "Switzerland": "CHE",
    "Austria": "AUT",
    "Belgium": "BEL",
    "Netherlands": "NLD",
    "United Kingdom": "GBR",
    "Ireland": "IRL",
    "Australia": "AUS",
    "New Zealand": "NZL",
    # Add more as needed
}

COUNTRY_TO_CODE.update({
    "Iceland": "ISL",
    "Norway": "NOR",
    "Sweden": "SWE",
    "Finland": "FIN",
    "Denmark": "DNK",
    "Luxembourg": "LUX",
    "Russia": "RUS",
    "Belarus": "BLR",
    "Ukraine": "UKR",
    "Moldova": "MDA",
    "Romania": "ROU",
    "Bulgaria": "BGR",
    "Turkey": "TUR",
    "Slovenia": "SVN",
    "Croatia": "HRV",
    "Bosnia and Herzegovina": "BIH",
    "Serbia": "SRB",
    "North Macedonia": "MKD",
    "Montenegro": "MNE",
    "Kosovo": "XKX",            # check your geo.json feature id
    "Albania": "ALB",
    "Greece": "GRC",
    "Malta": "MLT",
    "Andorra": "AND",
    "Monaco": "MCO",
    "Liechtenstein": "LIE",
    "Vatican City": "VAT",
    "San Marino": "SMR",
    "Poland": "POL",
    "Lithuania": "LTU",
    "Latvia": "LVA",
    "Estonia": "EST",
    "Czech Republic": "CZE",
    "Slovakia": "SVK",
    "Hungary": "HUN",
})

COUNTRY_TO_CODE.update({
    "Ethiopia": "ETH",
    "Tunisia": "TUN",
    "Syria": "SYR",
    "Bangladesh": "BGD",
    "Pakistan": "PAK",
    "Madagascar": "MDG",
    "Mali": "MLI",
    "South Africa": "ZAF",
    "Brazil": "BRA",
    "Colombia": "COL",
    "Argentina": "ARG",
    "Bolivia": "BOL",
    "Iraq": "IRQ",
    "Egypt": "EGY",
    "Peru": "PER",
    "Iran": "IRN",
    "Afghanistan": "AFG",
    "South Korea": "KOR"
})

COUNTRY_TO_CODE.update({
    # ...existing entries...
    "Canada": "CAN",
    "United States": "USA",
    "Mexico": "MEX"
})

COUNTRY_TO_CODE.update({
    # ...existing entries...
    "Venezuela": "VEN",
    "Ecuador": "ECU",
    "Chile": "CHL",
    "Ghana": "GHA",
    "Democratic Republic of the Congo": "COD",
    "Somalia": "SOM",
    "Eritrea": "ERI"
})

COUNTRY_TO_CODE.update({
    "Cuba": "CUB",
    "Jamaica": "JAM",
    "Namibia": "NAM",
    "Libya": "LBY",
    "Morocco": "MAR",
    "Nigeria": "NGA",
    "Kenya": "KEN",
    "Algeria": "DZA",
    "Indonesia": "IDN",
    "China": "CHN",
    "Thailand": "THA",
    "Philippines": "PHL",
    "India": "IND",
    "Japan": "JPN",
    "Malaysia": "MYS",
    "Saudi Arabia": "SAU"
})

def extract_country_coordinates(country_name):
    """Extract coordinates for a country from GeoJSON data"""
    # Try to map German name to English
    english_name = COUNTRY_MAP.get(country_name, country_name)
    
    # Get country code
    country_code = COUNTRY_TO_CODE.get(english_name)
    
    if not country_code or country_code not in country_code_to_feature:
        # Return dummy coordinates if no match found
        return {"type": "polygon", "points": [[0, 0]]}
    
    feature = country_code_to_feature[country_code]
    
    if 'geometry' not in feature:
        return {"type": "polygon", "points": [[0, 0]]}
    
    geometry = feature['geometry']
    geo_type = geometry['type'].lower()
    
    if geo_type == 'polygon':
        # Extract first polygon's coordinates
        coordinates = geometry['coordinates'][0]  # First polygon
        # Convert [lon, lat] to [lat, lon] format
        points = [[coord[1], coord[0]] for coord in coordinates]
        return {"type": "polygon", "points": points}
    
    elif geo_type == 'multipolygon':
        # Include all sub‐polygons (e.g. Australia mainland + Tasmania)
        points = []
        for polygon in geometry['coordinates']:
            for ring in polygon:
                points.extend([[coord[1], coord[0]] for coord in ring])
        return {"type": "polygon", "points": points}
    
    return {"type": "polygon", "points": [[0, 0]]}

# Transform raw data into the expected format
def transform_countries_data(countries_list):
    data = []
    coords = {}
    
    for country_obj in countries_list:
        country_name = country_obj["country"]
        data.append(country_name)
        
        # Get coordinates from GeoJSON data
        coords[country_name] = extract_country_coordinates(country_name)
    
    return {"data": data, "coords": coords}

europe_data = transform_countries_data(europe_data_raw)
asia_data = transform_countries_data(asia_oceania_data_raw)
africa_data = transform_countries_data(africa_data_raw)

# Combine both North and South America into "americas_data"
americas_data_raw = north_america_data_raw + south_america_data_raw
americas_data = transform_countries_data(americas_data_raw)

# For oceania, we'll extract the countries from asia_oceania that are part of Oceania
# For now, let's just use Australia and New Zealand
oceania_countries = ["Australien", "Neuseeland"]
oceania_data_raw = [country for country in asia_oceania_data_raw if country["country"] in oceania_countries]
oceania_data = transform_countries_data(oceania_data_raw)

countries_data = {
    "regions": {
        "europe": europe_data,
        "asia": asia_data,
        "africa": africa_data,
        "americas": americas_data,
        "oceania": oceania_data
    }
}

###############################################################################
# 2) BUILD DATAFRAME
###############################################################################
data_rows = []

def add_category(cat_name, cat_data):
    feats = cat_data.get("data", [])
    coords = cat_data.get("coords", {})
    for feat in feats:
        info = coords.get(feat, {})
        geom_type = info.get("type", "polygon")  # Countries are mostly polygons
        points = info.get("points", [])
        data_rows.append({
            "category": cat_name,
            "country": feat,
            "geometry_type": geom_type,
            "geometry_points": points
        })

# Add each region
add_category("Europe", countries_data["regions"]["europe"])
add_category("Asia", countries_data["regions"]["asia"])
add_category("Africa", countries_data["regions"]["africa"])
add_category("Americas", countries_data["regions"]["americas"])
add_category("Oceania", countries_data["regions"]["oceania"])

df = pd.DataFrame(data_rows)

###############################################################################
# 3) DASH APP LAYOUT
###############################################################################
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    dcc.Store(id="store-mode", data=None),
    dcc.Store(id="store-selected-category", data=None),
    dcc.Store(id="store-countries-list", data=[]),
    dcc.Store(id="store-current-index", data=0),
    dcc.Store(id="store-current-country", data=None),
    dcc.Store(id="store-show-name", data=False),

    dbc.NavbarSimple(
        brand="Country Quiz App",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4"
    ),

    # SCREEN 0: Mode Selection
    dbc.Card(
        [
            dbc.CardHeader("Select Mode", className="bg-secondary text-white"),
            dbc.CardBody([
                dbc.Button("LEARN", id="mode-learning-button", n_clicks=0, color="primary", className="me-2"),
                dbc.Button("QUIZ", id="mode-quiz-button", n_clicks=0, color="secondary")
            ])
        ],
        id="mode-selection-card",
        style={"maxWidth": "600px", "margin": "0 auto 2rem auto", "display": "block"}
    ),

    # SCREEN 1: Category Selection
    dbc.Card(
        [
            dbc.CardHeader("Select Region", className="bg-secondary text-white"),
            dbc.CardBody([
                dcc.Dropdown(id="category-dropdown", style={"maxWidth": "300px"}),
                dbc.Button("Continue", id="category-next-button", n_clicks=0, color="success", className="mt-3")
            ])
        ],
        id="category-selection-card",
        style={"maxWidth": "600px", "margin": "0 auto 2rem auto", "display": "none"}
    ),

    # SCREEN 2A: Learn Mode
    dbc.Card(
        [
            dbc.CardHeader("Learn Countries", className="bg-secondary text-white"),
            dbc.CardBody([
                html.H3(id="country-name-display", className="text-center mb-4"),
                dcc.Graph(id="country-map", style={"height": "500px"}),
                html.Div(className="d-flex justify-content-center mt-3", children=[
                    dbc.Button("BACK", id="back-button", n_clicks=0, color="secondary", className="me-2"),
                    dbc.Button("NEXT", id="next-button", n_clicks=0, color="primary", className="me-2"),
                    dbc.Button("Return to Menu", id="learn-return-button", n_clicks=0, color="info")
                ])
            ])
        ],
        id="learn-card",
        style={"maxWidth": "900px", "margin": "0 auto 2rem auto", "display": "none"}
    ),

    # SCREEN 2B: Quiz Mode
    dbc.Card(
        [
            dbc.CardHeader("Country Quiz", className="bg-secondary text-white"),
            dbc.CardBody([
                html.H3(id="quiz-country-display", className="text-center mb-4"),
                dcc.Graph(id="quiz-map", style={"height": "500px"}),
                html.Div(className="d-flex justify-content-center mt-3", children=[
                    dbc.Button("SHOW", id="show-button", n_clicks=0, color="primary", className="me-2"),
                    dbc.Button("NEXT", id="quiz-next-button", n_clicks=0, color="success", className="me-2"),
                    dbc.Button("Return to Menu", id="quiz-return-button", n_clicks=0, color="info")
                ])
            ])
        ],
        id="quiz-card",
        style={"maxWidth": "900px", "margin": "0 auto 2rem auto", "display": "none"}
    )
], fluid=True)

###############################################################################
# 4) CALLBACKS FOR MODE SELECTION
###############################################################################
@app.callback(
    Output("store-mode", "data"),
    Input("mode-learning-button", "n_clicks"),
    Input("mode-quiz-button", "n_clicks")
)
def set_mode(n_learn, n_quiz):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trig_id == "mode-learning-button" and n_learn:
        return "learn"
    elif trig_id == "mode-quiz-button" and n_quiz:
        return "quiz"
    return no_update

###############################################################################
# 5) POPULATE CATEGORY DROPDOWN
###############################################################################
@app.callback(
    Output("category-dropdown", "options"),
    Input("store-mode", "data")
)
def populate_category(mode):
    if mode in ["learn", "quiz"]:
        return [
            {"label": "All Regions", "value": "All"},
            {"label": "Europe", "value": "Europe"},
            {"label": "Asia", "value": "Asia"},
            {"label": "Africa", "value": "Africa"},
            {"label": "Americas", "value": "Americas"},
            {"label": "Oceania", "value": "Oceania"},
        ]
    return []

###############################################################################
# 6) SET CATEGORY AND INITIALIZE COUNTRY LIST
###############################################################################
@app.callback(
    Output("store-selected-category", "data"),
    Output("store-countries-list", "data"),
    Output("store-current-index", "data"),
    Output("store-current-country", "data"),
    Input("category-next-button", "n_clicks"),
    Input("learn-return-button", "n_clicks"),
    Input("quiz-return-button", "n_clicks"),
    State("category-dropdown", "value"),
)
def set_category_and_initialize(n_next, n_learn_return, n_quiz_return, chosen_cat):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trig_id in ["learn-return-button", "quiz-return-button"]:
        # Reset everything when returning to menu
        return None, [], 0, None
    
    if trig_id == "category-next-button" and chosen_cat:
        # Get countries for the selected category
        if chosen_cat == "All":
            countries = df["country"].tolist()
        else:
            countries = df[df["category"] == chosen_cat]["country"].tolist()
        
        # Randomize order for quiz/learn
        random.shuffle(countries)
        
        # Set first country
        current_country = countries[0] if countries else None
        
        return chosen_cat, countries, 0, current_country
    
    return no_update, no_update, no_update, no_update

###############################################################################
# 7) NAVIGATION CALLBACKS (NEXT/BACK)
###############################################################################
@app.callback(
    Output("store-current-index", "data", allow_duplicate=True),
    Output("store-current-country", "data", allow_duplicate=True),
    Output("store-show-name", "data"),
    Input("next-button", "n_clicks"),
    Input("back-button", "n_clicks"),
    Input("quiz-next-button", "n_clicks"),
    Input("show-button", "n_clicks"),
    State("store-current-index", "data"),
    State("store-countries-list", "data"),
    prevent_initial_call=True
)
def navigate_countries(n_next, n_back, n_quiz_next, n_show, current_idx, countries_list):
    ctx = callback_context
    if not ctx.triggered or not countries_list:
        return no_update, no_update, no_update
    
    trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
    show_name = False
    
    if trig_id == "next-button" or trig_id == "quiz-next-button":
        new_idx = (current_idx + 1) % len(countries_list)
        new_country = countries_list[new_idx]
        return new_idx, new_country, show_name
    
    elif trig_id == "back-button":
        new_idx = (current_idx - 1) % len(countries_list)
        new_country = countries_list[new_idx]
        return new_idx, new_country, show_name
    
    elif trig_id == "show-button":
        show_name = True
        return current_idx, countries_list[current_idx], show_name
    
    return no_update, no_update, no_update

###############################################################################
# 8) DISPLAY COUNTRY NAME
###############################################################################
@app.callback(
    Output("country-name-display", "children"),
    Output("quiz-country-display", "children"),
    Input("store-current-country", "data"),
    Input("store-show-name", "data"),
    Input("store-mode", "data")
)
def display_country_name(current_country, show_name, mode):
    if not current_country:
        return "Select a region to start", ""
    
    if mode == "learn":
        return current_country, ""
    elif mode == "quiz":
        if show_name:
            return "", current_country
        else:
            return "", "?"
    
    return no_update, no_update

###############################################################################
# 9) SWITCH SCREENS
###############################################################################
@app.callback(
    Output("mode-selection-card", "style"),
    Output("category-selection-card", "style"),
    Output("learn-card", "style"),
    Output("quiz-card", "style"),
    Input("store-mode", "data"),
    Input("store-selected-category", "data")
)
def switch_screens(mode, selected_cat):
    if mode is None:
        return (
            {"maxWidth": "600px", "margin": "0 auto 2rem auto", "display": "block"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"}
        )
    if selected_cat is None:
        return (
            {"display": "none"},
            {"maxWidth": "600px", "margin": "0 auto 2rem auto", "display": "block"},
            {"display": "none"},
            {"display": "none"}
        )
    if mode == "learn":
        return (
            {"display": "none"},
            {"display": "none"},
            {"maxWidth": "900px", "margin": "0 auto 2rem auto", "display": "block"},
            {"display": "none"}
        )
    elif mode == "quiz":
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"maxWidth": "900px", "margin": "0 auto 2rem auto", "display": "block"}
        )
    return no_update, no_update, no_update, no_update

###############################################################################
# 10) MAP DISPLAY
###############################################################################
@app.callback(
    Output("country-map", "figure"),
    Output("quiz-map", "figure"),
    Input("store-current-country", "data"),
    Input("store-mode", "data")
)
def update_map(current_country_from_store, mode):
    learn_fig = go.Figure()
    quiz_fig  = go.Figure()

    # Initial layout with explicit mapbox properties
    learn_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center=dict(lat=0, lon=0),
        mapbox_zoom=1,
        height=500,
        margin={"l":0,"r":0,"t":30,"b":0}
    )
    quiz_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center=dict(lat=0, lon=0),
        mapbox_zoom=1,
        height=500,
        margin={"l":0,"r":0,"t":30,"b":0}
    )

    # Set default titles
    learn_fig.update_layout(title_text="Learn Mode")
    quiz_fig.update_layout(title_text="Quiz Mode")

    if not current_country_from_store:
        return learn_fig, quiz_fig

    # Fix user-provided spelling (synonyms dictionary)
    synonyms = {
        "Andora": "Andorra",
        "San MArino": "San Marino",
        "Lichtenstein": "Liechtenstein",
        "Vaitikan": "Vatican City",
        "monaco": "Monaco",
        "kosovo": "Kosovo",
        "Monacco": "Monaco",
        "Kossovo": "Kosovo"
    }
    
    processed_country_name = current_country_from_store
    if processed_country_name in synonyms:
        processed_country_name = synonyms[processed_country_name]

    # Get English name for logic, and row for data
    eng_name = COUNTRY_MAP.get(processed_country_name, processed_country_name)
    
    row = df[df["country"] == processed_country_name]
    if row.empty:
        # If country (after synonym processing) is not in DataFrame, return empty maps
        return learn_fig, quiz_fig

    pts = row.iloc[0]["geometry_points"]
    cat = row.iloc[0]["category"]

    # Case 1: Selected country is a European Microstate - display all of them
    if eng_name in EUROPEAN_MICROSTATES_ENGLISH_CHECK:
        learn_fig.update_layout(title_text=f"European Microstates (Selected: {processed_country_name})")
        quiz_fig.update_layout(title_text="Quiz: European Microstates")

        for micro_df_key in EUROPEAN_MICROSTATES_DF_KEYS:
            micro_row = df[df["country"] == micro_df_key]
            if micro_row.empty:
                continue
            
            micro_pts_data = micro_row.iloc[0]["geometry_points"]
            if not micro_pts_data or len(micro_pts_data) == 0 or not isinstance(micro_pts_data[0], list) or len(micro_pts_data[0])!=2 :
                continue # Skip if no valid points

            micro_lats_calc = [p[0] for p in micro_pts_data]
            micro_lons_calc = [p[1] for p in micro_pts_data]

            if not micro_lats_calc or not micro_lons_calc:
                continue

            micro_centroid = dict(lat=sum(micro_lats_calc) / len(micro_lats_calc), 
                                  lon=sum(micro_lons_calc) / len(micro_lons_calc))
            
            marker_color_learn = "darkviolet" if micro_df_key == processed_country_name else "blue"
            marker_color_quiz = "orange" if micro_df_key == processed_country_name else "red"


            learn_fig.add_trace(go.Scattermapbox(
                lat=[micro_centroid["lat"]], lon=[micro_centroid["lon"]],
                mode="markers+text", marker=dict(size=12, color=marker_color_learn), name=micro_df_key,
                text=[micro_df_key], textposition="top right", textfont=dict(size=10)
            ))
            quiz_fig.add_trace(go.Scattermapbox(
                lat=[micro_centroid["lat"]], lon=[micro_centroid["lon"]],
                mode="markers", marker=dict(size=12, color=marker_color_quiz), name=micro_df_key
            ))
        
        # Center map on Europe to show all microstates
        map_center_europe = dict(lat=47, lon=12) # Adjusted for better coverage including Malta
        map_zoom_europe = 3.6
        learn_fig.update_layout(mapbox_center=map_center_europe, mapbox_zoom=map_zoom_europe)
        quiz_fig.update_layout(mapbox_center=map_center_europe, mapbox_zoom=map_zoom_europe)
        return learn_fig, quiz_fig

    # Case 2: Selected country is Russia or an Asian country (not a European microstate) - display as single dot
    if eng_name == "Russia" or (cat == "Asia" and eng_name not in EUROPEAN_MICROSTATES_ENGLISH_CHECK):
        if not pts or len(pts) <= 1 or not isinstance(pts[0], list) or len(pts[0])!=2: # Check for valid points for centroid calculation
            return learn_fig, quiz_fig # Not enough data for centroid

        lats_calc = [p[0] for p in pts]
        lons_calc = [p[1] for p in pts]
        if not lats_calc or not lons_calc:
             return learn_fig, quiz_fig

        centroid = dict(lat=sum(lats_calc)/len(lats_calc), lon=sum(lons_calc)/len(lons_calc))
        if eng_name == "Russia":
            centroid = dict(lat=55.7558, lon=37.6173) # Moscow

        learn_fig.add_trace(go.Scattermapbox(
            lat=[centroid["lat"]], lon=[centroid["lon"]],
            mode="markers", marker=dict(size=10, color="blue"), name=processed_country_name
        ))
        quiz_fig.add_trace(go.Scattermapbox(
            lat=[centroid["lat"]], lon=[centroid["lon"]],
            mode="markers", marker=dict(size=10, color="red"), name=processed_country_name
        ))
        learn_fig.update_layout(mapbox_center=centroid, mapbox_zoom=4, title_text=f"Learn: {processed_country_name}")
        quiz_fig.update_layout(mapbox_center=centroid, mapbox_zoom=4, title_text=f"Quiz: {processed_country_name}")
        return learn_fig, quiz_fig

    # Case 3: Default - display as polygon
    if not pts or len(pts) <= 1 or not isinstance(pts[0], list) or len(pts[0])!=2: # Check for valid polygon points
        return learn_fig, quiz_fig

    lats_poly = [p[0] for p in pts]
    lons_poly = [p[1] for p in pts]
    if pts[0] != pts[-1]: # Ensure polygon is closed
        lats_poly.append(pts[0][0])
        lons_poly.append(pts[0][1])

    # Update titles for polygon display
    learn_fig.update_layout(title_text=f"Learn: {processed_country_name}")
    quiz_fig.update_layout(title_text=f"Quiz: {processed_country_name}")
    
    color = "red" if processed_country_name == "Italien" else "blue"
    learn_fig.add_trace(go.Scattermapbox(
        lat=lats_poly, lon=lons_poly, mode="lines",
        fill="toself", fillcolor=color, line=dict(width=2, color=color),
        opacity=0.6, name=processed_country_name
    ))
    quiz_fig.add_trace(go.Scattermapbox(
        lat=lats_poly, lon=lons_poly, mode="lines",
        fill="toself", fillcolor="red", line=dict(width=2, color="red"),
        opacity=0.6, name=processed_country_name
    ))

    # Recenter + zoom for polygon
    lat0, lat1 = min(lats_poly), max(lats_poly)
    lon0, lon1 = min(lons_poly), max(lons_poly)
    center_poly = dict(lat=(lat0 + lat1) / 2, lon=(lon0 + lon1) / 2)
    span_poly = max(lat1 - lat0, lon1 - lon0, 0.1) # Avoid division by zero if span is tiny
    zoom_poly = max(2, min(12, 4 / span_poly if span_poly > 0 else 2))

    learn_fig.update_layout(mapbox_center=center_poly, mapbox_zoom=zoom_poly)
    quiz_fig.update_layout(mapbox_center=center_poly, mapbox_zoom=zoom_poly)
    
    return learn_fig, quiz_fig

###############################################################################
# RUN
###############################################################################
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
