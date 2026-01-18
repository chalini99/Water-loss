def generate_explanation(row):
    if row['Risk_Level'] == "High":
        return (
            "A sharp increase in water usage combined with reduced pressure "
            "was detected. This pattern strongly suggests a possible underground leak."
        )
    elif row['Risk_Level'] == "Medium":
        return (
            "Water usage shows moderate deviation from historical patterns. "
            "This zone should be monitored closely."
        )
    else:
        return (
            "Water usage and pressure levels are within expected limits. "
            "No immediate action is required."
        )
