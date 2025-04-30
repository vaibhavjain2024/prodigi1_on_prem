        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/master/upload",
            "lambdaName": "msil-iot-psm-master-file-upload",
            "methodType":["POST"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/master/details",
            "lambdaName": "msil-iot-psm-master-file-details",
            "methodType":["GET"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/master/upload/details-save",
            "lambdaName": "msil-iot-psm-master-file-details-save",
            "methodType":["POST"]
        },
        {
            "httpApiGatewayName": "msil-iot-pressshop-apis",
            "httpAuthorizerName":"pressShopCognitoAuthorizer",
            "routeName" : "pressShop/master/download",
            "lambdaName": "msil-iot-psm-get-psm-signed-url-to-download-master-file",
            "methodType":["GET"]
        }