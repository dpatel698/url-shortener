from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId # Used to handle MongoDB's unique
import hashlib
import time
import random

# Initialize the Flask application
app = Flask(__name__)

# --- MongoDB Connection ---
# Replace 'mongodb://localhost:27017/' with your MongoDB connection string
# If MongoDB is running on your local machine with default port, this should work.
# For a remote MongoDB Atlas cluster, you would use its connection string.
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mydatabase # Connect to a database named 'mydatabase'
    shortener_collection = db.shortener # Connect to a collection named 'items'
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


# --- API Endpoints ---

@app.route('/items', methods=['GET'])
def get_all_items():
    """
    Handles GET requests to /items.
    Returns a list of all items from the MongoDB collection.
    """
    all_items = []
    # Iterate through all documents in the 'items' collection
    for item in shortener_collection.find():
        # MongoDB's default '_id' field is an ObjectId, which is not JSON serializable.
        # Convert it to a string before returning.
        item['_id'] = str(item['_id'])
        all_items.append(item)
    return jsonify(all_items)

@app.route('/items/<string:item_id>', methods=['GET'])
def get_item(item_id):
    """
    Handles GET requests to /items/<item_id>.
    Returns a single item by its MongoDB _id.
    Returns 404 if the item is not found.
    """
    try:
        # Convert the string ID from the URL to a MongoDB ObjectId
        obj_id = ObjectId(item_id)
    except Exception:
        # If the ID is not a valid ObjectId format, return a bad request error
        return jsonify({"message": "Invalid item ID format"}), 400

    # Find a single document by its _id
    item = shortener_collection.find_one({"_id": obj_id})

    if item:
        item['_id'] = str(item['_id']) # Convert ObjectId to string for JSON serialization
        return jsonify(item)
    else:
        return jsonify({"message": "Item not found"}), 404


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
    new_data["short_url"] = "http://localhost/" + key


    # Insert the new document into the collection. MongoDB will automatically add an '_id'.
    result = shortener_collection.insert(new_data)

    # Fetch the newly created item by its _id to return it in the response
    # This also ensures that the returned item includes the generated _id
    created_item = shortener_collection.find_one({"_id": result.inserted_id})
    if created_item:
        created_item['_id'] = str(created_item['_id']) # Convert ObjectId to string
        return jsonify(created_item), 201
    else:
        # This case should ideally not happen if insertion was successful
        return jsonify({"message": "Failed to retrieve created item"}), 500


@app.route('/items/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Handles PUT requests to /items/<item_id>.
    Updates an existing item by its MongoDB _id.
    Expects JSON data in the request body with updated 'name' or 'description'.
    Returns the updated item.
    Returns 404 if the item is not found.
    """
    try:
        obj_id = ObjectId(item_id)
    except Exception:
        return jsonify({"message": "Invalid item ID format"}), 400

    updated_data = request.get_json()

    # Define the update operation. $set updates specific fields.
    update_result = shortener_collection.update_one(
        {"_id": obj_id},
        {"$set": updated_data}
    )

    if update_result.matched_count == 0:
        return jsonify({"message": "Item not found"}), 404
    elif update_result.modified_count == 0:
        # Item found but no changes were made (e.g., update data was identical)
        return jsonify({"message": "Item found but no changes applied"}), 200 # Or 204 No Content
    else:
        # Fetch the updated item to return it in the response
        updated_item = shortener_collection.find_one({"_id": obj_id})
        if updated_item:
            updated_item['_id'] = str(updated_item['_id'])
            return jsonify(updated_item)
        else:
            return jsonify({"message": "Failed to retrieve updated item"}), 500


@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Handles DELETE requests to /items/<item_id>.
    Deletes an item by its MongoDB _id.
    Returns a success message.
    Returns 404 if the item is not found.
    """
    try:
        obj_id = ObjectId(item_id)
    except Exception:
        return jsonify({"message": "Invalid item ID format"}), 400

    # Delete a single document by its _id
    delete_result = shortener_collection.delete_one({"_id": obj_id})

    if delete_result.deleted_count == 1:
        return jsonify({"message": f"Item with ID {item_id} deleted successfully"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404

# --- Run the Flask Application ---
if __name__ == '__main__':
    app.run(debug=True)