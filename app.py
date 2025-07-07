from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching [5]
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto-reload templates [5]


GENRES = [
    "dankmemes",
    "wholesomememes",
    "brainrot",
    "ProgrammerHumor",
    "voidmemes",
]

def get_meme(subreddit="memes"):
    url = f"https://meme-api.com/gimme/{subreddit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  
        data = response.json()

        meme_image_url = None
        previews = data.get('preview')

        
        if previews and isinstance(previews, list) and len(previews) > 0:
            if len(previews) >= 2:
                meme_image_url = previews[-2] 
            else:
                meme_image_url = previews[-1] 
        
        if not meme_image_url: 
            meme_image_url = data.get('url')

        if not meme_image_url: # If still no URL after checking common fields
            print(f"No image URL found in API response data for {subreddit}: {data}")
            # if data.get('nsfw') or data.get('spoiler'): # Check if it's NSFW or spoiler if no image
            #      return "/static/fallback.jpg", f"{subreddit} (Post was NSFW/Spoiler or not an image)"
            raise ValueError("No suitable image URL found in API response")

        sub = data.get('subreddit', subreddit)
        return meme_image_url, sub

    except requests.exceptions.Timeout:
        print(f"Timeout error fetching meme from {subreddit}")
        return "/static/fallback.jpg", f"{subreddit} (Timeout)"
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching meme from {subreddit}: {e}")
        return "/static/fallback.jpg", f"{subreddit} (API Error)"
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing meme data for {subreddit}: {e}")
        return "/static/fallback.jpg", f"{subreddit} (Data Error)"
    except Exception as e:
        print(f"An unexpected error occurred for {subreddit}: {e}")
        return "/static/fallback.jpg", "Error (Unknown)"


@app.route('/')
def index():
    fallback_img_url = app.static_url_path + '/fallback.jpg' 
    return render_template('index.html', genres=GENRES, fallback_img_url=fallback_img_url)

@app.route('/fetch_meme')
def fetch_meme_route():
    genre = request.args.get('genre', 'memes')
    meme_pic, sub = get_meme(genre)
    return jsonify({"meme_pic": meme_pic, "sub": sub})

if __name__ == '__main__':
    app.run(debug=True)
