        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/filters",
            "lambdaName": "msil-iot-psm-get-quality-punching-filters",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality",
            "lambdaName": "msil-iot-psm-get-quality-punching",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/report",
            "lambdaName": "msil-iot-psm-get-quality-punching-report",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/reasons",
            "lambdaName": "msil-iot-psm-quality-reason-list",
            "methodType":["GET"]
        } -> Done,       
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/punching",
            "lambdaName": "msil-iot-psm-quality-punching-records-update",
            "methodType":["PUT"]
        } -> Done,        
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/submit",
            "lambdaName": "msil-iot-psm-quality-punching-submission",
            "methodType":["POST"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/quality/records",
            "lambdaName": "msil-iot-psm-get-quality-punching-records",
            "methodType":["GET"]
        } -> Done