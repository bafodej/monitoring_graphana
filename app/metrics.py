from prometheus_client import Gauge

# ============================
#      Custom Prometheus Metrics
# ============================

# Indique si la ventilation doit être activée :
# 1 = Good (pas besoin de ventilation)
# 0 = Moderate/Poor (ventilation activée)
ventilation_metric = Gauge(
    "ventilation_required",
    "Indique si la ventilation doit être activée (1=Good, 0=Moderate/Poor)"
)
