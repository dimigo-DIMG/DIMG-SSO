import uvicorn
import dotenv

if __name__ == "__main__":
    dotenv.load_dotenv()
    uvicorn.run("app.app:app", host="0.0.0.0", log_level="info")
