from api.Config import app
from api.routers import feedback, hiscore, legacy, player, prediction, report, scaper, label

app.include_router(hiscore.router)
app.include_router(player.router)
app.include_router(prediction.router)
app.include_router(feedback.router)
app.include_router(report.router)
app.include_router(legacy.router)
app.include_router(scaper.router)
app.include_router(label.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}