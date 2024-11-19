import praw
import os

# Credentials
client_id = 'b8....'
client_secret = '24csi...'
user_agent = 'linux:com.example.myapp:v1.0.0 (by /u/username)'

# Create a Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Specify the subreddit and the number of top posts you want to fetch
subreddit_name = 'Nature'
top_n = 10

# Access the subreddit
subreddit = reddit.subreddit(subreddit_name)

# Fetch the top N posts from the subreddit
top_posts = subreddit.top(limit=top_n)

APPLICATIONS_FILEPATH = '/home/editor/applications/'
APPLICATIONS = os.listdir(APPLICATIONS_FILEPATH)

for application in APPLICATIONS:
    # Path to store the traversed IDs
    ids_traversed_path = os.path.join(APPLICATIONS_FILEPATH, application, 'raw_text', 'ids_traversed.txt')

    traversed_ids = set()

    # Load the traversed IDs
    if os.path.exists(ids_traversed_path):
        with open(ids_traversed_path, 'r') as file:
            traversed_ids = set(line.strip() for line in file)
    else:
        print(f"File {ids_traversed_path} does not exist for application {application}")
        continue

    # Collect the data
    posts_data = []
    for post in top_posts:
        if post.id not in traversed_ids:
            post_info = {
                'title': post.title,
                'score': post.score,
                'id': post.id,
                'url': post.url,
                'num_comments': post.num_comments,
                'created': post.created,
                'body': post.selftext
            }
            posts_data.append(post_info)
            
            # Save the title and body to separate files
            title_file_path = os.path.join(APPLICATIONS_FILEPATH, application, 'raw_text', f'{post.id}_title.txt')
            body_file_path = os.path.join(APPLICATIONS_FILEPATH, application, 'raw_text', f'{post.id}_body.txt')

            with open(title_file_path, 'w') as title_file:
                title_file.write(post.title)
            
            with open(body_file_path, 'w') as body_file:
                body_file.write(post.selftext)
            
            # Append the post ID to the traversed IDs list
            with open(ids_traversed_path, 'a') as file:
                file.write(post.id + '\n')
            
            # Add the post ID to the set to avoid duplicates in the same run
            traversed_ids.add(post.id)