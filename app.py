

from nicegui import ui


import string, random
from starlette.responses import RedirectResponse
from supabase import create_client, Client

SUPABASE_URL = ""
SUPABASE_KEY = ""
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def shorten_url(long_url):
    short_code = generate_short_code()
    supabase.table("urls").insert({"short_code": short_code, "long_url": long_url}).\
        execute()
    return f"http://localhost:8080/{short_code}"

def get_long_url(short_code):
    data = supabase.table("urls").select("long_url").eq("short_code", short_code).\
        single().execute()
    if data.data:
        return data.data["long_url"]
    return None

# --- UI ---
with ui.column().style('align-items: center; justify-content: center; height: 100vh;'):
    ui.label("🌐 URL Shortener").style('font-size: 2.5em; font-weight: bold;\
                                        margin-bottom: 0.5em;')
    ui.label("Enter a long URL and get a short, shareable link!").\
        style('font-size: 1.2em; margin-bottom: 1em;')
    
    with ui.card().style('padding: 1.5em; width: 24em;'):
        url_input = ui.input(label="Long URL", placeholder="https://example.com")
        url_input.classes('w-full')
        result_label = ui.label().style('margin-top: 1em; word-break: break-all;')

        def handle_shorten():
            long_url = url_input.value.strip()
            if long_url:
                short_url = shorten_url(long_url)
                result_label.set_text(short_url)

        ui.button("Shorten", on_click=handle_shorten).style(
            'margin-top: 1em; width: 100%; background-color: #3B82F6; color: white;'
        )

# Redirect page
@ui.page("/{short_code}")
def redirect_page(short_code: str):
    long_url = get_long_url(short_code)
    if long_url:
        return RedirectResponse(long_url)
    else:
        ui.label("Error: This short link does not exist!")

ui.run()
