from api.Config import app
from api.routers import feedback, hiscore, legacy, player, prediction, report, scraper, label, legacy_debug
from concurrent.futures.process import ProcessPoolExecutor

app.include_router(hiscore.router)
app.include_router(player.router)
app.include_router(prediction.router)
app.include_router(feedback.router)
app.include_router(report.router)
app.include_router(legacy.router)
app.include_router(scraper.router)
app.include_router(label.router)
app.include_router(legacy_debug.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()