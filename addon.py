import os
import sys
import json
import urllib.parse
import traceback # Import traceback for better error logging

import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

# --- Constants ---
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0] # The plugin:// URL base
try:
    ADDON_ID = xbmc.getAddonInfo('id')
    ADDON_PROFILE = xbmcvfs.translatePath(f'special://profile/addon_data/{ADDON_ID}/')
    ADDON_PATH = xbmcvfs.translatePath(f'special://home/addons/{ADDON_ID}/')
except Exception as e:
    xbmc.log(f"[Guemara] Error getting Addon ID/Paths: {e}. Using fallback.", xbmc.LOGWARNING)
    ADDON_ID = 'plugin.video.guemara' # Fallback ID
    ADDON_PATH = xbmcvfs.translatePath(f'special://home/addons/{ADDON_ID}')

STRUCTURE_FILE = os.path.join(ADDON_PATH, 'resources', 'guemara_structure.json')

xbmc.log("=== [Guemara] default.py execution started ===", xbmc.LOGINFO)
xbmc.log(f"[Guemara] Addon Handle: {ADDON_HANDLE}", xbmc.LOGINFO)
xbmc.log(f"[Guemara] Base URL: {BASE_URL}", xbmc.LOGINFO)
xbmc.log(f"[Guemara] Addon Path: {ADDON_PATH}", xbmc.LOGINFO)
xbmc.log(f"[Guemara] Structure File Path: {STRUCTURE_FILE}", xbmc.LOGINFO)


# --- Load Structure File ---
try:
    xbmc.log(f"[Guemara] Attempting to load structure file: {STRUCTURE_FILE}", xbmc.LOGINFO)

    # *** REVISED: Remove explicit exists() checks ***
    # Rely directly on xbmcvfs.File() to handle file access.
    # This should work if the previous script could access the file.
    f = xbmcvfs.File(STRUCTURE_FILE, 'r')
    content = f.read()
    f.close()

    if not content:
         # Raise an error if the file was empty
         raise ValueError("Structure file is empty")

    GUEMARA_STRUCTURE = json.loads(content)
    xbmc.log("[Guemara] Loaded and parsed guemara_structure.json successfully", xbmc.LOGINFO)

except Exception as e:
    # Log the specific error type and message
    error_details = traceback.format_exc()
    xbmc.log(f"[Guemara] Failed to load or parse structure file '{STRUCTURE_FILE}': {e}\n{error_details}", xbmc.LOGERROR)
    # Show a more generic error to the user, log details for debugging
    xbmcgui.Dialog().notification("Guemara", "Error loading content file", xbmcgui.NOTIFICATION_ERROR, 5000)
    xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
    sys.exit()


# --- Helper Functions ---
def build_url(query_dict):
    """Encodes a dictionary into a URL query string for the plugin."""
    return f"{BASE_URL}?{urllib.parse.urlencode(query_dict)}"

def create_listitem(title, plot="", is_folder=False, is_playable=False, icon=None, thumb=None):
    """General helper function to create a ListItem."""
    # TODO - natively https://forum.kodi.tv/showthread.php?tid=369255&pid=3107800#pid3107800
    # or using this convenient module: https://github.com/jurialmunkey/script.module.infotagger
    # DEBUG prints: "Setting most video properties through ListItem.setInfo() is deprecated and
    # might be removed in future Kodi versions. Please use the respective setter in InfoTagVideo"
    li = xbmcgui.ListItem(label=title)
    info = {'title': title, 'plot': plot}
    if is_playable:
        info['mediatype'] = 'video'
        li.setProperty('IsPlayable', 'true')
    else:
         # Keep mediatype video for folders too if desired, some skins use it
         info['mediatype'] = 'video'

    li.setInfo('video', info)

    # --- Icon Logic Modification ---
    icon_to_use = icon  # Use the passed icon if available
    if not icon_to_use: # Fallback to defaults only if no icon was passed
        if is_playable:
            icon_to_use = 'DefaultMovies.png' # Default for playable if no specific icon
        else:
            icon_to_use = 'DefaultFolder.png' # Default for folder if no specific icon

    art = {'icon': icon_to_use}
    if thumb:
        art['thumb'] = thumb
    # Optional: If you want the thumb to default to the icon when no specific thumb is available:
    elif not thumb and icon_to_use != 'DefaultFolder.png' and icon_to_use != 'DefaultMovies.png':
        art['thumb'] = icon_to_use
    li.setArt(art)

    return li

# --- Listing Functions ---
def list_sedarim():
    """Lists the main categories (Sedarim) and the Search option."""
    xbmc.log("[Guemara] list_sedarim() called", xbmc.LOGINFO)
    items = []

    # 1. Add Search Item (remains unchanged)
    search_url = build_url({'action': 'search'})
    search_li = create_listitem("Buscar...", plot="Buscar tratados por título", is_folder=True, icon='DefaultAddonsSearch.png')
    items.append((search_url, search_li, True))
    xbmc.log("[Guemara] Added Search item", xbmc.LOGDEBUG)

    # 2. Add Sedarim Items
    if not GUEMARA_STRUCTURE:
        xbmc.log("[Guemara] GUEMARA_STRUCTURE is empty or not loaded.", xbmc.LOGWARNING)
    else:
        # Iterate using JSON order
        for seder_key in GUEMARA_STRUCTURE.keys():
            seder_data = GUEMARA_STRUCTURE.get(seder_key, {})

            display_name = f"Seder {seder_key}"
            seder_description = seder_data.get("description", "") # Get description from Seder data
            # Get the specific thumbnail URL from the Seder's data in the JSON
            seder_thumb_url = seder_data.get("thumb") # Returns None if "thumb" key doesn't exist
            seder_url = build_url({'action': 'list_books', 'seder': seder_key})

            seder_li = create_listitem(
                title=display_name,
                plot=seder_description,
                is_folder=True,
                icon='DefaultVideoPlaylists.png', # Keep using default playlist icon for the list view
                thumb=seder_thumb_url            # Pass the thumb URL read from JSON
            )
            items.append((seder_url, seder_li, True))
            # Log the thumb URL being used for debugging
            xbmc.log(f"[Guemara] Added Seder: {display_name} with thumb: {seder_thumb_url}", xbmc.LOGDEBUG)

    if not items:
        xbmc.log("[Guemara] No items generated in list_sedarim (excluding search)", xbmc.LOGWARNING)
        if len(items) <= 1: # Only search item exists
             xbmcgui.Dialog().notification("Guemara", "No content categories found.", xbmcgui.NOTIFICATION_INFO, 3000)

    xbmcplugin.addDirectoryItems(handle=ADDON_HANDLE, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    xbmc.log("[Guemara] list_sedarim() finished", xbmc.LOGINFO)


def list_books(seder):
    """Lists books under a specific Seder."""
    xbmc.log(f"[Guemara] Listing books for Seder '{seder}'", xbmc.LOGINFO)
    seder_data = GUEMARA_STRUCTURE.get(seder, {})
    books = seder_data.get("books", {})
    items = []

    # Iterate using JSON order
    for book_name in books.keys():
        book_data = books.get(book_name, {}) # Get book data to potentially read thumb from JSON later if needed
        book_description = book_data.get("description", "")
        # book_thumb_path = book_data.get("thumb") # TODO if reading from JSON
        book_url = build_url({'action': 'list_lessons', 'seder': seder, 'book': book_name})

        book_li = create_listitem(
            title=book_name,
            plot=book_description,
            is_folder=True,
            icon='DefaultVideoPlaylists.png',
            thumb='DefaultVideoPlaylists.png'
        )
        items.append((book_url, book_li, True))
        xbmc.log(f"[Guemara] Added book: {book_name}", xbmc.LOGDEBUG)

    if not items:
        xbmc.log(f"[Guemara] No books found for Seder '{seder}'", xbmc.LOGWARNING)
        xbmcgui.Dialog().notification("Guemara", f"No se encontraron libros en {seder}", xbmcgui.NOTIFICATION_INFO, 3000)

    xbmcplugin.addDirectoryItems(handle=ADDON_HANDLE, items=items, totalItems=len(items))
    xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    xbmc.log(f"[Guemara] list_books() finished for Seder '{seder}'", xbmc.LOGINFO)

def list_lessons(seder, book):
    """Lists playable lessons for a specific Seder and Book."""
    xbmc.log(f"[Guemara] Listing lessons for Book '{book}' in Seder '{seder}'", xbmc.LOGINFO)
    lessons = GUEMARA_STRUCTURE.get(seder, {}).get("books", {}).get(book, {}).get("lessons", {})
    items = []

    # Iterate through lessons (order is preserved from JSON)
    for title, direct_url in lessons.items():
        # Create the ListItem - marked as playable here
        lesson_li = create_listitem(
            title,
            plot=f"Tratado de {book}, Seder {seder}",
            is_playable=True,
            icon='DefaultMovies.png',
            thumb='DefaultMovies.png'
        )

        # *** Create a plugin URL that calls the 'play' action ***
        # Pass the direct URL as an encoded parameter
        play_plugin_url = build_url({'action': 'play', 'video_url': direct_url, 'title': title})

        # Add the item with the plugin URL, not the direct URL
        items.append((play_plugin_url, lesson_li, False)) # False indicates it's not a folder
        xbmc.log(f"[Guemara] Added lesson item: {title} with plugin URL", xbmc.LOGDEBUG)

    if not items:
        xbmc.log(f"[Guemara] No lessons found for Book '{book}', Seder '{seder}'", xbmc.LOGWARNING)
        xbmcgui.Dialog().notification("Guemara", f"No se encontraron videos en {book}", xbmcgui.NOTIFICATION_INFO, 3000)

    xbmcplugin.addDirectoryItems(handle=ADDON_HANDLE, items=items, totalItems=len(items))
    # Set content type
    xbmcplugin.setContent(ADDON_HANDLE, 'episodes') # Or 'videos'
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    xbmc.log(f"[Guemara] list_lessons() finished for Book '{book}', Seder '{seder}'", xbmc.LOGINFO)


# --- Action Functions ---
def search_dialog():
    """Displays search input and lists results."""
    xbmc.log("[Guemara] search_dialog() called", xbmc.LOGINFO)
    query = xbmcgui.Dialog().input("Buscar tratado", type=xbmcgui.INPUT_ALPHANUM)
    if not query:
        xbmc.log("[Guemara] Search cancelled by user.", xbmc.LOGINFO)
        # Need to end directory even if cancelled, otherwise UI hangs
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)
        return

    xbmc.log(f"[Guemara] Searching for: '{query}'", xbmc.LOGINFO)
    results = []
    query_lower = query.lower()

    for seder, seder_data in GUEMARA_STRUCTURE.items():
        for book, book_data in seder_data.get("books", {}).items():
            for title, direct_url in book_data.get("lessons", {}).items():
                if query_lower in title.lower():
                    # Found a match
                    result_li = create_listitem(
                        title,
                        plot=f"Resultado de búsqueda: {book}, Seder {seder}",
                        is_playable=True,
                        icon='DefaultAddonVideo.png',
                        thumb='DefaultAddonVideo.png'
                        # Add 'thumb' if available
                    )
                    # *** Create a plugin URL pointing to 'play' action ***
                    play_plugin_url = build_url({'action': 'play', 'video_url': direct_url, 'title': title})
                    results.append((play_plugin_url, result_li, False))
                    xbmc.log(f"[Guemara] Found search result: {title}", xbmc.LOGDEBUG)

    if not results:
        xbmc.log("[Guemara] No search results found.", xbmc.LOGINFO)
        xbmcgui.Dialog().notification("Buscar", "No se encontraron resultados", xbmcgui.NOTIFICATION_INFO, 3000)
        # Still need to end directory even if no results
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)
        return

    xbmcplugin.addDirectoryItems(handle=ADDON_HANDLE, items=results, totalItems=len(results))
    xbmcplugin.setContent(ADDON_HANDLE, 'videos')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    xbmc.log("[Guemara] search_dialog() finished displaying results.", xbmc.LOGINFO)


def play_video(url, title=""):
    """Resolves the final URL for playback using setResolvedUrl."""
    xbmc.log(f"[Guemara] play_video() called for URL: {url}", xbmc.LOGINFO)
    if not url:
        xbmc.log("[Guemara] play_video() called with empty URL!", xbmc.LOGERROR)
        xbmcgui.Dialog().notification("Guemara", "Error: No video URL provided", xbmcgui.NOTIFICATION_ERROR, 3000)
        xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=False, listitem=xbmcgui.ListItem())
        return

    # Create a simple ListItem needed for setResolvedUrl
    # Pass the direct playable URL via 'path'
    list_item = xbmcgui.ListItem(path=url)

    # Optional: Set info labels again if needed, title is useful
    list_item.setInfo('video', {'title': title})

    # Optional: Set properties like MIME type if known
    if url.lower().endswith(".mp4"):
         list_item.setMimeType("video/mp4")

    xbmc.log(f"[Guemara] Calling setResolvedUrl with path: {url}", xbmc.LOGDEBUG)
    # Send the resolved URL to Kodi
    xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=True, listitem=list_item)
    xbmc.log("[Guemara] setResolvedUrl called successfully.", xbmc.LOGINFO)


# --- Main Router ---
def run():
    """Main entry point and router."""
    # Parse query string provided by Kodi
    raw_params = sys.argv[2][1:] # Get query string without '?'
    params = urllib.parse.parse_qs(raw_params)
    xbmc.log(f"[Guemara] Router received params: {params}", xbmc.LOGDEBUG)

    # Get action, default to None for root view
    action = params.get('action', [None])[0]

    try: # Add a top-level try-except for the router actions
        if action is None:
            list_sedarim()
        elif action == 'list_books':
            seder = params.get('seder', [None])[0]
            if seder:
                list_books(seder)
            else:
                xbmc.log("[Guemara] Router Error: 'list_books' action missing 'seder' param", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("Guemara", "Error: Seder no especificado", xbmcgui.NOTIFICATION_ERROR, 3000)
                xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        elif action == 'list_lessons':
            seder = params.get('seder', [None])[0]
            book = params.get('book', [None])[0]
            if seder and book:
                list_lessons(seder, book)
            else:
                xbmc.log("[Guemara] Router Error: 'list_lessons' action missing 'seder' or 'book' param", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("Guemara", "Error: Seder o libro no especificado", xbmcgui.NOTIFICATION_ERROR, 3000)
                xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        elif action == 'search':
            search_dialog()
        elif action == 'play':
            video_url_encoded = params.get('video_url', [None])[0]
            video_title = params.get('title', ["Video"])[0] # Get title if passed, fallback
            if video_url_encoded:
                video_url_decoded = urllib.parse.unquote(video_url_encoded)
                play_video(video_url_decoded, video_title)
                # Note: play_video calls setResolvedUrl, so we don't call endOfDirectory here
            else:
                xbmc.log("[Guemara] Router Error: 'play' action missing 'video_url' param", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("Guemara", "Error: URL de video no encontrado", xbmcgui.NOTIFICATION_ERROR, 3000)
                xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=False, listitem=xbmcgui.ListItem())
        else:
            xbmc.log(f"[Guemara] Unknown action: '{action}'. Showing root list.", xbmc.LOGWARNING)
            list_sedarim()

    except Exception as e:
        # Catch any unexpected errors during action execution
        error_details = traceback.format_exc()
        xbmc.log(f"[Guemara] Unexpected error during action '{action}': {e}\n{error_details}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification("Guemara", "An unexpected error occurred", xbmcgui.NOTIFICATION_ERROR, 5000)
        # Ensure directory listing ends even on unexpected error, unless it was during play
        if action != 'play':
             xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        else:
             # If error during play action before setResolvedUrl, signal failure
             xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=False, listitem=xbmcgui.ListItem())


# --- Execute ---
if __name__ == '__main__':
    run()