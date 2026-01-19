from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from bot_engine import scan_market
from config import USERS, DEFAULT_BALANCE, DEFAULT_RISK
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SESSIONS = {}

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        SESSIONS[username] = {"balance": DEFAULT_BALANCE, "risk": DEFAULT_RISK}
        return RedirectResponse("/dashboard?user="+username, status_code=302)
    return HTMLResponse("❌ Login Failed")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: str):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.post("/update")
def update_settings(user: str = Form(...), balance: float = Form(...), risk: float = Form(...)):
    SESSIONS[user]["balance"] = balance
    SESSIONS[user]["risk"] = risk
    return RedirectResponse(f"/dashboard?user={user}", status_code=302)

@app.get("/signals")
def get_signals(user: str):
    u = SESSIONS[user]
    return JSONResponse(scan_market(u["balance"], u["risk"]))

@app.post("/autotrade")
def auto_trade(user: str = Form(...), symbol: str = Form(...), signal: str = Form(...)):
    return JSONResponse({"status":"PAPER TRADE EXECUTED","user":user,"symbol":symbol,"action":signal})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
