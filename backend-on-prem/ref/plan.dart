        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan/filters",
            "lambdaName": "msil-iot-psm-get-plan-filters",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan",
            "lambdaName": "msil-iot-psm-get-plan",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/alerts",
            "lambdaName": "msil-iot-psm-get-alerts",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan/download",
            "lambdaName": "msil-iot-psm-get-psm-signed-url-to-download-plan-file",
            "methodType":["GET"]
        } --> Open,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan/upload",
            "lambdaName": "msil-iot-psm-get-psm-signed-url-to-upload-plan-file",
            "methodType":["GET"]
        } --> Open,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan/report",
            "lambdaName": "msil-iot-psm-get-plan-report",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/plan/status",
            "lambdaName": "msil-iot-psm-get-file-status",
            "methodType":["GET"]
        } -> Done