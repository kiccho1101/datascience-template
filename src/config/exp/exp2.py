config = {
    "features": {
        "target": ["visitors"],
        "train": [
            "te_dow_mean",
            "is_holiday",
            "yesterday_is_holiday",
            "te_air_id_dow_mean",
        ],
    },
    "kfold_config_name": "basic",
    "metrics": "RMSLE",
    "model": {
        "name": "LGBMRegressor",
        "params": {
            "boosting_type": "gbdt",
            "learning_rate": 0.1,
            "max_depth": 10,
            "min_child_weight": 5,
            "n_estimators": 100,
            "num_leaves": 15,
            "min_child_samples": 65,
            "verbose": -1,
        },
        "fit_params": {"eval_metric": "l2"},
    },
}
