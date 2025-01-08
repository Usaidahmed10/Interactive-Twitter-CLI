from pymongo import MongoClient
from datetime import datetime
import os
import time

DATABASE_NAME = "TweetsDB"


def clear_screen():
    if os.name == 'nt':  # Check if the system is Windows (NT stands for New Technology, used in Windows)
        os.system('cls')  # Clears the screen in Windows
    else:
        os.system('clear')  # Clears the screen in Unix-like systems

def connect_to_db(port):
    """
    Connect to the MongoDB instance and return the database.
    """
    try:
        client = MongoClient(f"mongodb://localhost:{port}/")
        print(f"Connected to MongoDB on port {port}")
        db = client["TweetsDB"]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    
def search_tweets(db):
    """
    Function:
    - User provides keywords (space-separated) to search tweets.
    - Displays a list of tweets containing any of the keywords.
    - For each tweet, lists the tweet ID, username, date, and content (truncated if long).
    - Allows the user to select a tweet to view its full content and detailed metadata.
    """
    while True:
        # Get user input for keywords and split them into a list
        keywords = input("Enter keywords (space-separated) (or 0 to go back to main menu): ").split()
        if keywords[0] == "0":
            return
        if not keywords:
            print("Error: Please enter at least one keyword.")
            continue
        
        # Construct query to search tweets containing any of the keywords (case-insensitive)
        query = {
            "$and": [
                {"content": {"$regex": rf'(?<!\w)#{keyword}\b|\b{keyword}\b', "$options": "i"}}
                for keyword in keywords
            ]
        }

        # Execute the query
        collection = db["tweets"]
        results = list(collection.find(query, {}))

        # Handle no results
        if not results:
            print("Error: No tweets found for the given keywords.")
        else:
            break
        
    # print results
    idx = 1
    for tweet in results:
        # will default to 'N/A' if field is absent
        print(f"{idx}. ID: {tweet.get('id', 'N/A')}, Date: {tweet.get('date', 'N/A')}, Content: {repr(tweet.get('content', 'N/A'))}, Username: {tweet.get('user', {}).get('username', 'N/A')}")
        idx += 1

    
    # Allow user to select a tweet for detailed view

    while True:
        try:
            user_choice = int(input("\nSelect a tweet for detailed information (enter tweet number or 0 to go back to main menu): ")) - 1
            if user_choice == -1:
                break
            if 0 <= user_choice < len(results):
                selected_tweet = results[user_choice]
                for key, value in selected_tweet.items():
                    print(f"{key}: {value}")
                break
            else:
                print("Error: Invalid choice. Please select a valid number.")
        except ValueError:
            print("Error: Please enter a valid number.")

def search_users(db):
    '''
    Function:
    User provides keyword and sees all users whose display name / location contains this keyword.
    For each user, list the username, displayname, and location (no duplicates).
    Can select a user and see full information about the user.
    '''
    while True:

        keyword = input("Enter the search term (or 0 to go back to main menu):")
        if keyword == "0":
            return
        collection = db['tweets']

        # aggregation pipeline: search for users with the keyword in displayname or location
        pipeline = [
            {
                # filter documents where user.displayname or user.location has keyword.
                # "$options" : "i" allows for case insensitive pattern matching.
                "$match": { 
                    "$or": [
                        {"user.displayname": {"$regex": f"\\b{keyword}\\b", "$options": "i"}},
                        {"user.location": {"$regex": f"\\b{keyword}\\b", "$options": "i"}}
                    ]
                }
            },
            {
                # group result by user.username
                "$group": {
                    "_id": "$user.username",
                    # specifies what value to include for the displayname field in the grouped output.
                    # selects the first value of the user.displayname field it encounters in each group.
                    "displayname": {"$first": "$user.displayname"},
                    # similar thing here
                    "location": {"$first": "$user.location"}
                }
            }
        ]

        # execute above aggregation pipeline
        results = list(collection.aggregate(pipeline))
        if not results:
            print("Error: No users found for that search term")
        else:
            break

    # print results
    idx = 1
    for user in results:
        # will default to 'N/A' if field is absent
        print(f"{idx}. Username: {user['_id']}, Display Name: {user.get('displayname', 'N/A')}, Location: {user.get('location', 'N/A')}")
        idx += 1

    # user can try to select another user for detailed info
    while True:
        try:
            user_choice = int(input("Select a user for detailed information (enter user number or 0 to go back to main menu): ")) - 1
            if user_choice == -1:
                break
            if 0 <= user_choice < len(results):
                selected_user_username = results[user_choice]['_id']

                user_details = collection.find_one({"user.username": selected_user_username}, {"_id": 0, "user": 1})
                if user_details and ("user" in user_details):
                    print(f"Full user details for username {selected_user_username}: ")
                    for key, value in user_details['user'].items():
                        print(f"{key} : {value}")
                    break
                else:
                    print(f"No details found for username {selected_user_username}")
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")



def list_top_tweets(db):
    """
    List the top n tweets based on a field (retweetCount, likeCount, quoteCount),
    and only show full details after the user selects a tweet.
    """
    # Prompt user for sorting field and number of tweets
    field = input("Enter the field to sort by (retweetCount/likeCount/quoteCount) (or 0 to go back to main menu): ").strip()
    if field[0] == "0":
        return
    n = int(input("Enter the number of top tweets to list: ").strip())

    # Ensure the field is valid
    valid_fields = ["retweetCount", "likeCount", "quoteCount"]
    if field not in valid_fields:
        print(f"Invalid field. Please choose one of {valid_fields}.")
        return

    # Query to get the top `n` tweets, with required fields (you can include more fields here)
    results = db["tweets"].find({}, {"_id": 1, "date": 1, "content": 1, "user.username": 1, field: 1}).sort(field, -1).limit(n)

    # Convert the cursor to a list
    results_list = list(results)

    # Check if results exist
    if not results_list:
        print("No tweets found.")
        return

    # Display the top tweets with basic information (ID, date, content, username, and the chosen field)
    print(f"\nTop Tweets sorted by {field}:")
    for index, result in enumerate(results_list, start=1):
        tweet_id = result.get("_id", "N/A")
        date = result.get("date", "N/A")
        content = result.get("content", "N/A")
        username = result.get("user", {}).get("username", "N/A")
        score = result.get(field, "N/A")  # Include the chosen category's value
        print(f"{index}. ID: {tweet_id} | Date: {date} | Content: {repr(content)} | Username: {username} | {field}: {score}")

    # Allow user to select a tweet for more details
    choice = input("\nWould you like to see more details about any tweet? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            tweet_index = int(input(f"Enter the number (1-{n}) to view full tweet details: "))
            if 1 <= tweet_index <= n:
                selected_tweet = results_list[tweet_index - 1]  # Retrieve selected tweet
                
                # Fetch the full document using the _id of the selected tweet to get all fields
                full_tweet = db["tweets"].find_one({"_id": selected_tweet["_id"]})
                
                if full_tweet:
                    print("\nFull Tweet Details:")
                    for key, value in full_tweet.items():
                        if key == "content":
                            print(f"{key}: {repr(value)}")
                        else:   
                            print(f"{key}: {value}")
                else:
                    print("Tweet details not found.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")



def list_top_users(db):
    '''
    Function:
    Lists the top n users based on followersCount.
    Displays username, displayname, and followersCount for each user.
    Allows the user to select a user and view full information.
    '''
    try:
        while True:
            n = input("Enter the number of top users to list (or 0 to go back to main menu): ")
            if n == "0":
                return
            if not n.isdigit() or int(n) <= 0:
                print("Error: Please enter a positive number.")
            else:
                n = int(n)
                break
        
        pipeline = [
            {
                # grouping by username, and also getting maximum followersCount
                "$group": {
                    "_id": "$user.username",
                    "displayname": {"$first": "$user.displayname"},
                    "followersCount": {"$max": "$user.followersCount"}
                }
            },

            {"$sort": {"followersCount": -1}},
            # only show top n
            {"$limit": n}
        ]

        results = list(db["tweets"].aggregate(pipeline))

        if not results:
            print("Error: No users found.")
            return

        # displaying:
        print("\nTop Users:")
        idx = 1
        for user in results:
            print(f"{idx}. Username: {user['_id']}, Display Name: {user.get('displayname', 'N/A')}, Followers: {user.get('followersCount', 0)}")
            idx += 1

        # user can select user for full details
        while True:
            try:
                user_choice = int(input("\nSelect a user for detailed information (enter user number or 0 to go back to main menu): ")) - 1
                if user_choice ==  -1:
                    return
                if 0 <= user_choice < len(results):
                    selected_user_username = results[user_choice]['_id']
                    
                    # fetches full user details
                    user_details_cursor = db["tweets"].find({"user.username": selected_user_username}, {"_id": 0, "user": 1}).sort("user.followersCount", -1).limit(1)
                    user_details = next(user_details_cursor, None)
                    
                    # prints full user details
                    if user_details and "user" in user_details:
                        print(f"\nFull details for username '{selected_user_username}':\n")
                        for key, value in user_details["user"].items():
                            if key == "rawDescription":
                                print(f"{key}: {repr(value)}")
                            else:
                                print(f"{key}: {value}")
                    else:
                        print(f"No details found for username '{selected_user_username}'.")
                    break
                else:
                    print("Error: Invalid choice. Please select a valid number.")
            except ValueError:
                print("Error: Please enter a valid number.")
    except ValueError:
        print("Error: Please enter a valid number.")


def compose_tweet(db):
    content = input("Enter your tweet (or 0 to go back to main menu): ")
    if content == "0":
        return
    tweet = {
    "url": None,
    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    "content": content,
    "renderedContent": None,
    "id": None,
    "user": {
        "username": "291user",
        "displayname": None,
        "id": None,
        "description": None,
        "rawDescription": None,
        "descriptionUrls": None,
        "verified": None,
        "created": None,
        "followersCount": None,
        "friendsCount": None,
        "statusesCount": None,
        "favouritesCount": None,
        "listedCount": None,
        "mediaCount": None,
        "location": None,
        "protected": None,
        "linkUrl": None,
        "linkTcourl": None,
        "profileImageUrl": None,
        "profileBannerUrl": None,
        "url": None
    },
    "outlinks": None,
    "tcooutlinks": None,
    "replyCount": None,
    "retweetCount": None,
    "likeCount": None,
    "quoteCount": None,
    "conversationId": None,
    "lang": None,
    "source": None,
    "sourceUrl": None,
    "sourceLabel": None,
    "media": None,
    "retweetedTweet": None,
    "quotedTweet": None,
    "mentionedUsers": None
}
    
    db["tweets"].insert_one(tweet)
    print("Tweet composed successfully!")




def main():
    # Connect to MongoDB
    port = input("Enter MongoDB port: ")
    if not port.isdigit() or int(port) < 0:
        print("Port must be a positive integer")
        return
    db = connect_to_db(port)
    if db is None:
        exit()
    time.sleep(1)
    clear_screen()
    
    while True:
        print("Main Menu:")
        print("1. Search for tweets")
        print("2. Search for users")
        print("3. List top tweets")
        print("4. List top users")
        print("5. Compose a tweet")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            clear_screen()
            search_tweets(db)
        elif choice == "2":
            clear_screen()
            search_users(db)
        elif choice == "3":
            clear_screen()
            list_top_tweets(db)
        elif choice == "4":
            clear_screen()
            list_top_users(db)
        elif choice == "5":
            clear_screen()
            compose_tweet(db)
        elif choice == "6":
            print("Exiting...")
            time.sleep(2)
            break
        else:
            clear_screen()
            print("Invalid choice. Please try again.")
    clear_screen()


if __name__ == "__main__":
    main()