# Interactive Twitter CLI

A command-line interface (CLI) application that allows users to interact with Twitter-like data stored in a MongoDB database. The application supports searching tweets and users, listing top tweets and users, and composing new tweets, all from the terminal. The integrated database is efficiently handled using MongoDB.

## Features

- **Search Tweets:** Search for tweets containing specific keywords. View tweet IDs, usernames, dates, and truncated content, and select a tweet for full details and metadata.
- **Search Users:** Search for users based on keywords in their display name or location. View usernames, display names, and locations, and select a user for detailed information.
- **List Top Tweets:** List top tweets sorted by retweet count, like count, or quote count. View detailed information about any selected tweet.
- **List Top Users:** List top users based on follower count. View detailed user information by selecting a user.
- **Compose Tweet:** Add a new tweet to the database with a username and content.

## Requirements

- Python 3.8+
- MongoDB (running locally)
- Python libraries:
  - `pymongo`
  - `datetime`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Usaidahmed10/MongoDB-Tweet-Manager.git
   cd MongoDB-Tweet-Manager
   ```

2. Install the required Python libraries:
   ```bash
   pip install pymongo
   ```

3. Ensure MongoDB is running locally on your machine.

4. Initialize the MongoDB environment by running:
   ```bash
   python3 load-json.py <db.json> <port_num>
   ```
   This will create the MongoDB environment, create a `tweets` collection, and load tweets into it from the `db.json` file in batches of 10,000. You should see a success message similar to:
   ```
   Starting MongoDB server on port 27017 with dbpath: C:\Users\<your-name>\MongoDB-Tweet-Manager\mongodb-data-76cacf61
   MongoDB server started successfully.
   Connected to MongoDB on port 27017
   Existing 'tweets' collection dropped.
   New 'tweets' collection created.
   Inserted the final batch of 100 tweets.
   All tweets have been inserted successfully!
   ```

   **Note:** `load-json.py` looks for the `MongoDB-Tweet-Manager` folder to find the MongoDB data directory and initialize the environment. If this repository is cloned and renamed, update the `directory_name` parameter in the `find_assignment_directory` function of `load-json.py` to match the new folder name or rename your folder to `MongoDB-Tweet-Manager`.

## Usage

1. Run the main program:
   ```bash
   python3 tweet-manager.py
   ```

2. Enter the MongoDB port when prompted. Use the same port specified when running `load-json.py`.

3. Use the main menu to navigate through the features:
   - Search tweets by keywords
   - Search users by keywords
   - List top tweets
   - List top users
   - Compose a new tweet

   Ensure you have Python 3+ installed, as the code is not designed to work with earlier versions of Python. This program is designed for Unix-like environments and may not work on Windows without alterations to the `load-json.py` logic.

## File Structure

- `tweet-manager.py`: Main script containing all functionalities of the application.
- `load-json.py`: Script to initialize MongoDB and load data.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request for any improvements or fixes.

## Contributors

- AhmedZ04

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

