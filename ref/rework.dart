        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework",
            "lambdaName": "msil-iot-psm-get-quality-updation",
            "methodType":["GET"]
        } -> Done,
        ,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework/report",
            "lambdaName": "msil-iot-psm-get-quality-updation-report",
            "methodType":["GET"]
        } -> Done,
        ,        
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework/updation",
            "lambdaName": "msil-iot-psm-quality-updation-records-update",
            "methodType":["PUT"]
        } -> Done,        
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework/submit",
            "lambdaName": "msil-iot-psm-quality-updation-submission",
            "methodType":["POST"]
        } -> Done,        
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework/total",
            "lambdaName": "msil-iot-psm-quality-updation-total-rework-qty",
            "methodType":["GET"]
        } -> Done,
        ,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/rework/records",
            "lambdaName": "msil-iot-psm-get-quality-updation-records",
            "methodType":["GET"]
        } -> Done
        