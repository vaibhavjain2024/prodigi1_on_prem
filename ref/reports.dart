        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/filters",
            "lambdaName": "msil-iot-psm-get-report-filters",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/downtime",
            "lambdaName": "msil-iot-psm-get-reports-downtime",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/quality",
            "lambdaName": "msil-iot-psm-get-reports-quality",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/production",
            "lambdaName": "msil-iot-psm-get-reports-production",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/downtime/report",
            "lambdaName": "msil-iot-psm-get-reports-downtime-report",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/quality/report",
            "lambdaName": "msil-iot-psm-get-reports-quality-report",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/reports/production/report",
            "lambdaName": "msil-iot-psm-get-reports-production-report",
            "methodType":["GET"]
        } -> Done