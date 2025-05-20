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
def update_map(current_country, mode):
    learn_fig = go.Figure()
    quiz_fig  = go.Figure()

    # initial layout with explicit mapbox properties
    learn_fig.update_layout(
        title="Learn Mode",
        mapbox_style="open-street-map",
        mapbox_center=dict(lat=0, lon=0),
        mapbox_zoom=1,
        height=500,
        margin={"l":0,"r":0,"t":30,"b":0}
    )
    quiz_fig.update_layout(
        title="Quiz Mode",
        mapbox_style="open-street-map",
        mapbox_center=dict(lat=0, lon=0),
        mapbox_zoom=1,
        height=500,
        margin={"l":0,"r":0,"t":30,"b":0}
    )

    if not current_country:
        return learn_fig, quiz_fig

    # get country polygon
    row = df[df["country"] == current_country]
    if row.empty:
        return learn_fig, quiz_fig

    pts = row.iloc[0]["geometry_points"]
    if len(pts) <= 1:
        return learn_fig, quiz_fig

    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    # close polygon
    if pts[0] != pts[-1]:
        lats.append(pts[0][0])
        lons.append(pts[0][1])

    # learn mode trace
    color = "red" if current_country == "Italien" else "blue"
    learn_fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        fill="toself", fillcolor=color, line=dict(width=2, color=color),
        opacity=0.6, name=current_country
    ))

    # quiz mode trace
    quiz_fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        fill="toself", fillcolor="red",   line=dict(width=2, color="red"),
        opacity=0.6, name=current_country
    ))

    # recenter + zoom around country
    lat0, lat1 = min(lats), max(lats)
    lon0, lon1 = min(lons), max(lons)
    center = dict(lat=(lat0+lat1)/2, lon=(lon0+lon1)/2)
    span = max(lat1-lat0, lon1-lon0)
    # raise upper zoom limit from 6 to 12 for micro‐states
    zoom = max(2, min(12, 4/span if span>0 else 2))

    learn_fig.update_layout(
        mapbox_center=center,
        mapbox_zoom=zoom
    )
    quiz_fig.update_layout(
        mapbox_center=center,
        mapbox_zoom=zoom
    )

    return learn_fig, quiz_fig

###############################################################################
# RUN
###############################################################################
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
