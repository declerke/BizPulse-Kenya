import os
import time
import mlflow

from sentiment import finbert_scorer, vader_scorer, textblob_scorer

EXPERIMENT_NAME = "bizpulse-sentiment"
CHAMPION_MODEL = "finbert-sentiment-champion"


def _count_labels(results: list[dict]) -> dict:
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_conf = 0.0
    for r in results:
        counts[r["label"]] += 1
        total_conf += r["confidence"]
    total = len(results) or 1
    return {
        "positive_count": counts["positive"],
        "negative_count": counts["negative"],
        "neutral_count": counts["neutral"],
        "avg_confidence": round(total_conf / total, 4),
    }


def run_experiments(texts: list[str]) -> dict:
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow-server:5000"))
    mlflow.set_experiment(EXPERIMENT_NAME)

    models = {
        "finbert": finbert_scorer.score,
        "vader": vader_scorer.score,
        "textblob": textblob_scorer.score,
    }

    run_ids = {}
    champion_results = None

    for model_name, score_fn in models.items():
        with mlflow.start_run(run_name=model_name) as run:
            mlflow.log_param("model", model_name)
            mlflow.log_param("article_count", len(texts))

            t0 = time.time()
            results = score_fn(texts)
            elapsed_ms = round((time.time() - t0) * 1000, 1)

            metrics = _count_labels(results)
            metrics["processing_time_ms"] = elapsed_ms
            mlflow.log_metrics(metrics)

            run_ids[model_name] = run.info.run_id
            if model_name == "finbert":
                champion_results = results

    _register_champion(run_ids["finbert"])

    return {
        "run_ids": run_ids,
        "champion": "finbert",
        "results": champion_results,
    }


def _register_champion(run_id: str):
    client = mlflow.tracking.MlflowClient()
    try:
        client.create_registered_model(CHAMPION_MODEL)
    except mlflow.exceptions.MlflowException:
        pass

    model_uri = f"runs:/{run_id}/model"
    try:
        mv = client.create_model_version(
            name=CHAMPION_MODEL,
            source=model_uri,
            run_id=run_id,
        )
        client.set_model_version_tag(mv.name, mv.version, "champion", "true")
    except Exception:
        pass
