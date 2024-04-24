from googleapiclient.discovery import build
import googleapiclient.discovery
import pandas as pd
from datetime import datetime
import streamlit as st
import mysql.connector
import re 

#API Key extracting
def api_connect():
    api = "AIzaSyCj11X2-1qaME6Plk7C2wS71vcetUX0H1c"
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name,api_version,developerKey=api)
    return youtube

#storing the function to another variable
youtube=api_connect() 

#to get channel informations:
def get_channel_data(channel_id):
    request = youtube.channels().list(
        part="Snippet,ContentDetails,Statistics,Status",
        id=channel_id
    )
    response = request.execute()
    channel_data = []

    if 'items' in response:
        for item in response['items']:
            data = {
                "channel_id": item['id'],
                "channel_name": item['snippet']['title'],
                "channel_description": item['snippet']['description'],
                "channel_playlistid": item['contentDetails']['relatedPlaylists']['uploads'],
                "channel_videocount": item['statistics']['videoCount'],
                "channel_subscriptioncount": item['statistics']['subscriberCount'],
                "channel_viewcount": item['statistics']['viewCount'],
                "channel_status": item['status']['privacyStatus']
            }
            channel_data.append(data)
    return channel_data


#to get video ids:
def get_video_ids(channel_id):
    video_ids = []
    try:
        response = youtube.channels().list(id=channel_id, part='contentDetails').execute()
        if 'items' in response:
            channel_playlistid = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            next_page_token = None
            while True:
                videos = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=channel_playlistid,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                for video in videos.get('items', []):
                    video_ids.append(video['snippet']['resourceId']['videoId'])
                next_page_token = videos.get('nextPageToken')
                if not next_page_token:
                    break
    except KeyError as e:
        print(f"KeyError: {e}. Response may not contain 'items' key.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return video_ids


#to get video informations:
def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        response=request.execute()
        for item in response['items']:
            data = {"channel_name":item['snippet']['channelTitle'],
                "channel_id":item['snippet']['channelId'],
                "Video_ID": item['id'],
                "video_name": item['snippet']['title'], 
                "video_description": item['snippet']['description'],
                "video_publishedAt": item['snippet']['publishedAt'], 
                "video_thumbnail": item['snippet']['thumbnails']['default']['url'],
                "video_duration": item['contentDetails']['duration'],
                "video_views": item['statistics'].get('viewCount'),
                "video_commentcount": item['statistics'].get('commentCount'),
                "video_likes": item['statistics'].get('likeCount'),
                "video_dislikes": item['statistics'].get('dislikeCount'),
                "video_favoritecount": item['statistics']['favoriteCount'],
                "video_Tags": item['snippet'].get('tags'),
                "video_caption": item['contentDetails']['caption']
            }
            video_data.append(data)
    return video_data

#to get comment informations:
def get_comment_info(video_ids):
    comment_data=[]
    comment_count=0
    try:   
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()
            for item in response['items']:      #item=variablename
                data={
                        "Comment_id": item['snippet']['topLevelComment']['id'],
                        "Video_Id": item['snippet']['topLevelComment']['snippet']['videoId'],
                        "Comment_text": item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        "Comment_Author": item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        "Comment_PublishedAt": item['snippet']['topLevelComment']['snippet']['publishedAt']
                    }
                comment_data.append(data)
                comment_count += 1
                if comment_count >= 150:
                    break
            if comment_count >= 150:
                break
    except:
        pass
    return comment_data

#to get playlist informations:
def get_playlist_details(channel_id):
    next_page_token = None
    all_data = []
    try:
        if channel_id:
            while True:
                response = youtube.playlists().list(
                    part='id,snippet,contentDetails',
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                for item in response.get('items', []):
                    data = {
                        "Playlist_Id": item['id'],
                        "Channel_Id": item['snippet']['channelId'],
                        "Playlist_Name": item['snippet']['title']
                    }
                    all_data.append(data)
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
        else:
            print("No channel ID provided.")
    except Exception as e:
        print(f"An error occurred while fetching playlist details: {e}")
    return all_data


# Streamlit:
def display_option_menu():
    st.sidebar.markdown("🎉 Welcome to YouTube Data Hub 🎉")
    st.sidebar.markdown("<span style='color:yellow;'>EXPLORE YOUR DATA JOURNEY!</span>", unsafe_allow_html=True)
    st.sidebar.subheader("Skills You'll Gain")
    st.sidebar.markdown("- Python Scripting\n- API Integration\n- Data Collection\n- SQL Connection & Management\n- Streamlit Page")

# Display the option menu
display_option_menu()

st.balloons()
st.title(":sparkles: YouTube Data Harvesting and Warehousing :sparkles:")
st.write(":blue[Welcome to this innovative platform for harvesting and warehousing YouTube data!]")

#to get the user input:
channel_ids = set()
def get_channel_id():
    return st.text_input("# :red[Enter the Channel ID]")
channel_id = get_channel_id()
st.button("🚀 Migrate to SQL")

channel_details=get_channel_data(channel_id)
Video_Ids=get_video_ids(channel_id)
video_details=get_video_info(Video_Ids)
comment_details=get_comment_info(Video_Ids)
playlist_details=get_playlist_details(channel_id)

# Converting data to DataFrames:
channel_df = pd.DataFrame(channel_details)
video_df = pd.DataFrame(video_details)
comment_df = pd.DataFrame(comment_details)
playlist_df = pd.DataFrame(playlist_details)

#To display the collected data
st.subheader('Channel Information')
st.dataframe(channel_df)

st.subheader('Video Information')
st.dataframe(video_df)

st.subheader('Comment Information')
st.dataframe(comment_df)

st.subheader('Playlist Information')
st.dataframe(playlist_df)
    
#MySQL Connection:
mydb = mysql.connector.connect(host="localhost",user="root",password="Dhusha98")
print(mydb)
mycursor = mydb.cursor(buffered=True)
#mycursor.execute('CREATE DATABASE projectyoutube01')
mycursor.execute('use projectyoutube01')

#Creating channel table in SQL:
def channel_table():
    try:
        
        query= '''create table if not exists channeldetails(channel_id VARCHAR(255),
                                                            channel_name VARCHAR(255),
                                                            channel_subscriptioncount VARCHAR(255),
                                                            channel_viewcount INT,
                                                            channel_videocount INT,
                                                            channel_description TEXT,
                                                            channel_status VARCHAR(255))'''
        mycursor.execute(query)
        mydb.commit()
    except:
        print ('Channel tables are created')
channel_table()

#Inserting channel details
if channel_id:
    channel_ids.add(channel_id)
    st.success(f"Channel ID '{channel_id}' added to migration list.")
    channel_details = get_channel_data(channel_id)

    sql = '''INSERT IGNORE INTO channeldetails(channel_id, channel_name, channel_subscriptioncount, channel_viewcount,channel_videocount, channel_description, channel_status) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    
    try:
        for channel_detail in channel_details:
            query = "SELECT * FROM channeldetails WHERE channel_id = %s"
            channel_id_tuple = (channel_detail["channel_id"],)
            mycursor.execute(query, channel_id_tuple)
            existing_channel = mycursor.fetchone()
            if not existing_channel:  
                val = (
                    channel_detail["channel_id"],
                    channel_detail["channel_name"],
                    channel_detail["channel_subscriptioncount"],
                    channel_detail["channel_viewcount"],
                    channel_detail["channel_videocount"],
                    channel_detail["channel_description"],
                    channel_detail["channel_status"]
                )
                mycursor.execute(sql, val)
                mydb.commit()
                print(f"Channel details for {channel_detail['channel_name']} inserted successfully!")
            else:
                print(f"Channel details for {channel_detail['channel_name']} already exist in the database. Skipping insertion.")
    except mysql.connector.Error as err:
        print("Error:", err)
else:
    st.warning("Please enter a valid Channel ID before migrating to SQL.")

#Creating playlist table in SQL:
def playlist_table():
    try:
        # Create table in SQL
        query = '''create table if not exists playlistdetails(Playlist_Id VARCHAR(255),
                                                                Channel_Id VARCHAR(255),
                                                                Playlist_Name VARCHAR(255))'''
        mycursor.execute(query)
        mydb.commit()
    except Exception as e:
        print('Creating playlist table failed:', e)
playlist_table()

#Inserting playlist details:
try:
    for playlist_detail in playlist_details:
        # Check if the playlist already exists in the table based on Playlist_Id
        query = "SELECT COUNT(*) FROM playlistdetails WHERE Playlist_Id = %s"
        mycursor.execute(query, (playlist_detail["Playlist_Id"],))
        result = mycursor.fetchone()
        if result[0] == 0:  # If the playlist does not exist, insert it
            sql = '''INSERT INTO playlistdetails (Playlist_Id, Channel_Id, Playlist_Name)
                    VALUES (%s, %s, %s)'''
            val = (
                playlist_detail["Playlist_Id"],
                playlist_detail["Channel_Id"],
                playlist_detail["Playlist_Name"]
            )
            mycursor.execute(sql, val)
            mydb.commit()
            print("Playlist inserted successfully!")
        else:
            print("Playlist already exists, skipping insertion.")

except Exception as e:
    print("Error inserting playlists:", e)


#Creating video table in SQL
def video_table():
    try:
        query = '''create table if not exists videodetails(channel_name VARCHAR(255),
                                                            Video_ID VARCHAR(255),
                                                            video_name VARCHAR(255),
                                                            video_description TEXT,
                                                            video_publishedAt DATETIME,
                                                            video_thumbnail VARCHAR(255),
                                                            video_duration INT,
                                                            video_views INT,
                                                            video_commentcount VARCHAR(100),
                                                            video_likes INT,
                                                            video_dislikes INT,
                                                            video_favoritecount INT,
                                                            video_Tags VARCHAR(500),
                                                            video_caption VARCHAR(255)
                                                            )'''
        mycursor.execute(query)
        mydb.commit()
    except:
        print("Creating video table")
video_table()

#Inserting video details:
def video_exists(video_id):
    try:
        query = "SELECT COUNT(*) FROM videodetails WHERE Video_ID = %s"
        mycursor.execute(query, (video_id,))
        result = mycursor.fetchone()
        return result[0] > 0
    except Exception as e:
        print("Error executing SQL query in video_exists:", e)
        return False  # Return False in case of an error

try:
    for video_detail in video_details:
        if not video_exists(video_detail['Video_ID']):
            sql = '''INSERT INTO videodetails (channel_name, Video_ID, video_name, video_description, video_publishedAt, video_thumbnail, video_duration, video_views,
                        video_commentcount, video_likes, video_dislikes, video_favoritecount, video_Tags, video_caption)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            duration = video_detail['video_duration']
            match = re.match(r'^PT(\d+H)?(\d+M)?(\d+S)?$', duration)
            if match:
                hours = int(match.group(1)[:-1]) if match.group(1) else 0
                minutes = int(match.group(2)[:-1]) if match.group(2) else 0
                seconds = int(match.group(3)[:-1]) if match.group(3) else 0
                duration_seconds = hours * 3600 + minutes * 60 + seconds
            else:
                duration_seconds = None

            video_publishedAt = datetime.strptime(video_detail['video_publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            video_tags = ', '.join(video_detail.get("video_Tags", [])) if video_detail.get("video_Tags") else None
            val = (
                video_detail["channel_name"],
                video_detail["Video_ID"],
                video_detail["video_name"],
                video_detail["video_description"],
                video_publishedAt,
                video_detail["video_thumbnail"],
                duration_seconds,
                video_detail["video_views"],
                video_detail["video_commentcount"],
                video_detail["video_likes"],
                video_detail["video_dislikes"],
                video_detail["video_favoritecount"],
                video_tags,
                video_detail["video_caption"]
            )
            mycursor.execute(sql, val)
    mydb.commit()
    print("All video details inserted successfully!")
except Exception as e:
    print("Error inserting records:", e)

#Creating comment table in SQL:
def comments_table():
    try:
        query = '''create table if not exists commentdetails(Comment_id VARCHAR(255),
                                                                Video_Id VARCHAR(255),
                                                                Comment_text TEXT,
                                                                Comment_Author VARCHAR(255),
                                                                Comment_PublishedAt DATETIME)'''
        mycursor.execute(query)
        mydb.commit()
    except:
        print("Creating channel table")
comments_table()

# Inserting comment details
def check_duplicate(comment_id):
    query = "SELECT COUNT(*) FROM commentdetails WHERE Comment_id = %s"
    mycursor.execute(query, (comment_id,))
    result = mycursor.fetchone()
    return result[0] > 0
for comment_detail in comment_details:
    if not check_duplicate(comment_detail['Comment_id']):
        Comment_PublishedAt = datetime.strptime(comment_detail['Comment_PublishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        val = (
            comment_detail['Comment_id'],
            comment_detail['Video_Id'],
            comment_detail['Comment_text'],
            comment_detail['Comment_Author'],
            Comment_PublishedAt
        )
        try:
            sql = '''INSERT INTO commentdetails (Comment_id, Video_Id, Comment_text, Comment_Author, Comment_PublishedAt) VALUES (%s, %s, %s, %s, %s)'''
            mycursor.execute(sql, val)
            mydb.commit()
        except mysql.connector.Error as err:
            print("Error:", err)
    else:
        print("Duplicate comment found and skipped:", comment_detail['Comment_id'])

# Function to fetch channel details from the database and convert to DataFrame
def fetch_channel_db():
    mycursor.execute("SELECT * FROM channeldetails")
    data = mycursor.fetchall()
    df1 = pd.DataFrame(data, columns=["channel_id", "channel_name", "channel_subscriptioncount", "channel_viewcount", "channel_videocount", "channel_description", "channel_status"])
    # Assuming channel_id is the primary key
    df1.drop_duplicates(subset=["channel_id"], inplace=True)
    return df1

# Function to fetch playlist details from the database and convert to DataFrame
def fetch_playlist_db():
    mycursor.execute("SELECT * FROM playlistdetails")
    data = mycursor.fetchall()
    df2 = pd.DataFrame(data, columns=["Playlist_Id", "Channel_Id", "Playlist_Name"])
    # Assuming Playlist_Id is the primary key
    df2.drop_duplicates(subset=["Playlist_Id"], inplace=True)
    return df2

# Function to fetch video details from the database and convert to DataFrame
def fetch_video_db():
    mycursor.execute("SELECT DISTINCT * FROM videodetails")  # Add DISTINCT keyword to select unique rows
    data = mycursor.fetchall()
    df3 = pd.DataFrame(data, columns=["channel_name", "Video_ID", "video_name", "video_description", "video_publishedAt", "video_thumbnail", "video_duration", "video_views",
                    "video_commentcount", "video_likes", "video_dislikes", "video_favoritecount", "video_Tags", "video_caption"])
    df3.drop_duplicates(subset=["Video_ID"], inplace=True)
    return df3

# Function to fetch comment details from the database and convert to DataFrame
def fetch_comments_db():
    mycursor.execute("SELECT * FROM commentdetails")
    data = mycursor.fetchall()
    df4 = pd.DataFrame(data, columns=["Comment_id", "Video_Id", "Comment_text", "Comment_Author", "Comment_PublishedAt"])
    # Assuming Comment_id is the primary key
    df4.drop_duplicates(subset=["Comment_id"], inplace=True)
    return df4

#Main Streamlit code
def main():
    show_table = st.radio("# :green[Select the table for View:-]", ("CHANNEL", "PLAYLIST", "VIDEOS", "COMMENTS"))

    if show_table == "CHANNEL":
        df1 = fetch_channel_db()
        st.dataframe(df1)

    elif show_table == "PLAYLIST":
        df2 = fetch_playlist_db()
        st.dataframe(df2)

    elif show_table == "VIDEOS":
        df3 = fetch_video_db()
        st.dataframe(df3)

    elif show_table == "COMMENTS":
        df4 = fetch_comments_db()
        st.dataframe(df4)

if __name__ == "__main__":
    main()

#Answers for the 10 questions:
ques = st.selectbox("# :blue[Select the questions that you would like to query:]",
                         ["1.What are the names of all videos and their corresponding channels?",
                          "2.Which channels have the most number of videos, and how many videos do they have?",
                          "3.What are the top 10 most viewed videos and their respective channels?",
                          "4.How many comments were made on each video, and what are their corresponding video names?",
                          "5.Which videos have the highest number of likes, and what are their corresponding channel names?",
                          "6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                          "7.What is the total number of views for each channel, and what are their corresponding channel names?",
                          "8.What are the names of all the channels that have published videos in the year 2022?",
                          "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                          "10.Which videos have the highest number of comments, and what are their corresponding channel names?"])

if ques == "1.What are the names of all videos and their corresponding channels?":
            query1 = '''SELECT channel_name AS Channel_Title, video_name AS Video_Title FROM videodetails'''
            mycursor.execute(query1)
            mydb.commit()
            q1 = mycursor.fetchall()
            df1 = pd.DataFrame(q1, columns=["Channel_Title", "Video_Title"])
            st.dataframe(df1, width=1000)

elif ques == "2.Which channels have the most number of videos, and how many videos do they have?":
            query2 = '''SELECT channel_name AS Channel_Title, MAX(channel_videocount) AS Max_Video_Count
                        FROM channeldetails 
                        GROUP BY channel_name
                        ORDER BY Max_Video_Count DESC'''
            mycursor.execute(query2)
            mydb.commit()
            q2 = mycursor.fetchall()
            df2 = pd.DataFrame(q2, columns=["Channel_Title", "Max_Video_Count"])
            st.dataframe(df2)

elif ques == "3.What are the top 10 most viewed videos and their respective channels?":
            query3 = '''SELECT Channel_Title, Video_Title, Views
                        FROM (
                            SELECT channel_name AS Channel_Title, video_name AS Video_Title, MAX(video_views) AS Views
                            FROM videodetails
                            WHERE video_views IS NOT NULL
                            GROUP BY channel_name, video_name
                            ORDER BY MAX(video_views) DESC
                            LIMIT 10
                        ) AS top_videos'''
            mycursor.execute(query3)
            mydb.commit()
            q3 = mycursor.fetchall()
            df3 = pd.DataFrame(q3, columns=["Channel_Title", "Video_Title", "Views"])
            st.dataframe(df3)

elif ques == "4.How many comments were made on each video, and what are their corresponding video names?":
            query4 = '''SELECT video_name AS Video_Title,video_commentcount AS No_Of_Comments
                        FROM videodetails
                        WHERE video_commentcount IS NOT NULL'''
            mycursor.execute(query4)
            mydb.commit()
            q4 = mycursor.fetchall()
            df4 = pd.DataFrame(q4, columns=["Video_Title", "No_Of_Comments"])
            st.dataframe(df4)

elif ques == "5.Which videos have the highest number of likes, and what are their corresponding channel names?":
            query5 = '''SELECT Channel_Title, Video_Title, MAX(Likes) AS Likes
                        FROM (
                            SELECT channel_name AS Channel_Title, video_name AS Video_Title, video_likes AS Likes
                            FROM videodetails
                            WHERE video_likes IS NOT NULL
                        ) AS top_likes
                        GROUP BY Channel_Title, Video_Title
                        ORDER BY MAX(Likes) DESC'''
            mycursor.execute(query5)
            mydb.commit()
            q5 = mycursor.fetchall()
            df5 = pd.DataFrame(q5, columns=["Channel_Title", "Video_Title", "Likes"])
            st.dataframe(df5)

elif ques == "6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
            query6 = '''
                SELECT video_name AS Video_Title, 
                    SUM(video_likes) AS Likes, 
                    SUM(video_dislikes) AS Dislikes 
                FROM videodetails 
                GROUP BY video_name;
            '''
            mycursor.execute(query6)
            mydb.commit()
            q6 = mycursor.fetchall()
            df6 = pd.DataFrame(q6, columns=["Video_Title", "Likes", "Dislikes"])
            st.dataframe(df6)

elif ques == "7.What is the total number of views for each channel, and what are their corresponding channel names?":
            query7 = '''
                SELECT channel_name AS Channel_Title,
                    SUM(channel_viewcount) AS Channel_Views 
                FROM channeldetails 
                GROUP BY channel_name;
            '''
            mycursor.execute(query7)
            mydb.commit()
            q7 = mycursor.fetchall()
            df7 = pd.DataFrame(q7, columns=["Channel_Title", "Channel_Views"])
            st.dataframe(df7)

elif ques == "8.What are the names of all the channels that have published videos in the year 2022?":
            query8='''SELECT channel_name AS Channel_Title,video_name AS Video_Title,video_publishedAt AS Video_Published 
            FROM videodetails 
            WHERE extract(year from video_publishedAt)=2022;'''
            mycursor.execute(query8)
            mydb.commit()
            q8 = mycursor.fetchall()
            df8 = pd.DataFrame(q8, columns=["Channel_Title","Video_Title","Video_Published"])
            st.dataframe(df8)

elif ques == "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?":
            query9 = '''SELECT channel_name AS Channel_Title,AVG(video_duration) AS Avg_dur FROM videodetails GROUP BY channel_name;'''
            mycursor.execute(query9)
            mydb.commit()
            q9 = mycursor.fetchall()
            df9 = pd.DataFrame(q9, columns=["Channel_Title", "Avg_Dur"])
            st.dataframe(df9)

elif ques == "10.Which videos have the highest number of comments, and what are their corresponding channel names?":
            query10 = '''SELECT channel_name AS Channel_Title, video_name AS Video_Title, video_commentcount AS Comments 
            FROM videodetails 
            WHERE video_commentcount > 0
            ORDER BY video_commentcount DESC'''
            mycursor.execute(query10)
            q10 = mycursor.fetchall()
            mydb.commit()
            df10 = pd.DataFrame(q10, columns=["Channel_Title", "Video_Title", "Comments"])
            st.dataframe(df10, width=1000)
                


