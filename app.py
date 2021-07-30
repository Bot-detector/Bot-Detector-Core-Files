from Config import app
from routers import hiscore, player, prediction, report, legacy

app.include_router(hiscore.router)
app.include_router(player.router)
app.include_router(prediction.router)
app.include_router(report.router)
app.include_router(legacy.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
