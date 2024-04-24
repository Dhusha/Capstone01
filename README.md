**Title: YouTube Data Harvesting and Warehousing using SQL and Streamlit**

The "YouTube Data Harvesting and Warehousing using SQL and Streamlit" project aims to facilitate the collection of data from YouTube channels via the YouTube Data API v3, storing it in a MySQL database, and offering querying capabilities through a Streamlit web interface.

**Technologies Utilized:**

1. **Python:** The primary language for scripting and data processing.
2. **Google APIs Client Library for Python:** Used to interact with the YouTube Data API v3 for fetching essential information like channel details, playlist details, video details, and comments.
3. **Streamlit:** Employs Streamlit to create a user-friendly UI, enabling users to interact with the application, conduct data retrieval, and perform analysis operations.
4. **MySQL:** Leveraged for data storage, creating a database for channels, playlists, comments, and videos, and establishing connections with Python.

**Streamlit:**
Streamlit is utilized to create a web page interface, providing users with intuitive interaction and seamless data retrieval and analysis capabilities.

**Python:**
Python, renowned for its ease of learning and understanding, serves as the primary programming language for developing the application. It handles tasks such as data retrieval, processing, analysis, and visualization.

**Google API Client:**
The googleapiclient library facilitates communication with various Google APIs. In this project, it enables interaction with YouTube's Data API v3, offering access to crucial information via code.

**MySQL:**
MySQL, a robust relational database management system, is extensively used to create and manage databases for channels, playlists, comments, and videos. It efficiently stores data for querying and analysis purposes.

**Required Libraries:**

1. `googleapiclient.discovery`
2. `streamlit`
3. `mysql`
4. `pandas`
5. `regex`

**Features:**
The application offers the following functionalities:

1. Retrieval of channel, playlist, comment, and video data from YouTube using the YouTube API.
2. Migration and storage of data in a SQL database for efficient querying and analysis.
3. Search and retrieval of data from the SQL database using various search options.

By leveraging these technologies and features, the project streamlines the process of harvesting, warehousing, and querying YouTube data, empowering users with valuable insights and analysis capabilities.
