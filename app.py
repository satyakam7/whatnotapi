#Coded by Sumanjay on 29th Feb 2020
from flask import Flask, request, jsonify
from inshorts import getNews, getNewFromAPi
from flask_cors import CORS
from flask_sock import Sock
from database import get_db, serialize_doc, get_object_id
from datetime import datetime
from bson import ObjectId
import json

# Custom JSON encoder to handle ObjectId and datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
# Set custom JSON encoder for Flask app
app.json.encoder = CustomJSONEncoder
app.secret_key = "i_am_not_feeling_sleepy_so_i_am_coding_this"
import os, json, base64, asyncio, aiohttp

# from flask import Flask, request, jsonify
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants  # pip install livekit-api

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIP2MjWhagPpc3")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "XTk3OmhQYu2KTpUGnQ4Q4yvEUeUzcrmeEJLpsrYFdgM")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://godai-obtudbj9.livekit.cloud")
AZURE_OAI_ENDPOINT = os.getenv("AZURE_OAI_ENDPOINT", "https://satyakam-1859-resource.cognitiveservices.azure.com")
AZURE_OAI_DEPLOYMENT = os.getenv("AZURE_OAI_DEPLOYMENT", "gpt-4o-mini-realtime-preview")
AZURE_OAI_KEY = os.getenv("AZURE_OAI_KEY", "AwX3I3RDHGg49dhMcCnDnDFsXPeQauBHchT58odWoCTZ6em3ItLrJQQJ99BGACHYHv6XJ3w3AAAAACOGrCJ3")

CORS(app)
sock = Sock(app)

# Helper function to create safe JSON responses
def safe_json_response(data, status_code=200):
    """Create a JSON response with proper serialization"""
    try:
        serialized_data = serialize_doc(data)
        return jsonify(serialized_data), status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Serialization error: {str(e)}'
        }), 500

@app.route('/')
def home():
    return 'News API is UP!<br><br>A part of <a href="https://t.me/sjprojects">Sj Projects</a>'

@app.route('/news')
def news():
    if request.method == 'GET':
        category = request.args.get("category")
        if not category:
            return jsonify({
                "error": "please add category in query params"
            }), 404
        return jsonify(getNews(category)), 200


@app.get("/token")
def create_token():
    room = request.args.get("room")   # e.g. ?room=hall&user=ishaan
    user = request.args.get("user")

    if not room or not user:
        return jsonify({"error": "room and user are required"}), 400

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(user)
        .with_grants(VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return jsonify({"token": token})


@app.get("/newsapi")
def newsapi():
    result = getNewFromAPi()
    return safe_json_response(result)


@app.route('/db/news/today', methods=['GET'])
def get_todays_news():
    """Get today's cached news with additional metadata"""
    try:
        result = getNewFromAPi()
        response_data = {
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        }
        return safe_json_response(response_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/db/news/history', methods=['GET'])
def get_news_history():
    """Get historical daily news cache"""
    db = get_db()
    
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        date = request.args.get('date')  # Format: ddmmyyyy
        
        query = {}
        if date:
            query['date'] = date
            
        # Get daily cache entries
        daily_entries = db.find_many('daily', query=query, limit=limit, 
                                   sort=[('created_at', -1)])
        
        return safe_json_response({
            'success': True,
            'data': daily_entries,
            'count': len(daily_entries)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/db/news/search', methods=['GET'])
def search_news():
    """Search news articles by title or content"""
    db = get_db()
    
    try:
        # Get query parameters
        query_text = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        # Search in news collection
        search_query = {
            '$or': [
                {'title': {'$regex': query_text, '$options': 'i'}},
                {'description': {'$regex': query_text, '$options': 'i'}},
                {'content': {'$regex': query_text, '$options': 'i'}}
            ]
        }
        
        articles = db.find_many('news', query=search_query, limit=limit,
                              sort=[('created_at', -1)])
        
        return safe_json_response({
            'success': True,
            'data': articles,
            'count': len(articles),
            'query': query_text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# MongoDB Database Routes
@app.route('/db/articles', methods=['GET', 'POST'])
def articles():
    """Handle articles collection operations"""
    db = get_db()
    
    if request.method == 'GET':
        # Get all articles or filter by query parameters
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        query = {}
        if category:
            query['category'] = category
            
        articles = db.find_many('articles', query=query, limit=limit, 
                               sort=[('created_at', -1)])
        return jsonify({
            'success': True,
            'data': serialize_doc(articles),
            'count': len(articles)
        }), 200
    
    elif request.method == 'POST':
        # Create a new article
        try:
            article_data = request.get_json()
            if not article_data:
                return jsonify({'error': 'No data provided'}), 400
                
            result = db.insert_one('articles', article_data)
            return jsonify({
                'success': True,
                'message': 'Article created successfully',
                'id': str(result.inserted_id)
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/db/articles/<article_id>', methods=['GET', 'PUT', 'DELETE'])
def article_by_id(article_id):
    """Handle individual article operations"""
    db = get_db()
    
    try:
        object_id = get_object_id(article_id)
    except ValueError:
        return jsonify({'error': 'Invalid article ID'}), 400
    
    if request.method == 'GET':
        # Get a specific article
        article = db.find_one('articles', {'_id': object_id})
        if not article:
            return jsonify({'error': 'Article not found'}), 404
            
        return jsonify({
            'success': True,
            'data': serialize_doc(article)
        }), 200
    
    elif request.method == 'PUT':
        # Update an article
        try:
            update_data = request.get_json()
            if not update_data:
                return jsonify({'error': 'No data provided'}), 400
                
            result = db.update_one('articles', 
                                 {'_id': object_id}, 
                                 {'$set': update_data})
            
            if result.matched_count == 0:
                return jsonify({'error': 'Article not found'}), 404
                
            return jsonify({
                'success': True,
                'message': 'Article updated successfully',
                'modified_count': result.modified_count
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        # Delete an article
        try:
            result = db.delete_one('articles', {'_id': object_id})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Article not found'}), 404
                
            return jsonify({
                'success': True,
                'message': 'Article deleted successfully'
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/db/users', methods=['GET', 'POST'])
def users():
    """Handle users collection operations"""
    db = get_db()
    
    if request.method == 'GET':
        # Get all users
        limit = request.args.get('limit', type=int)
        users = db.find_many('users', limit=limit, sort=[('created_at', -1)])
        
        return jsonify({
            'success': True,
            'data': serialize_doc(users),
            'count': len(users)
        }), 200
    
    elif request.method == 'POST':
        # Create a new user
        try:
            user_data = request.get_json()
            if not user_data:
                return jsonify({'error': 'No data provided'}), 400
                
            # Check if user already exists
            existing_user = db.find_one('users', {'email': user_data.get('email')})
            if existing_user:
                return jsonify({'error': 'User with this email already exists'}), 409
                
            result = db.insert_one('users', user_data)
            return jsonify({
                'success': True,
                'message': 'User created successfully',
                'id': str(result.inserted_id)
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/db/collections', methods=['GET'])
def list_collections():
    """List all collections in the database"""
    db = get_db()
    
    try:
        collections = db.db.list_collection_names()
        return jsonify({
            'success': True,
            'collections': collections
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/db/stats', methods=['GET'])
def database_stats():
    """Get database statistics"""
    db = get_db()
    
    try:
        stats = {}
        collections = db.db.list_collection_names()
        
        for collection_name in collections:
            count = db.count_documents(collection_name)
            stats[collection_name] = count
            
        return jsonify({
            'success': True,
            'stats': stats,
            'total_collections': len(collections)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @sock.route("/ws/bridge")
# async def bridge(ws):
#     """
#     Browser sends raw 16-kHz 16-bit little-endian PCM frames (≈320-bytes each)
#     We relay to Azure Realtime → send Azure audio deltas straight back.
#     """
#     url = (f"{os.getenv('AZURE_OAI_ENDPOINT')}/openai/realtime"
#            f"?deployment={os.getenv('AZURE_OAI_DEPLOYMENT')}"
#            f"&api-version=2025-04-01-preview")
#     hdrs = {
#         "api-key": os.getenv("AZURE_OAI_KEY"),
#         "accept": "application/json",
#         # supersede default “text+audio”; we only want audio out
#         "x-openai-realtime-modality": "audio",
#     }

#     async with aiohttp.ClientSession() as s, s.ws_connect(url, headers=hdrs) as aoai:
#         # ----- send session config with your news context -----
#         await aoai.send_json({
#             "type": "session.update",
#             "session": {
#                 "response_format": {
#                     "modality": ["audio"],
#                     "instructions": (
#                         "You are a friendly news explainer. "
#                         "Only answer questions about THIS article: "
#                         f"{request.args.get('heading')} – "
#                         f"{request.args.get('description')}. "
#                         "If the user goes off-topic, politely refuse."
#                     )
#                 }
#             }
#         })                                                                          # :contentReference[oaicite:0]{index=0}

#         # pump data both ways
#         async for msg in ws:
#             if isinstance(msg, bytes):  # audio from browser → Azure
#                 await aoai.send_json({
#                     "type": "input_audio_buffer.append",
#                     "audio": base64.b64encode(msg).decode()
#                 })                                                            # :contentReference[oaicite:1]{index=1}
#             elif msg == "COMMIT":
#                 await aoai.send_json({"type": "input_audio_buffer.commit"})

#             # read every AOAI event, forward any audio chunks back
#             async for evt in aoai:
#                 if evt.type == aiohttp.WSMsgType.TEXT:
#                     data = json.loads(evt.data)
#                     if data.get("type") == "response.audio.delta":
#                         pcm = base64.b64decode(data["audio"])
#                         await ws.send(pcm)                                # browser plays + re-publishes
#                 elif evt.type == aiohttp.WSMsgType.CLOSED:
#                     break

@sock.route("/ws/bridge")
async def bridge(ws):
    """Relay browser PCM → Azure GPT-4o Realtime → PCM back"""
    az_url = (
        f"{os.getenv('AZURE_OAI_ENDPOINT')}/openai/realtime"
        f"?deployment={os.getenv('AZURE_OAI_DEPLOYMENT')}"
        f"&api-version=2025-04-01-preview"
    )
    hdrs = {
        "api-key": os.getenv("AZURE_OAI_KEY"),
        "accept": "application/json",
        "x-openai-realtime-modality": "audio",
    }

    heading = request.args.get("heading", "")
    desc = request.args.get("description", "")

    async with aiohttp.ClientSession() as s, s.ws_connect(az_url, headers=hdrs) as az:
        # prime GPT-4o with context & boundaries
        await az.send_json(
            {
                "type": "session.update",
                "session": {
                    "response_format": {"modality": ["audio"]},
                    "instructions": (
                        "You are an Indian friend explaining news casually. "
                        f"Only discuss this article: '{heading}'. {desc} "
                        "Politely refuse other topics."
                    ),
                },
            }
        )

        async def browser_to_azure():
            async for msg in ws:
                if isinstance(msg, bytes):
                    await az.send_json(
                        {
                            "type": "input_audio_buffer.append",
                            "audio": base64.b64encode(msg).decode(),
                        }
                    )
                elif msg == "COMMIT":
                    await az.send_json({"type": "input_audio_buffer.commit"})

        async def azure_to_browser():
            async for msg in az:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "response.audio.delta":
                        pcm = base64.b64decode(data["audio"])
                        await ws.send(pcm)
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    break

        await asyncio.gather(browser_to_azure(), azure_to_browser())

# tiny helper ------------------------------------------
class AudioFrameStream:
    """Simple iterator yielding fixed-size frames for AOAI and browser."""
    def __init__(self, wav_bytes, frame_ms=20, sample_rate=16000):
        self.frame_bytes = int(sample_rate * frame_ms / 1000 * 2)
        self.wav = memoryview(wav_bytes)

    def __iter__(self):
        for i in range(0, len(self.wav), self.frame_bytes):
            chunk = self.wav[i : i + self.frame_bytes]
            if len(chunk) == self.frame_bytes:
                yield bytes(chunk)
                
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000,use_reloader=True)
