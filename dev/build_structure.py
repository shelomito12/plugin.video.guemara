import os
import json

# Category descriptions (Sedarim)
CATEGORY_DESCRIPTIONS = {
    "Seder Zeraim": "Este primer Séder trata los asuntos relativos a leyes agrícolas - En general relevantes sólo para la vida en Israel.",
    "Seder Moed": "Este segundo Séder discute las leyes del Shabat y de las fiestas.",
    "Seder Nashim": "Este tercer Séder trata los asuntos relativos al matrimonio y del derecho de familia.",
    "Seder Nezikin": "Este cuarto Séder cubre el derecho civil y penal y el sistema judicial.",
    "Seder Kodashim": "Este quinto Séder se centra en el Templo y en el servicio Divino en torno a él.",
    "Seder Taharot": "Este sexto y último Séder discute las leyes de pureza ritual."
}

# Book (masejta) descriptions
BOOK_DESCRIPTIONS = {
    "Berajot": "Este Masejet se ocupa de las leyes y de la filosofía de la oración y de las bendiciones.",
    "Shabat": "Este Masejet trata sobre las leyes del sábado, entre las que destacan las 39 prohibiciones relacionadas con el día sagrado.",
    "Eruvin": "Este Masejet trata sobre las leyes complicadas relativas a cargar algo en el exterior de la casa de uno en Shabat, y sobre el límite del Eruv.",
    "Pesajim": "Este Masejet trata sobre las leyes de la Pascua (tanto hoy como en la época del Templo).",
    "Yoma": "Este Masejet trata sobre Yom Ha-Kipurim (El Día del Perdón), sus leyes y la ceremonia de los Sacerdotes durante este día.",
    "Suca": "Este Masejet trata sobre las leyes de la fiesta de los Tabernáculos (Sucot) y sobre las medidas de la Sucá.",
    "Beitza": "Este Masejet trata principalmente sobre las reglas que deben observarse en Yom Tov.",
    "Rosh Hashana": "Este Masejet trata sobre las leyes que conciernen al Año Nuevo judío (Rosh Hashaná).",
    "Taanit": "Este Masejet se ocupa de los días especiales de ayuno en épocas de sequía u otras ocurrencias adversas en el calendario judío.",
    "Shekalim": "Este Masejet trata sobre las leyes de la recolección del Majatzit HaShekel, así como de los gastos del Templo.", # From Moed
    "Meguila": "Este Masejet se ocupa de las leyes de las distintas mitzvot que rodean a la festividad de Purim.",
    "Moed Katan": "Este Masejet se ocupa de las leyes de los días intermedios (Jol HaMoed) tanto de Sucot como de Pésaj.",
    "Jaguiga": "Este Masejet trata sobre las leyes relativas a la presentación de una ofrenda de animales en cada una de las fiestas de peregrinación.",
    "Yevamot": "Este Masejet trata las leyes (muy complicadas) en relación con un matrimonio levirato.",
    "Ketubot": "Este tratado habla acerca de las leyes de los contratos de matrimonio; las obligaciones y las responsabilidades financieras.",
    "Nedarim": "Este Masejet trata las leyes de los votos y sus consecuencias legales.",
    "Nazir": "Este Masejet trata las leyes del Nazareo. Un Nazareo es un judío que se abstiene de tomar vino, de estar en contacto con los muertos, y de cortarse el pelo.",
    "Sota": "Este Masejet trata las leyes de la sospecha contra una adúltera.",
    "Guitin": "Este Masejet trata las leyes y documentos de divorcio.", # Corrected typo from Guitin
    "Kidushin": "Este Masejet trata las leyes con respecto a la etapa inicial del matrimonio, el compromiso matrimonial, y las leyes del matrimonio.",
    "Baba Kama": "Este Masejet trata las leyes en materia del Derecho civil (de daños) y derecho penal por daños no criminales.",
    "Baba Metzia": "Este Masejet trata las leyes en materia de asuntos civiles, en gran parte de delitos y leyes de propiedad.",
    "Baba Batra": "Este Masejet trata las leyes en materia de asuntos civiles, en gran parte propiedad de la tierra.",
    "Sanhedrin": "Este Masejet trata las reglas de los procedimientos judiciales en el Sanhedrin, la pena de muerte y otros asuntos en materia penal.",
    "Avoda Zara": "Este Masejet trata con las leyes de las interacciones entre judíos y gentiles y / o idólatras.",
    "Horayot": "Este Masejet trata sobre lo que le pasa a un tribunal superior, alto sacerdote o rey que emite un fallo legal por error o que peca.",
    "Shevuot": "Este Masejet trata las reglas que se ocupan de los distintos tipos de juramentos y sus consecuencias.", # From Nezikin
    "Makot": "Este Masejet trata las reglas en materia de castigos no capitales (es decir, azotes).",
    "Zebajim": "Este Masejet trata sobre las leyes relativas a la presentación de ofrendas de animales en el Templo.", # Corrected typo from Zebajim
    "Menajot": "Este Masejet se ocupa de las reglas relativas a la preparación y presentación de las ofrendas de cereales y bebidas.",
    "Julin": "Este Masejet se ocupa de las leyes para el sacrificio de animales y aves para carne de uso ordinario, en lugar de sagrado.", # Corrected typo from Julin
    "Bejorot": "Este Masejet trata sobre las leyes del hijo varón primogénito (ambos, animales y humanos).", # Corrected typo from Bejorot
    "Arajin": "Este Masejet trata sobre el valor de una promesa al Templo 'por mi vida / por la vida de mi hijo', etc.", # Corrected typo from Arajin
    "Temura": "Este Masejet trata sobre la transferencia (ilegal) de la santidad del sacrificio de un animal potencial a otro.",
    "Keritot": "Este Masejet trata sobre la presentación de las ofrendas por el pecado u otras ofrendas por los pecados más graves.",
    "Meila": "Este Masejet trata sobre el uso irrespetuoso de la propiedad del Templo, y de los objetos que conforman el mismo.", # Corrected typo from Meila
    "Nida": "Este Masejet trata sobre las leyes que rodean el ciclo menstrual de una mujer.", # From Taharot
}

# Map folder names to clean Seder keys (maintains Seder order)
SEDER_FOLDER_MAP = {
    "Seder_Zeraim": "Zeraim",
    "Seder_Moed": "Moed",
    "Seder_Nashim": "Nashim",
    "Seder_Nezikin": "Nezikin",
    "Seder_Kodashim": "Kodashim",
    "Seder_Taharot": "Taharot"
}

# --- Define the canonical order of Masechtot within each Seder ---
# Use the *clean* names (spaces, not underscores) as these are used for lookups later
MASECHTOT_ORDER = {
    "Zeraim": ["Berajot"],
    "Moed": [
        "Shabat", "Eruvin", "Pesajim", "Yoma", "Suca", "Beitza", "Rosh Hashana",
        "Taanit", "Shekalim", "Meguila", "Moed Katan", "Jaguiga"
    ],
    "Nashim": ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sota", "Guitin", "Kidushin"],
    "Nezikin": [
        "Baba Kama", "Baba Metzia", "Baba Batra", "Sanhedrin", "Avoda Zara",
        "Horayot", "Shevuot", "Makot"
    ],
    "Kodashim": [
        "Zebajim", "Menajot", "Julin", "Bejorot", "Arajin", "Temura",
        "Keritot", "Meila"
    ],
    "Taharot": ["Nida"]
}

# --- Read Seder Thumb URLs from external file ---
THUMB_URL_FILE = "sedarim_thumb_urls.txt"
seder_thumb_urls = []
try:
    # Ensure the file exists in the same directory as the script
    if os.path.isfile(THUMB_URL_FILE):
        with open(THUMB_URL_FILE, 'r', encoding='utf-8') as tf:
            # Read non-empty lines and strip whitespace
            seder_thumb_urls = [line.strip() for line in tf if line.strip()]
        if len(seder_thumb_urls) < len(SEDER_FOLDER_MAP):
            print(f"⚠️ Warning: '{THUMB_URL_FILE}' contains fewer URLs ({len(seder_thumb_urls)}) than expected Sedarim ({len(SEDER_FOLDER_MAP)}). Some thumbs may be missing.")
        elif len(seder_thumb_urls) > len(SEDER_FOLDER_MAP):
             print(f"⚠️ Warning: '{THUMB_URL_FILE}' contains more URLs ({len(seder_thumb_urls)}) than expected Sedarim ({len(SEDER_FOLDER_MAP)}). Extra URLs will be ignored.")
        print(f"✅ Successfully read {len(seder_thumb_urls)} thumb URLs from '{THUMB_URL_FILE}'.")
    else:
        print(f"⚠️ Warning: Thumb URL file '{THUMB_URL_FILE}' not found in script directory. No Seder thumbs will be added.")
except Exception as e:
    print(f"❌ Error reading thumb URL file '{THUMB_URL_FILE}': {e}")
    # Continue without thumbs if file reading fails
    seder_thumb_urls = []


# --- Build structure in correct order ---
output_structure = {}

# Iterate through Sedarim in the specified order, getting index too
for index, (folder, seder_key) in enumerate(SEDER_FOLDER_MAP.items()):
    if not os.path.isdir(folder):
        print(f"ℹ️ Skipping Seder folder (not found): {folder}")
        continue

    seder_label = f"Seder {seder_key}"
    seder_description = CATEGORY_DESCRIPTIONS.get(seder_label, "")
    print(f"Processing Seder: {seder_key} (from folder {folder})")

    # --- Get the corresponding thumb URL using the index ---
    current_seder_thumb_url = None
    if index < len(seder_thumb_urls): # Check index is within the bounds of URLs read
        current_seder_thumb_url = seder_thumb_urls[index]
    else:
        # This warning is now handled during file reading, but keep check just in case
        print(f"  ⚠️ No thumb URL found or assigned for Seder {seder_key} at index {index}.")

    # Initialize the structure for this Seder, adding the thumb key
    output_structure[seder_key] = {
        "description": seder_description,
        "thumb": current_seder_thumb_url, # Assign the URL (or None if not found)
        "books": {}
    }

    # Iterate through Masechtot in the canonical order for this Seder
    ordered_masechtot = MASECHTOT_ORDER.get(seder_key, [])
    if not ordered_masechtot:
         print(f"⚠️ No canonical order defined for Seder: {seder_key}")
         continue

    for masejta_name in ordered_masechtot:
        # Reconstruct the expected filename from the clean Masechet name
        filename = masejta_name.replace(" ", "_") + ".txt"
        file_path = os.path.join(folder, filename)

        if not os.path.isfile(file_path):
            # print(f"  ℹ️ Skipping Masechet '{masejta_name}' (file not found: {filename})") # Reduced verbosity
            continue

        # print(f"  Processing Masechet: {masejta_name} (from file {filename})") # Reduced verbosity
        try:
            with open(file_path, encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                # print(f"  ⚠️ File is empty: {filename}") # Reduced verbosity
                continue

            lessons = {}
            for i, url in enumerate(lines, start=2):
                lesson_title = f"{masejta_name} {i}"
                lessons[lesson_title] = url # Store as simple URL for now

                # If you wanted lessons to have thumbs/more data from JSON later:
                # lessons[lesson_title] = {"video": url, "thumb": None} # Example

            book_description = BOOK_DESCRIPTIONS.get(masejta_name, "")
            # if not book_description:
            #      print(f"  ⚠️ No description found for Masechet: {masejta_name}") # Reduced verbosity

            # Add the book data - NOTE: Currently NOT adding thumbs at book level
            output_structure[seder_key]["books"][masejta_name] = {
                "description": book_description,
                # "thumb": "path/to/book/thumb.png", # Add logic here later if needed
                "lessons": lessons
            }
        except Exception as e:
            print(f"  ❌ Error processing file {filename}: {e}")


# --- Save the final structure as JSON ---
try:
    # Ensure the 'resources' directory exists where the script is run OR in addon path
    # For consistency with Kodi addon structure, let's save relative to script path for now
    os.makedirs("resources", exist_ok=True)
    output_path = os.path.join("resources", "guemara_structure.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_structure, f, indent=2, ensure_ascii=False)
    print(f"✅ '{output_path}' generated successfully.")

except Exception as e:
    print(f"❌ Error writing JSON file '{output_path}': {e}")