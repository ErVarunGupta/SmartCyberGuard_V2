def predict_system_state(model, features_df):
    if features_df is None or features_df.empty:
        return 0, False  # Normal, ML not used

    cpu = features_df["cpu_usage"].iloc[0]
    ram = features_df["ram_usage"].iloc[0]
    disk = features_df["disk_usage"].iloc[0]

    # Rule fallback
    if cpu > 85 and ram > 90:
        return 2, False
    if cpu > 70 or ram > 80:
        return 1, False

    if model is None:
        return 0, False

    try:
        pred = model.predict(features_df)[0]
        return pred, True
    except Exception:
        return 0, False
