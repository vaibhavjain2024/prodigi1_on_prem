        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view",
            "lambdaName": "msil-iot-psm-get-shop-view",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/report",
            "lambdaName": "msil-iot-psm-get-shop-view-report",
            "methodType":["GET"]
        } -> Done ,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/graph",
            "lambdaName": "msil-iot-psm-get-shop-view-graph",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/uniquecounts",
            "lambdaName": "msil-iot-psm-unique-parts-count",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/topbreakdown",
            "lambdaName": "msil-iot-psm-top-downtime-reasons",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/machine",
            "lambdaName": "msil-iot-psm-get-machine-view",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/shop-view/machine-trend",
            "lambdaName": "msil-iot-psm-get-machine-trend-graph",
            "methodType":["GET"]
        } -> Done
