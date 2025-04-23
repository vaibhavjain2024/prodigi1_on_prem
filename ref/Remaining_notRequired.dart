        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/machines",
            "lambdaName": "msil-iot-psm-get-machines",
            "methodType":["GET"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/part/input",
            "lambdaName": "msil-iot-psm-get-input-material",
            "methodType":["GET"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "routeName" : "pressShop/data-check",
            "lambdaName": "msil-iot-psm-data-check-by-shop-id",
            "methodType":["GET"]
        },