import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Convert image to binary data
def convertToBinaryData(file_path):
    with open(file_path, 'rb') as file:
        blobData = file.read()
    return blobData

# Insert image and data into SQLite
def insertBLOB(data):
    try:
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()

        # Create a table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS mineral_diseases (
                    image BLOB NOT NULL,
                    name TEXT PRIMARY KEY,
                    deficiency TEXT, 
                    content FLOAT, 
                    type TEXT, 
                    solution TEXT
                )''')     

        # Insert data into the table
        sqlite_insert_blob_query = '''INSERT OR REPLACE INTO mineral_diseases 
                    (image, name, deficiency, content, type, solution)
                    VALUES (?, ?, ?, ?, ?, ?)'''
        for record in data:
            photo_path, name, deficiency, content, type, solution = record
            imgPhoto = convertToBinaryData(photo_path)
            data_tuple = (imgPhoto, name, deficiency, content, type, solution)
            cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

# Find matching image in the database
def find_matching_image_in_db(input_image):
    try:
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()

        # Retrieve all records from the 'mineral_diseases' table
        cursor.execute("SELECT image, name, deficiency, content, type, solution FROM mineral_diseases")
        records = cursor.fetchall()

        # Loop through each record and compare the binary image data
        for row in records:
            db_image, db_name, db_deficiency, db_content, db_type, db_solution = row
            if input_image == db_image:
                return {
                    "name": db_name,
                    "deficiency": db_deficiency,
                    "content": db_content,
                    "type": db_type,
                    "solution": db_solution
                }
        
        return None
    except sqlite3.Error as error:
        print("Failed to retrieve data from sqlite table", error)
        return None
    finally:
        if sqliteConnection:
            sqliteConnection.close()

@app.route('/', methods=['GET', 'POST'])
def main():
    result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            # Read the file content
            file_content = file.read()
            # Find matching image in the database
            result = find_matching_image_in_db(file_content)
    
    return render_template_string(''' 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mineral Detector in Plants</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-image: url("/greenfarm.jpg");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }
        .header {
            position: relative;
            width: 100%;
            height: 60px;
            background-color: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            box-sizing: border-box;
        }
        .heading {
            font-size: 18px;
            font-weight: bold;
            margin: 0;
        }
        .account-icon {
            width: 24px;
            height: 24px;
        }
        .content {
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section h2 {
            margin-bottom: 10px;
        }
        #google_translate_element {
            margin-left: auto;
        }
        .upload-form {
            margin-bottom: 20px;
        }
    </style>
    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement(
                {
                    pageLanguage: 'en', 
                    includedLanguages: 'en,es,fr,ta,hi,zh-CN', 
                    layout: google.translate.TranslateElement.InlineLayout.SIMPLE
                }, 
                'google_translate_element'
            );
        }
    </script>
    <script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
</head>
<body>
    <header class="header">
        <h1>
            <p style="font-family: 'times new roman', 'Times New Roman', times New Roman, monospace;">
                MINERAL DETECTOR IN PLANTS
            </p>
        </h1>
        <!-- Google Translate Dropdown -->
        <div id="google_translate_element"></div>

        <svg class="account-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
        </svg>
    </header>
    
    <main class="content">
        <!-- Show the upload form only if no result has been found yet -->
        {% if not result %}
        <form class="upload-form" method="POST" enctype="multipart/form-data">
            <label for="file">Upload plant image:</label>
            <input type="file" name="file" id="file" required>
            <button type="submit">Submit</button>
        </form>
        {% endif %}
        
        <!-- Display result if found -->
        {% if result %}
        <div class="section">
            <h2>DISEASE NAME</h2>
            <p>{{ result.name }}</p>
        </div>
        <div class="section">
            <h2>DEFICIENCY</h2>
            <p>{{ result.deficiency }}</p>
        </div>
        <div class="section">
            <h2>CONTENT</h2>
            <p>{{ result.content }}</p>
        </div>
        <div class="section">
            <h2>TYPE OF NUTRIENT</h2>
            <p>{{ result.type }}</p>
        </div>
        <div class="section">
            <h2>SOLUTION</h2>
            <p>{{ result.solution }}</p>
        </div>
        {% endif %}
    </main>
</body>
</html>
    ''', result=result)

if __name__ == '__main__':
    data = [
        ('C:\\Users\\Messilena Shalom\\Downloads\\Grape Rot.jpg', 'Grape Black Rot', 'Magnesium', 0.35, 'Macronutrient', 'Epsom Salt, Dolomitic Lime, Kieserite,  Magnesium Oxide'), 
        ('C:\\Users\\Messilena Shalom\\Downloads\\Grape.jpg', 'Grape Leaf Blight', 'Magnesium', 0.1, 'Macronutrient', 'Epsom Salt, Dolomitic Lime, Kieserite,  Magnesium Oxide'),
        ('C:\\Users\\Messilena Shalom\\Pictures\\Potato .JPG', 'Potato Late Blight', 'Potassium', 2, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'), 
        ('C:\\Users\\Messilena Shalom\\Pictures\\Squash Powdery mildew.JPG', 'Squash Powdery Mildew', 'Potassium', 2, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Pictures\\Strawberry Scorch.JPG', 'Strawberry Leaf Scorch', 'Potassium', 1.5, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Downloads\\Tomato Bact Spot.jpg', 'Tomato Bacterial Spot', 'Potassium', 3, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Pictures\\Tomato Blight.JPG', 'Tomato Early Blight', 'Potassium', 3, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Pictures\\Tomato Mold.JPG', 'Tomato Leaf Mold', 'Potassium', 2, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Pictures\\Tomato Septoria.JPG', 'Tomato Septoria Leaf Spot', 'Potassium', 3, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Downloads\\Tomato Spider.JPG', 'Tomato Spider Mites Two Spotted', 'Magnesium, Potassium',  0.35, 'Macronutrient', 'Epsom Salt, Dolomitic Lime, Kieserite,  Magnesium Oxide, Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate'),
        ('C:\\Users\\Messilena Shalom\\Downloads\\Tomato Target.jpg', 'Tomato Target Spot', 'Potassium', 3, 'Macronutrient', 'Langbeinite, Wood Ash, Banana Peel Fertilizer,  Potassium Sulfate')
    ]
    insertBLOB(data)
    input_image_path = get_image_path_from_user()
    if input_image_path:
        find_matching_image_in_db(input_image_path)
if __name__ == '__main__':
    app.run()    
    