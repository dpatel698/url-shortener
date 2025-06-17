from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId # Used to handle MongoDB's unique
import hashlib
import urllib.parse
from pymongo.server_api import ServerApi

# Initialize the Flask application
app = Flask(__name__)
host_name = "127.0.0.1:5000"

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

@app.route('/shorturl/<string:shorturl_key>', methods=['GET'])
def get_url(shorturl_key):
    """
    Handles GET requests to /shorturl/<item_id>.
    Returns an original url location found by its MongoDB key.
    Returns 404 if the key is not found.
    """
    item = shortener_collection.find_one({"key": shorturl_key})

    if item:
        return jsonify({"location": item['url']}), 302
    else:
        return jsonify({"message": "URL not found"}), 404


def generate_unique_url_key(
    original_url: str,
    key_length: int = 10,
    existing_keys_db: dict = None
) -> str:
    """
    Generates a unique, short hash key for a given URL,
    with a collision resolution mechanism.

    Args:
        original_url (str): The URL for which to generate a unique key.
        key_length (int): The desired length of the generated key.
                          Shorter keys have a higher practical collision probability.
        existing_keys_db (dict): A dictionary simulating a database
                                 mapping existing keys to their original URLs.
                                 e.g., {"shortkey": "https://long.url"}

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
        query = {candidate_key: {'$exists': True}}
        find_key = shortener_collection.find_one({"key": candidate_key})
        if not find_key:
            # Case a: Key is unique
            return candidate_key
        elif find_key["key"] == original_url:
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
def add_item():
    """
    Handles POST requests to /shorturl.
    Adds a new item to the MongoDB collection.
    Expects JSON data in the request body with 'url'
    Returns the newly created item and 201 Created status.
    """
    new_data = request.get_json()

    if not new_data or 'url' not in new_data:
        return jsonify({"message": "Missing 'url' in request body"}), 400

    # Generate a key for the url using a hash function
    key = generate_unique_url_key(new_data['url'])
    new_data["key"] = key
    new_data["short_url"] = "http://shorturl/" + key


    # Insert the new document into the collection. MongoDB will automatically add an '_id'.
    result = shortener_collection.insert_one(new_data)

    # Fetch the newly created item by its _id to return it in the response
    # This also ensures that the returned item includes the generated _id
    created_item = shortener_collection.find_one({"_id": result.inserted_id})
    if created_item:
        created_item['_id'] = str(created_item['_id']) # Convert ObjectId to string
        return jsonify(created_item), 201
    else:
        return jsonify({"wrong_key": new_data['url']}), 500

@app.route('/shorturl/<string:shorturl_key>', methods=['DELETE'])
def delete_item(shorturl_key):
    """
    Handles DELETE requests to /shorturl/<string:shorturl_key>>.
    Deletes an item by its MongoDB _id.
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