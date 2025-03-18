import dash
from dash import dcc, html, Input, Output, State
import base64
import os
import pytesseract
from PIL import Image
from googletrans import Translator
from gtts import gTTS
import io
import time  # Import time to generate unique filenames

# Set the Tesseract-OCR path (Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Ensure assets folder exists
if not os.path.exists("assets"):
    os.makedirs("assets")

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("OCR with Translation and Speech Output", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Div(
        children=[
            dcc.Upload(
                id="upload",
                children=html.Div([
                    html.Button("Upload Image", id="upload_btn", style={
                        'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                        'padding': '10px 20px', 'cursor': 'pointer', 'borderRadius': '5px'
                    })
                ]),
                multiple=False
            ),
            html.Br(),
            html.Span(id="upload_status", children="No file uploaded", style={'color': 'red'}),
            html.Br(),
            dcc.Dropdown(
                id="language",
                options=[
                    {"label": "English", "value": "en"},
                    {"label": "Hindi", "value": "hi"},
                    {"label": "Bengali", "value": "bn"},
                    {"label": "French", "value": "fr"}
                ],
                placeholder="Select target language",
                style={'width': '50%', 'margin': '10px auto'}
            ),
            html.Br(),
            html.Button("Process", id="process_btn", style={
                'backgroundColor': '#2ecc71', 'color': 'white', 'border': 'none',
                'padding': '10px 20px', 'cursor': 'pointer', 'borderRadius': '5px'
            }),
            html.Br(),
            html.Div(id="ocr_output", style={
                'marginTop': '20px', 'padding': '10px', 'border': '1px solid #ddd',
                'borderRadius': '5px', 'backgroundColor': '#ecf0f1'
            }),
            html.Audio(id="audio_output", controls=True, autoPlay=False, style={'marginTop': '10px'})
        ],
        style={'textAlign': 'center', 'padding': '20px', 'maxWidth': '600px', 'margin': 'auto', 'backgroundColor': '#f7f9fc', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px #bdc3c7'}
    )
])

@app.callback(
    Output("upload_status", "children"),
    [Input("upload", "contents")]
)
def update_upload_status(contents):
    if contents:
        return "File uploaded successfully"
    return "No file uploaded"

@app.callback(
    [Output("ocr_output", "children"), Output("audio_output", "src")],
    [Input("process_btn", "n_clicks")],
    [State("upload", "contents"), State("language", "value")]
)
def process_ocr(n_clicks, contents, lang):
    if not n_clicks or not contents or not lang:
        return "", ""
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    img = Image.open(io.BytesIO(decoded))
    extracted_text = pytesseract.image_to_string(img)
    
    translator = Translator()
    translated_text = translator.translate(extracted_text, dest=lang).text
    
    # Generate a unique filename using timestamp
    timestamp = str(int(time.time()))
    audio_path = f"assets/output_{timestamp}.mp3"
    
    tts = gTTS(text=translated_text, lang=lang)
    tts.save(audio_path)
    
    # Return the new file path to force update
    return translated_text, f"/assets/output_{timestamp}.mp3"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
