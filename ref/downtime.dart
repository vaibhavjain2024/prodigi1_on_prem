        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime/filters",
            "lambdaName": "msil-iot-psm-get-downtime-filters",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime",
            "lambdaName": "msil-iot-psm-get-downtime",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime/report",
            "lambdaName": "msil-iot-psm-get-downtime-report",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime/totalduration",
            "lambdaName": "msil-iot-psm-get-total-downtime",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime/remark/list",
            "lambdaName": "msil-iot-psm-downtime-remark-list",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/downtime/remark/update",
            "lambdaName": "msil-iot-psm-downtime-remark-update",
            "methodType":["PUT"]
        } -> Done