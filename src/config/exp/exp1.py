config = {
    "features": {
        "target": ["survived"],
        "train": ["fare", "sib_sp", "family_size", "pclass"],
    },
    "kfold_config_name": "basic",
    "metrics": "accuracy_score",
    "model": {
        "name": "LGBMClassifier",
        "params": {
            "boosting_type": "gbdt",
            "objective": "binary",
            "metric": "binary_logloss",
            "learning_rate": 0.3,
            "max_depth": 25,
            "min_child_weight": 5,
            "num_leaves": 250,
            "min_child_samples": 65,
            "verbose": -1,
        },
        "fit_params": {"eval_metric": "l2"},
    },
}
