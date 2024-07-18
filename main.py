import uvicorn
from os import getenv


# Import the `configure_azure_monitor()` function from the
# `azure.monitor.opentelemetry` package.
# from azure.monitor.opentelemetry import configure_azure_monitor

# # Configure OpenTelemetry to use Azure Monitor with the specified connection string.
# configure_azure_monitor(
#     connection_string="InstrumentationKey=ca212634-1a9d-4b66-a349-6799470048af;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/",
# )

if __name__ == "__main__":
    port = int(getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True, proxy_headers=True, forwarded_allow_ips="*", log_level="info")
