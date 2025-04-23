        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "routeName" : "pressShop/retrieval/reports/download/initiated",
            "lambdaName": "msil-iot-psm-retrieval-db-reports-download-initiation",
            "methodType":["GET"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "routeName" : "pressShop/retrieval/reports/download/athena",
            "lambdaName": "msil-iot-psm-db-data-retrieval-report-from-athena",
            "methodType":["GET"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "routeName" : "pressShop/retrieval/reports/check/download/status",
            "lambdaName": "msil-iot-psm-retrieval-reports-download-status-check",
            "methodType":["GET"]
        }