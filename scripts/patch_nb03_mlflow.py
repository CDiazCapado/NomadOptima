"""Parchea la celda MLflow del notebook 03 para usar URI file:// correcto en Windows."""
import json
from pathlib import Path

NB = Path("notebooks/03_train_model.ipynb")

NEW_MLFLOW = '''\
mlflow_dir = ROOT / "notebooks" / "mlruns"
mlflow_dir.mkdir(parents=True, exist_ok=True)
mlflow.set_tracking_uri(mlflow_dir.as_uri())  # file:/// correcto en Windows
mlflow.set_experiment("nomadoptima_lambdarank")

best_ndcg5 = max(evals_result["val"]["ndcg@5"])
best_ndcg3 = max(evals_result["val"]["ndcg@3"])
best_ndcg1 = max(evals_result["val"]["ndcg@1"])

with mlflow.start_run(run_name="v3_producto_escalar_175features"):
    mlflow.log_params({
        "n_usuarios":       len(profiles),
        "n_ciudades":       len(city_raw),
        "n_features":       len(FEATURE_COLS),
        "n_user_features":  len(USER_COLS),
        "n_city_features":  len(CITY_FEAT_COLS),
        "label_method":     "producto_escalar_directo",
        "num_leaves":       params["num_leaves"],
        "learning_rate":    params["learning_rate"],
        "feature_fraction": params["feature_fraction"],
        "best_iteration":   model.best_iteration,
    })
    mlflow.log_metrics({
        "ndcg_at_1_val": best_ndcg1,
        "ndcg_at_3_val": best_ndcg3,
        "ndcg_at_5_val": best_ndcg5,
    })
    for png in ["nb03_curvas_aprendizaje.png", "nb03_feature_importance.png", "nb03_shap_summary.png"]:
        p = DATA_DIR / png
        if p.exists():
            mlflow.log_artifact(str(p))
    # Guardar modelo como artefacto (sin model registry)
    model_tmp = ROOT / "notebooks" / "mlruns" / "lgbm_tmp.txt"
    model.save_model(str(model_tmp))
    mlflow.log_artifact(str(model_tmp))
    model_tmp.unlink(missing_ok=True)

    run_id = mlflow.active_run().info.run_id
    print(f"MLflow run_id: {run_id}")

print(f"Experimento registrado en notebooks/mlruns/")
print(f"Para ver: mlflow ui --backend-store-uri notebooks/mlruns")
'''

nb = json.load(open(NB, encoding="utf-8"))
found = False
for cell in nb["cells"]:
    src = "".join(cell["source"])
    if "mlflow.set_tracking_uri" in src and cell["cell_type"] == "code":
        cell["source"] = NEW_MLFLOW.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        found = True
        print(f"OK celda MLflow parcheada (id={cell.get('id')})")
        break

if not found:
    print("ERROR: celda MLflow no encontrada")

json.dump(nb, open(NB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
