USERS = {}
from cryptography.fernet import Fernet
import base64
import hashlib
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from eth_account import Account

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from models import NFTCredential, SessionLocal, User



from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import Depends


from sqlalchemy.orm import Session
import logging
import os
import json
from datetime import datetime, timezone
from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel

class GoogleTokenRequest(BaseModel):
    token: str
#chirag code above

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from seeds import Web3Seed
from utils import apply_growth
from models import Credential



from sqlalchemy.orm import Session
import logging
import os
import json
from datetime import datetime, timezone
from typing import Optional


from groq import Groq
import os
from dotenv import load_dotenv # Add this
load_dotenv()                # And this





from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))

NFT_ABI = [
    {
        "inputs": [{"internalType":"address","name":"to","type":"address"}],
        "name":"mint",
        "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
        "stateMutability":"nonpayable",
        "type":"function"
    }
]

nft_contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv("NFT_CONTRACT_ADDRESS")),
    abi=NFT_ABI
)

OWNER_ACCOUNT = w3.eth.account.from_key(
    os.getenv("NFT_OWNER_PRIVATE_KEY")
)









# Now your existing code will work!
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))





app = FastAPI()
logger = logging.getLogger(__name__)


print("GROQ API KEY LOADED:", bool(os.getenv("GROQ_API_KEY")))


def _db_unavailable_error() -> HTTPException:
    return HTTPException(status_code=503, detail="Saving and loading are temporarily disabled.")


#Chirag 

def get_fernet():
    secret = os.getenv("WALLET_ENCRYPTION_SECRET")
    key = hashlib.sha256(secret.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_private_key(pk: str) -> str:
    return get_fernet().encrypt(pk.encode()).decode()


def decrypt_private_key(enc: str) -> str:
    return get_fernet().decrypt(enc.encode()).decode()


def verify_google_id_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )

        return {
            "google_sub": idinfo["sub"],
            "email": idinfo.get("email"),
            "email_verified": idinfo.get("email_verified", False),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")


def get_fernet():
    secret = os.getenv("WALLET_SECRET_KEY")
    key = hashlib.sha256(secret.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def create_wallet():
    acct = Account.create()
    return {
        "address": acct.address,
        "private_key": acct.key.hex()
    }
#till here

DB_AVAILABLE = False
SessionLocal = None  # Will be set if database initializes successfully

try:
    from models import (
        create_tables, get_db, GameSession, SearchResult, Branch, 
        Leaf, Flashcard, Fruit, Flower, SessionLocal as ModelSessionLocal
    )

    create_tables()
    DB_AVAILABLE = True
    SessionLocal = ModelSessionLocal
    logger.info("Database initialized successfully.")
except Exception as exc:
    logger.error("Database initialization failed: %s", exc)

    def get_db():  # type: ignore
        raise _db_unavailable_error()



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_game():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))

class SearchRequest(BaseModel):
    query: str

class WebSearchRequest(BaseModel):
    query: str
    count: int = 5
    negative_prompts: list = []  # List of existing search results to exclude

class SaveGameStateRequest(BaseModel):
    original_search_query: str
    search_results: list
    branches: list
    leaves: list
    fruits: list
    flowers: list
    flashcards: list = []
    camera_offset: dict = {"x": 0.0, "y": 0.0}

class LoadGameStateRequest(BaseModel):
    session_id: int

class CreateFlashcardsRequest(BaseModel):
    branch_id: Optional[int] = None
    count: int = 5
    search_result: Optional[dict] = None  # For frontend data
    node_position: Optional[dict] = None  # Node position for linking back to tree

class DeleteGameStateRequest(BaseModel):
    session_id: int

class GenerateQuizRequest(BaseModel):
    flashcards: list

class PlantSeedRequest(BaseModel):
    seed: Web3Seed

@app.post("/api/search")
async def search(request: SearchRequest):
    try:
        prompt = f"""
        You are an educational AI.

        Generate EXACTLY 5 distinct knowledge areas for:
        "{request.query}"

        Return ONLY valid JSON in the following format:
        {{
          "areas": [
            {{
              "name": "Area name",
              "description": "Short explanation",
              "search_query": "Search query for deeper study"
            }}
          ]
        }}

        Rules:
        - Exactly 5 items in areas
        - No markdown
        - No explanations outside JSON
        """

        response = groq_client.chat.completions.create(
             model="llama-3.1-8b-instant",
             messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.5
         )

        raw_text = response.choices[0].message.content



        print("\n========== GEMINI RAW RESPONSE ==========")
        print(raw_text)
        print("========== END RESPONSE ==========\n")

        structured_data = None

        # Try to extract JSON safely
        try:
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            if start != -1 and end != -1:
                structured_data = json.loads(raw_text[start:end])
        except Exception:
            structured_data = None

        # 🚑 Fallback if Gemini response is invalid
        if not structured_data or "areas" not in structured_data:
            structured_data = {
                "areas": [
                    {
                        "name": f"{request.query} – Concept {i+1}",
                        "description": f"An important concept related to {request.query}.",
                        "search_query": request.query
                    }
                    for i in range(5)
                ]
            }

        results = []
        for i, area in enumerate(structured_data["areas"]):
            results.append({
                "id": i,
                "title": area["name"],
                "url": f"https://example.com/{request.query.replace(' ', '-')}-{area['name'].lower().replace(' ', '-')}",
                "date": "2024-01-01",
                "snippet": area["description"],
                "llm_content": f"{area['name']}\n\n{area['description']}"
            })

        return {
            "query": request.query,
            "results": results,
            "structured_data": structured_data
        }

    except Exception as e:
        print("SEARCH ERROR:", str(e))
        return {
            "error": str(e),
            "query": request.query
        }

@app.post("/api/web-search")
def web_search(request: WebSearchRequest):
    try:
        negative_text = ""
        if request.negative_prompts:
            negative_text = (
                "Avoid generating content related to these topics:\n"
                + ", ".join(request.negative_prompts)
            )

        prompt = f"""
        Generate {request.count} NEW and DISTINCT insights about:
        "{request.query}"

        {negative_text}

        Return ONLY valid JSON in this format:
        {{
          "results": [
            {{
              "title": "Insight title",
              "snippet": "Short explanation of the insight"
            }}
          ]
        }}

        Rules:
        - Do NOT repeat avoided topics
        - No markdown
        - No explanations outside JSON
        """

        # ✅ GROQ CALL (REPLACEMENT)
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        raw_text = response.choices[0].message.content.strip()

        # Extract JSON safely
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        json_text = raw_text[start:end]

        data = json.loads(json_text)

        results = []
        for i, item in enumerate(data["results"]):
            results.append({
                "id": i,
                "title": item["title"],
                "url": f"https://example.com/{item['title'].lower().replace(' ', '-')}",
                "date": "2024-01-01",
                "snippet": item["snippet"],
                "llm_content": item["snippet"],
                "images": []
            })

        return {"query": request.query, "results": results}

    except Exception as e:
        return {"error": str(e), "query": request.query}


@app.post("/api/save-game-state")
async def save_game_state(request: SaveGameStateRequest, db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        raise _db_unavailable_error()
    try:
        # Create new game session
        game_session = GameSession(
            original_search_query=request.original_search_query,
            camera_offset_x=request.camera_offset.get("x", 0.0) if request.camera_offset else 0.0,
            camera_offset_y=request.camera_offset.get("y", 0.0) if request.camera_offset else 0.0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(game_session)
        db.flush()  # Get the ID
        
        # Save search results
        search_result_objects = []
        for result in request.search_results:
            search_result = SearchResult(
                game_session_id=game_session.id,
                title=result.get("title", ""),
                url=result.get("url", ""),
                snippet=result.get("snippet", ""),
                llm_content=result.get("llm_content", ""),
                search_query=result.get("search_query", ""),
                created_at=datetime.now(timezone.utc)
            )
            db.add(search_result)
            search_result_objects.append(search_result)
        
        db.flush()  # Get search result IDs
        
        # Save branches with hierarchy tracking
        branch_objects = []
        for i, branch_data in enumerate(request.branches):
            search_result_id = None
            
            # Check if branch has its own search result data
            if branch_data.get("searchResult"):
                # Create a new search result for this branch
                branch_search_result = SearchResult(
                    game_session_id=game_session.id,
                    title=branch_data["searchResult"].get("title", ""),
                    url=branch_data["searchResult"].get("url", ""),
                    snippet=branch_data["searchResult"].get("snippet", ""),
                    llm_content=branch_data["searchResult"].get("llm_content", ""),
                    search_query=branch_data["searchResult"].get("search_query", ""),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(branch_search_result)
                db.flush()  # Get the ID
                search_result_id = branch_search_result.id
            elif i < len(search_result_objects):
                # Fallback to index-based matching for initial branches
                search_result_id = search_result_objects[i].id
            else:
                search_result_id = None
            
            branch = Branch(
                game_session_id=game_session.id,
                search_result_id=search_result_id,
                parent_branch_id=branch_data.get("parentBranchId"),  # Track parent
                start_x=branch_data.get("start", {}).get("x", 0),
                start_y=branch_data.get("start", {}).get("y", 0),
                end_x=branch_data.get("end", {}).get("x", 0),
                end_y=branch_data.get("end", {}).get("y", 0),
                length=branch_data.get("length", 0),
                max_length=branch_data.get("maxLength", 0),
                angle=branch_data.get("angle", 0),
                thickness=branch_data.get("thickness", 1),
                generation=branch_data.get("generation", 0),
                is_growing=branch_data.get("isGrowing", False),
                growth_speed=branch_data.get("growthSpeed", 1.0),
                node_type=branch_data.get("nodeType", "branch"),
                created_at=datetime.now(timezone.utc)
            )
            db.add(branch)
            branch_objects.append(branch)
        
        db.flush()  # Get branch IDs
        
        # Save leaves
        for leaf_data in request.leaves:
            leaf = Leaf(
                game_session_id=game_session.id,
                branch_id=leaf_data.get("branchId"),  # Can be None now
                x=leaf_data.get("x", 0),
                y=leaf_data.get("y", 0),
                size=leaf_data.get("size", 1.0),
                created_at=datetime.now(timezone.utc)
            )
            db.add(leaf)
        
        # Save fruits
        for fruit_data in request.fruits:
            fruit = Fruit(
                game_session_id=game_session.id,
                x=fruit_data.get("x", 0),
                y=fruit_data.get("y", 0),
                type=fruit_data.get("type", "apple"),
                size=fruit_data.get("size", 1.0),
                created_at=datetime.now(timezone.utc)
            )
            db.add(fruit)
        
        # Save flowers
        for flower_data in request.flowers:
            flower = Flower(
                game_session_id=game_session.id,
                x=flower_data.get("x", 0),
                y=flower_data.get("y", 0),
                type=flower_data.get("type", "🌸"),
                size=flower_data.get("size", 1.0),
                created_at=datetime.now(timezone.utc)
            )
            db.add(flower)
        
        # Save flashcards
        for flashcard_data in request.flashcards:
            # Extract node position if available
            node_position = flashcard_data.get("node_position", {})
            flashcard = Flashcard(
                game_session_id=game_session.id,
                branch_id=flashcard_data.get("branch_id"),
                front=flashcard_data.get("front", ""),
                back=flashcard_data.get("back", ""),
                difficulty=flashcard_data.get("difficulty", "medium"),
                category=flashcard_data.get("category", ""),
                node_position_x=node_position.get("x"),
                node_position_y=node_position.get("y"),
                created_at=datetime.now(timezone.utc)
            )
            db.add(flashcard)
        
        db.commit()
        
        return {
            "success": True,
            "session_id": game_session.id,
            "message": "Game state saved successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e), "success": False}

@app.post("/api/load-game-state")
async def load_game_state(request: LoadGameStateRequest, db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        raise _db_unavailable_error()
    try:
        # Get game session
        game_session = db.query(GameSession).filter(GameSession.id == request.session_id).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # Get all related data
        search_results = db.query(SearchResult).filter(SearchResult.game_session_id == request.session_id).all()
        branches = db.query(Branch).filter(Branch.game_session_id == request.session_id).all()
        leaves = db.query(Leaf).filter(Leaf.game_session_id == request.session_id).all()
        flashcards = db.query(Flashcard).filter(Flashcard.game_session_id == request.session_id).all()
        fruits = db.query(Fruit).filter(Fruit.game_session_id == request.session_id).all()
        flowers = db.query(Flower).filter(Flower.game_session_id == request.session_id).all()
        
        # Convert to dictionaries
        search_results_data = []
        for result in search_results:
            search_results_data.append({
                "id": result.id,
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "llm_content": result.llm_content,
                "search_query": result.search_query
            })
        
        branches_data = []
        for branch in branches:
            branches_data.append({
                "id": branch.id,
                "start": {"x": branch.start_x, "y": branch.start_y},
                "end": {"x": branch.end_x, "y": branch.end_y},
                "length": branch.length,
                "maxLength": branch.max_length,
                "angle": branch.angle,
                "thickness": branch.thickness,
                "generation": branch.generation,
                "isGrowing": branch.is_growing,
                "growthSpeed": branch.growth_speed,
                "nodeType": branch.node_type,
                "parentBranchId": branch.parent_branch_id,
                "searchResult": {
                    "id": branch.search_result.id if branch.search_result else None,
                    "title": branch.search_result.title if branch.search_result else None,
                    "url": branch.search_result.url if branch.search_result else None,
                    "snippet": branch.search_result.snippet if branch.search_result else None,
                    "llm_content": branch.search_result.llm_content if branch.search_result else None
                } if branch.search_result else None
            })
        
        leaves_data = []
        for leaf in leaves:
            leaves_data.append({
                "id": leaf.id,
                "x": leaf.x,
                "y": leaf.y,
                "size": leaf.size,
                "branchId": leaf.branch_id
            })
        
        fruits_data = []
        for fruit in fruits:
            fruits_data.append({
                "id": fruit.id,
                "x": fruit.x,
                "y": fruit.y,
                "type": fruit.type,
                "size": fruit.size
            })
        
        flowers_data = []
        for flower in flowers:
            flowers_data.append({
                "id": flower.id,
                "x": flower.x,
                "y": flower.y,
                "type": flower.type,
                "size": flower.size
            })
        
        flashcards_data = []
        for flashcard in flashcards:
            flashcards_data.append({
                "id": flashcard.id,
                "branch_id": flashcard.branch_id,
                "front": flashcard.front,
                "back": flashcard.back,
                "difficulty": flashcard.difficulty,
                "category": flashcard.category,
                "node_position": {
                    "x": flashcard.node_position_x,
                    "y": flashcard.node_position_y
                } if flashcard.node_position_x is not None and flashcard.node_position_y is not None else None,
                "created_at": flashcard.created_at.isoformat(),
                "last_reviewed": flashcard.last_reviewed.isoformat() if flashcard.last_reviewed else None,
                "review_count": flashcard.review_count
            })
        
        return {
            "success": True,
            "game_state": {
                "original_search_query": game_session.original_search_query,
                "search_results": search_results_data,
                "branches": branches_data,
                "leaves": leaves_data,
                "flashcards": flashcards_data,
                "fruits": fruits_data,
                "flowers": flowers_data,
                "camera_offset": {"x": game_session.camera_offset_x, "y": game_session.camera_offset_y},
                "created_at": game_session.created_at.isoformat(),
                "updated_at": game_session.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/game-sessions")
async def get_game_sessions(db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        raise _db_unavailable_error()
    try:
        sessions = db.query(GameSession).order_by(GameSession.updated_at.desc()).all()
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "id": session.id,
                "original_search_query": session.original_search_query,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            })
        return {"success": True, "sessions": sessions_data}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/create-flashcards")
async def create_flashcards(request: CreateFlashcardsRequest):
    db_session: Optional[Session] = None
    branch = None

    try:
        # Handle both database branches and frontend data
        if request.branch_id:
            if not DB_AVAILABLE or SessionLocal is None:
                raise _db_unavailable_error()

            db_session = SessionLocal()
            branch = db_session.query(Branch).filter(Branch.id == request.branch_id).first()
            if not branch:
                raise HTTPException(status_code=404, detail="Branch not found")

            if not branch.search_result:
                raise HTTPException(status_code=400, detail="Branch has no search result data")

            search_result_data = {
                "title": branch.search_result.title,
                "llm_content": branch.search_result.llm_content,
                "snippet": branch.search_result.snippet
            }

        elif request.search_result:
            search_result_data = request.search_result
        else:
            raise HTTPException(status_code=400, detail="Either branch_id or search_result must be provided")

        # ---------- GROQ FLASHCARD GENERATION ----------
        flashcard_prompt = f"""
You are an educational AI that creates deep, explanatory flashcards.

Based on the content below, generate EXACTLY {request.count} flashcards.

Content:
Title: {search_result_data.get('title', '')}
Text: {search_result_data.get('llm_content', '')}

Return ONLY valid JSON in the following format:
[
  {{
    "front": "Clear conceptual question",
    "back": "A detailed explanation answering the question",
    "difficulty": "easy | medium | hard"
  }}
]

Answer requirements:
- Each "back" answer must be at least 3–5 full sentences
- Answers should explain *why* and *how*, not just define terms
- Use examples or analogies where helpful
- Assume the learner is intelligent but new to the topic

Rules:
- No markdown
- No bullet points
- No explanations outside JSON
- JSON array only
"""


        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": flashcard_prompt}],
            temperature=0.4
        )

        raw_text = response.choices[0].message.content.strip()
        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1

        try:
            start = raw_text.find("[")
            end = raw_text.rfind("]") + 1
            structured_flashcards = json.loads(raw_text[start:end])
        except Exception as e:
           raise HTTPException(
                status_code=500,
                detail=f"Flashcard JSON parse failed. Raw response: {raw_text}"
    )


        created_flashcards = []

        for card in structured_flashcards:
            if request.branch_id:
                flashcard = Flashcard(
                    game_session_id=branch.game_session_id,
                    branch_id=branch.id,
                    front=card["front"],
                    back=card["back"],
                    difficulty=card["difficulty"],
                    category=branch.search_result.title,
                    created_at=datetime.now(timezone.utc)
                )
                db_session.add(flashcard)
                created_flashcards.append({
                    "front": flashcard.front,
                    "back": flashcard.back,
                    "difficulty": flashcard.difficulty
                })
            else:
                created_flashcards.append(card)

        # 🌱 Growth logic — MUST be inside try
        if request.branch_id and branch:
            garden = db_session.query(GameSession).filter(
                GameSession.id == branch.game_session_id
            ).first()

            if garden:
                garden.maturity = apply_growth(garden.maturity, 15)
                garden.last_growth_at = datetime.now(timezone.utc)
                if garden.maturity == 100:
                    garden.credential_earned = True
                    auto_mint_if_eligible(db_session, garden)

        if db_session:
            db_session.commit()

        return {"success": True, "flashcards": created_flashcards}

    except HTTPException:
        if db_session:
            db_session.rollback()
        raise

    except Exception as e:
        if db_session:
            db_session.rollback()
        return {"success": False, "error": str(e)}

    finally:
        if db_session:
            db_session.close()





@app.get("/api/flashcards/{branch_id}")
async def get_flashcards(branch_id: int, db: Session = Depends(get_db)):
    try:
        flashcards = db.query(Flashcard).filter(Flashcard.branch_id == branch_id).all()
        
        flashcards_data = []
        for flashcard in flashcards:
            flashcards_data.append({
                "id": flashcard.id,
                "front": flashcard.front,
                "back": flashcard.back,
                "difficulty": flashcard.difficulty,
                "category": flashcard.category,
                "created_at": flashcard.created_at.isoformat(),
                "last_reviewed": flashcard.last_reviewed.isoformat() if flashcard.last_reviewed else None,
                "review_count": flashcard.review_count
            })
        
        return {
            "success": True,
            "flashcards": flashcards_data
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/delete-game-state")
async def delete_game_state(request: DeleteGameStateRequest, db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        raise _db_unavailable_error()
    try:
        # Get the game session
        game_session = db.query(GameSession).filter(GameSession.id == request.session_id).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # Delete the game session (cascade will handle related records)
        db.delete(game_session)
        db.commit()
        
        return {
            "success": True,
            "message": f"Game session {request.session_id} deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e), "success": False}
@app.post("/api/generate-quiz")
async def generate_quiz(request: GenerateQuizRequest):
    db_session: Optional[Session] = None

    try:
        # ---------------- Prepare flashcard content ----------------
        flashcard_data = "\n".join([
            f"Q: {card.get('front', '')}\nA: {card.get('back', '')}"
            for card in request.flashcards
        ])

        quiz_prompt = f"""
        You are an educational AI.

        Based on the flashcards below, generate EXACTLY 5 challenging
        multiple-choice questions that test understanding (not memorization).

        Flashcards:
        {flashcard_data}

        Rules:
        - Each question must be new (not copied from flashcards)
        - Correct answer: 50–100 characters
        - 3 plausible but incorrect options
        - Normal sentence casing
        - No all-caps

        Return ONLY valid JSON in this format:
        [
          {{
            "question": "Conceptual question",
            "correctAnswer": "Correct answer",
            "options": [
              "Correct answer",
              "Wrong option 1",
              "Wrong option 2",
              "Wrong option 3"
            ]
          }}
        ]
        """

        # ---------------- GROQ CALL ----------------
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": quiz_prompt}],
            temperature=0.4
        )

        raw_text = response.choices[0].message.content.strip()

        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1
        questions_data = json.loads(raw_text[start:end])

        # ---------------- Shuffle options ----------------
        import random
        questions = []
        for q in questions_data:
            options = q["options"]
            random.shuffle(options)
            questions.append({
                "question": q["question"],
                "correctAnswer": q["correctAnswer"],
                "options": options
            })

        # ---------------- 🌱 Growth Logic ----------------
        if (
            DB_AVAILABLE
            and SessionLocal
            and request.flashcards
            and isinstance(request.flashcards[0], dict)
            and "branch_id" in request.flashcards[0]
        ):
            branch_id = request.flashcards[0]["branch_id"]

            db_session = SessionLocal()
            branch = db_session.query(Branch).filter(Branch.id == branch_id).first()

            if branch:
                garden = db_session.query(GameSession).filter(
                    GameSession.id == branch.game_session_id
                ).first()

                if garden:
                    garden.maturity = apply_growth(garden.maturity, 25)
                    garden.last_growth_at = datetime.now(timezone.utc)

                    if garden.maturity == 100:
                        garden.credential_earned = True
                        auto_mint_if_eligible(db_session, garden)

                    db_session.commit()

        # ---------------- Return response ----------------
        return {
            "success": True,
            "questions": questions
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Failed to parse quiz data from AI response"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if db_session:
            db_session.close()


@app.get("/api/garden/{garden_id}")
async def get_garden(garden_id: int, db: Session = Depends(get_db)):
    garden = db.query(GameSession).filter(GameSession.id == garden_id).first()

    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    return {
        "id": garden.id,
        "seed": garden.seed_type,
        "maturity": garden.maturity,
        "credential_earned": garden.credential_earned,
        "created_at": garden.created_at.isoformat()
    }



@app.post("/api/plant-seed")
async def plant_seed(
    request: PlantSeedRequest,
    db: Session = Depends(get_db)
):
    try:
        garden = GameSession(
            original_search_query=request.seed.value,
            seed_type=request.seed.value,
            maturity=0,
            credential_earned=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(garden)
        db.commit()
        db.refresh(garden)

        return {
            "success": True,
            "garden": {
                "id": garden.id,
                "seed": garden.seed_type,
                "maturity": garden.maturity,
                "credential_earned": garden.credential_earned
            }
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@app.post("/api/mint-credential/{garden_id}")
async def mint_credential(
    garden_id: int,
    db: Session = Depends(get_db)
):
    # 1. Fetch garden
    garden = db.query(GameSession).filter(GameSession.id == garden_id).first()

    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    # 2. Check maturity
    if not garden.credential_earned:
        raise HTTPException(
            status_code=400,
            detail="Garden not mature enough to mint credential"
        )

    # 3. Prevent double mint
    existing = db.query(Credential).filter(
        Credential.game_session_id == garden.id
    ).first()

    if existing:
        return {
            "success": True,
            "credential": json.loads(existing.credential_metadata),
            "message": "Credential already minted"
        }

    # 4. NFT-like metadata
    metadata = {
        "name": f"BrainBonsai Credential — {garden.seed_type}",
        "description": f"Proof of mastery in {garden.seed_type}",
        "topic": garden.seed_type,
        "garden_id": garden.id,
        "maturity": garden.maturity,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "issuer": "BrainBonsai Garden",
        "image": "https://brainbonsai.xyz/nft-placeholder.png",
        "attributes": [
            {"trait_type": "Topic", "value": garden.seed_type},
            {"trait_type": "Completion", "value": "100%"},
            {"trait_type": "Platform", "value": "BrainBonsai"}
        ]
    }

    # 5. Create credential record
    credential = Credential(
        game_session_id=garden.id,
        topic=garden.seed_type,
        credential_metadata=json.dumps(metadata)
    )

    db.add(credential)
    db.commit()
    db.refresh(credential)

    # 6. Return minted credential
    return {
        "success": True,
        "credential": metadata
    }


@app.post("/api/mint-now")
async def mint_now(payload: dict, db: Session = Depends(get_db)):
    """Mint directly to a wallet without a garden. Payload: { wallet_address, topic }
    Useful for simplified automatic minting from the frontend when you don't want to create a garden.
    """
    try:
        wallet = payload.get("wallet_address")
        topic = payload.get("topic", "BrainBonsai Credential")

        if not wallet:
            raise HTTPException(status_code=400, detail="wallet_address is required")

        checksum = Web3.to_checksum_address(wallet)

        nonce = w3.eth.get_transaction_count(OWNER_ACCOUNT.address)
        tx = nft_contract.functions.mint(checksum).build_transaction({
            "from": OWNER_ACCOUNT.address,
            "nonce": nonce,
            "gas": 250_000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "chainId": 11155111
        })

        signed_tx = OWNER_ACCOUNT.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)


        metadata = {
            "name": f"BrainBonsai Credential — {topic}",
            "tx_hash": tx_hash.hex(),
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "issuer": "BrainBonsai"
        }

        credential = Credential(
            game_session_id=None,
            topic=topic,
            credential_metadata=json.dumps(metadata),
            minted_at=datetime.now(timezone.utc)
        )
        db.add(credential)
        db.commit()

        return {"success": True, "tx_hash": tx_hash.hex(), "credential": metadata}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug/gardens")
async def debug_gardens(db: Session = Depends(get_db)):
    gardens = db.query(GameSession).all()

    return [
        {
            "id": g.id,
            "seed": g.seed_type,
            "maturity": g.maturity,
            "credential_earned": g.credential_earned
        }
        for g in gardens
    ]

@app.post("/api/demo/grow/{garden_id}")
async def demo_grow_garden(
    garden_id: int,
    db: Session = Depends(get_db)
):
    garden = db.query(GameSession).filter(GameSession.id == garden_id).first()

    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    garden.maturity = 100
    garden.credential_earned = True
    garden.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(garden)

    return {
        "success": True,
        "garden": {
            "id": garden.id,
            "seed": garden.seed_type,
            "maturity": garden.maturity,
            "credential_earned": garden.credential_earned
        }
    }

#chirag code below 

def verify_google_id_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )

        return {
            "google_sub": idinfo["sub"],
            "email": idinfo.get("email"),
            "email_verified": idinfo.get("email_verified", False),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

class GoogleTokenRequest(BaseModel):
    token: str





@app.post("/api/auth/google/verify")
def google_verify(
    request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    user_info = verify_google_id_token(request.token)

    user = db.query(User).filter(
        User.google_sub == user_info["google_sub"]
    ).first()

    if not user:
        acct = Account.create()
        encrypted_pk = encrypt_private_key(acct.key.hex())

        user = User(
            google_sub=user_info["google_sub"],
            email=user_info["email"],
            wallet_address=acct.address,
            encrypted_private_key=encrypted_pk
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "wallet_address": user.wallet_address
        }
    }


@app.post("/api/auth/logout")
def logout():
    """Logout endpoint - clears user session and returns success"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }


# main.py

def auto_mint_if_eligible(db: Session, garden: GameSession, wallet_address: Optional[str] = None):
    # 1. Check if maturity is 100 and it hasn't been earned yet
    if garden.maturity < 100 or garden.credential_earned:
        return

    # 2. Check for existing credential in the database to prevent double-minting
    existing = db.query(Credential).filter(
        Credential.game_session_id == garden.id
    ).first()
    if existing:
        return 

    # 3. Get the user's wallet address. Try garden.user_id first, otherwise use provided wallet_address
    user = None
    try:
        if getattr(garden, 'user_id', None):
            user = db.query(User).filter(User.id == garden.user_id).first()
    except Exception:
        user = None

    if (not user or not user.wallet_address) and wallet_address:
        user = db.query(User).filter(User.wallet_address == wallet_address).first()

    if not user or not user.wallet_address:
        return

    try:
        # 4. Prepare the Minting Transaction
        nonce = w3.eth.get_transaction_count(OWNER_ACCOUNT.address)
        
        tx = nft_contract.functions.mint(
            Web3.to_checksum_address(user.wallet_address)
        ).build_transaction({
            "from": OWNER_ACCOUNT.address,
            "nonce": nonce,
            "gas": 250_000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "chainId": 11155111  # Sepolia Testnet [cite: 1]
        })

        # 5. Sign and Send
        signed_tx = OWNER_ACCOUNT.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)


        # 6. Record the success in the database
        metadata = {
            "name": f"BrainBonsai Credential — {garden.seed_type}",
            "tx_hash": tx_hash.hex(),
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "topic": garden.seed_type,
            "issuer": "BrainBonsai"
        }

        credential = Credential(
            game_session_id=garden.id,
            topic=garden.seed_type or "",
            credential_metadata=json.dumps(metadata),
            minted_at=datetime.now(timezone.utc)
        )
        garden.credential_earned = True
        db.add(credential)
        db.commit()

        print(f"Successfully minted NFT for session {garden.id}. Tx: {tx_hash.hex()}")

    except Exception as e:
        db.rollback()
        print(f"Minting failed: {e}")


@app.post("/api/apply-growth")
async def handle_growth(session_id: int, growth_amount: int, wallet_address: Optional[str] = None, db: Session = Depends(get_db)):
    garden = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    # Use your utility to apply growth safely
    garden.maturity = apply_growth(garden.maturity, growth_amount)
    db.commit()

    # Check for NFT eligibility after every growth update; forward optional wallet_address
    auto_mint_if_eligible(db, garden, wallet_address)

    return {"new_maturity": garden.maturity, "minted": garden.credential_earned}
def apply_growth_and_check_mint(db: Session, session_id: int, increment: int):
    garden = db.query(GameSession).filter(GameSession.id == session_id).first()
    
    # 1. Update Maturity
    garden.maturity = min(100, garden.maturity + increment)
    
    # 2. Check if we just hit 100 and haven't minted yet
    should_mint = False
    if garden.maturity >= 100 and not garden.credential_earned:
        should_mint = True
        # Mark as earned immediately to prevent race conditions
        garden.credential_earned = True 
    
    db.commit()

    if should_mint:
        # Call your existing auto_mint_if_eligible function
        # This function should handle the Web3 transaction
        auto_mint_if_eligible(db, garden)
    
    return garden
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")
from fastapi.responses import FileResponse

@app.get("/sim")
def sim():
    return FileResponse("../frontend/js/simulation.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
