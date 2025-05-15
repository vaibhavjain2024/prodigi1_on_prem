        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production",
            "lambdaName": "msil-iot-psm-get-production",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production",
            "lambdaName": "msil-iot-psm-quality-production-start",
            "methodType":["POST"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production/variant",
            "lambdaName": "msil-iot-psm-production-update-variant",
            "methodType":["PUT"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production/part-data",
            "lambdaName": "msil-iot-psm-get-production-part-data",
            "methodType":["GET"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production/material-update",
            "lambdaName": "msil-iot-psm-production-input-material-update",
            "methodType":["PUT"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production/quality-punch",
            "lambdaName": "msil-iot-psm-production-quality-punch",
            "methodType":["PUT"]
        } -> Done,
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/production/update",
            "lambdaName": "msil-iot-psm-production-update",
            "methodType":["PUT"]
        } -> Done
