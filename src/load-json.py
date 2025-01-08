import sys
import json
import subprocess
import time
import os
from pymongo import MongoClient

DATABASE_NAME = 'TweetsDB'


def find_directory(start_path="~", dir_name="MongoDB-Tweet-Manager"):
    """
    Recursively search for a directory named `dir_name` starting from `start_path`.
    Returns the first match found or raises an exception if not found.
    """
    start_path = os.path.expanduser(start_path) # expands '~' to the actual home directory path of the user
    for root, dirs, files in os.walk(start_path):
        if dir_name in dirs:
            return os.path.join(root, dir_name)
    raise FileNotFoundError(f"Directory '{dir_name}' not found starting from {start_path}")


def start_mongodb(port, dbpath, logpath):
    try:
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)
            print(f"Created database path: {dbpath}")
        
        os.chmod(dbpath, 0o700)

        print(f"Starting MongoDB server on port {port} with dbpath: {dbpath}")
        process = subprocess.Popen(
            [
                "mongod",
                "--port", str(port),
                "--dbpath", dbpath,
                "--logpath", logpath,
                "--logappend"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(5)

        if not wait_for_mongodb(port, timeout=60):
            print("Timed out waiting for MongoDB.")
            process.terminate()
            sys.exit(1)
        
        print("MongoDB server started successfully.")
    
    except Exception as e:
        print(f"Error starting MongoDB: {e}")
        sys.exit(1)


def wait_for_mongodb(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client = MongoClient(f"mongodb://localhost:{port}/")
            client.admin.command('ping') 
            return True
        except Exception:
            time.sleep(1)
    return False


def load_json(file_name, port):
    try:
        client = MongoClient(f"mongodb://localhost:{port}/")
        print(f"Connected to MongoDB on port {port}")
        
        db = client[DATABASE_NAME]
        
        # Drop existing collection
        if "tweets" in db.list_collection_names():
            db.tweets.drop()
            print("Existing 'tweets' collection dropped.")
        
        collection = db["tweets"]
        print("New 'tweets' collection created.")

        batch_size = 10000
        batch = []
        
        with open(file_name, 'r') as file:
            for line in file:
                batch.append(json.loads(line.strip()))
                
                if len(batch) == batch_size:
                    collection.insert_many(batch)
                    print(f"Inserted a batch of {batch_size} tweets.")
                    batch = []
            
            if batch:
                collection.insert_many(batch)
                print(f"Inserted the final batch of {len(batch)} tweets.")

        print("All tweets have been inserted successfully!")
    
    except Exception as e:
        print(f"Error loading JSON data: {e}")

import uuid

def main():
    if len(sys.argv) != 3:
        print("Usage: python load-json.py <file_name> <port>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    port = int(sys.argv[2])
    
    try:
        target_dir = find_directory()
        unique_id = str(uuid.uuid4())[:8] 
        dbpath = os.path.join(target_dir, f"mongodb-data-{unique_id}")
        logpath = os.path.join(dbpath, "mongodb.log")
        
        start_mongodb(port, dbpath, logpath)
        load_json(file_name, port)
    
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)



if __name__ == "__main__":
    main()