from flask import Flask, render_template, request
import pandas as pd
import ytm

app = Flask(__name__)

# Load the dataset from the CSV file
df = pd.read_csv('data_moods.csv')

# Define a mapping of keywords to moods
keyword_mapping = {
    'happy': 'Happy',
    'joyful': 'Happy',
    'excited': 'Energetic',
    'energetic': 'Energetic',
    'sad': 'Sad',
    'melancholic': 'Sad',
    'calm': 'Calm',
    'relaxed': 'Calm'
}


# Function to predict mood from input text
def predict_mood(input_text):
    input_text_lower = input_text.lower()
    moods = set()
    for keyword, mood in keyword_mapping.items():
        if keyword in input_text_lower:
            moods.add(mood)
    return list(moods)


# Function to suggest songs based on moods
def suggest_songs(moods):
    if len(moods) == 0:
        return None
    elif len(moods) == 1:
        specified_mood = moods[0]
        count = 20
    else:
        specified_mood = moods[0]
        count = 10
    filtered_dataset = df[df['mood'].isin(moods)]
    sorted_dataset = filtered_dataset.sort_values(by='popularity', ascending=False)

    # Initialize the YouTube Music API
    api = ytm.YouTubeMusic()
    song_url = lambda song_id: ytm.utils.url_ytm('watch', params={'v': song_id})

    # Get song URLs for recommended songs
    songs = sorted_dataset.head(count)
    for index, song in songs.iterrows():
        song_data = api.search_songs(f"{song['name']} {song['artist']}")['items']
        if song_data:
            song_url_str = song_url(song_data[0]['id'])  # Use a different variable name
            songs.at[index, 'url'] = song_url_str  # Update the 'url' column

    return songs[['name', 'album', 'artist', 'popularity', 'url']]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['mood_input']
        moods = predict_mood(user_input)
        recommendations = suggest_songs(moods)
        if recommendations is not None:
            return render_template('result.html', recommendations=recommendations.to_dict(orient='records'))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
