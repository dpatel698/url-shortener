from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from pymongo import MongoClient
import hashlib
import urllib.parse
from pymongo.server_api import ServerApi

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
BASE_SHORT_URL = "http://localhost:5000"


# --- MongoDB Connection ---
# Replace 'mongodb://localhost:27017/' with your MongoDB connection string
# If MongoDB is running on your local machine with default port, this should work.
# For a remote MongoDB Atlas cluster, you would use its connection string.
try:
    username = urllib.parse.quote_plus('dpatel0698')
    password = urllib.parse.quote_plus('SVdn@0698')
    uri = "mongodb+srv://%s:%s@cluster0.wqobmc3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" % (username, password)
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.Projects # Connect to a database named Projects
    shortener_collection = db.shortener # Connect to a collection named 'shortener'
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


# --- API Endpoints ---
@app.route('/<string:shorturl_key>', methods=['GET'])
def get_original_url_and_redirect(shorturl_key):
    """
    Handles GET requests for the short URL.
    Redirects the user to the original long URL.
    Returns 404 if the key is not found.
    """
    # Look up the document by the short key
    item = shortener_collection.find_one({"key": shorturl_key})

    if item and 'url' in item:
        # Perform a 302 Found (temporary) redirect to the original URL
        return redirect(item['url'], code=302)
    else:
        return jsonify({"message": "Short URL not found"}), 404


def generate_unique_url_key(
    original_url: str,
    key_length: int = 8,
) -> str:
    """
    Generates a unique, short hash key for a given URL,
    with a collision resolution mechanism.

    Args:
        original_url (str): The URL for which to generate a unique key.
        key_length (int): The desired length of the generated key.
                          Shorter keys have a higher practical collision probability.

    Returns:
        str: A unique, short key for the URL.
    """
    # Retry id collisions are found
    max_retries = 100
    for retry_count in range(max_retries):
        salted_url = f"{original_url}-{retry_count}" if retry_count > 0 else original_url

        # Hash the (salted) URL using SHA-256
        # encode() converts the string to bytes, which hashlib requires
        full_hash = hashlib.sha256(salted_url.encode('utf-8')).hexdigest()

        candidate_key = full_hash[:key_length]

        # 4. Check for collision in the "database"
        # Collision scenarios:
        # a) candidate_key is NOT in existing_keys_db: It's unique! Use it.
        # b) candidate_key IS in existing_keys_db AND maps to the original_url:
        #    This means the URL was already shortened, return the existing key.
        # c) candidate_key IS in existing_keys_db BUT maps to a DIFFERENT url:
        #    This is a true hash collision for our chosen key_length. Retry.
        existing_doc = shortener_collection.find_one({"key": candidate_key})

        if not existing_doc:
            # Case a: Key is unique (no document found with this key)
            return candidate_key
        elif existing_doc.get("url") == original_url:
            # Case b: URL was already shortened with this key
            print(f"DEBUG: Found existing key '{candidate_key}' for '{original_url}'. Returning existing.")
            return candidate_key
        else:
            # Case c: Collision detected (key exists for a DIFFERENT URL)
            print(f"DEBUG: Collision detected for key '{candidate_key}'. Retrying with salted URL.")
            # The loop will increment retry_count and try again with a new salt

    # If max_retries is reached, it implies an extremely high number of collisions
    # or an issue, so raise an error.
    raise Exception(f"Could not generate a unique key for '{original_url}' after {max_retries} retries.")


@app.route('/shorturl', methods=['POST'])
def create_short_url():
    """
    Handles POST requests to /shorturl.
    Creates a new short URL for a given long URL.
    Expects JSON data in the request body with 'url'.
    Returns the newly created short URL details and 201 Created status.
    """
    request_data = request.get_json()

    # Validate input
    if not request_data or 'url' not in request_data:
        return jsonify({"message": "Missing 'url' in request body"}), 400

    original_url = request_data['url']

    try:
        # Generate a unique key for the URL
        key = generate_unique_url_key(original_url)

        # Construct the full short URL
        short_url = f"{BASE_SHORT_URL}/{key}"

        # Prepare the document to insert into MongoDB
        new_document = {
            "url": original_url,
            "key": key,
            "short_url": short_url,
        }

        # Insert the new document into the collection
        result = shortener_collection.insert_one(new_document)

        # Fetch the newly created item by its _id to ensure all fields are returned
        created_item = shortener_collection.find_one({"_id": result.inserted_id})
        if created_item:
            # Convert ObjectId to string for JSON serialization
            created_item['_id'] = str(created_item['_id'])
            # Remove the MongoDB _id from the response if you don't want it exposed
            # created_item.pop('_id', None)
            return jsonify(created_item), 201
        else:
            # This case should be rare if insert_one was successful
            return jsonify({"message": "Failed to retrieve created short URL"}), 500

    except Exception as e:
        # Catch any exceptions during key generation or DB insertion
        return jsonify({"message": f"An error occurred: {e}"}), 500

@app.route('/<string:shorturl_key>', methods=['DELETE'])
def delete_short_url(shorturl_key):
    """
    Handles DELETE requests to /<string:shorturl_key>>.
    Deletes an item by its MongoDB key.
    Returns a success message.
    Returns 404 if the item is not found.
    """
    delete_result = shortener_collection.delete_one({"key": shorturl_key})

    if delete_result.deleted_count == 1:
        return jsonify({"message": f"Key: {shorturl_key}  deleted successfully"}), 200
    else:
        return jsonify({"message": "URL not found"}), 404

# --- Run the Flask Application ---
if __name__ == '__main__':
    app.run(debug=False)