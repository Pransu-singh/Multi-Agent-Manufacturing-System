"""Allows: python -m backend"""
from backend.app import create_app
from backend.config import cfg

app = create_app()

if __name__ == "__main__":
    import sys
    if "--server" in sys.argv or True:
        print(f"\n  🚀  MFG Agent Server")
        print(f"  URL   → http://localhost:{cfg.PORT}")
        print(f"  Model → {cfg.GROQ_MODEL}\n")

        app.run(
            host=cfg.HOST, 
            port=cfg.PORT,
            debug=cfg.DEBUG,
            threaded=True
        )

