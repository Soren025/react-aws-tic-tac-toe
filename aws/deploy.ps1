sam build --debug
sam deploy --profile codari --s3-bucket codari-cloudformation --s3-prefix React_Tic_Tac_Toe --stack-name react-tic-tac-toe --capabilities CAPABILITY_NAMED_IAM

Remove-Item .\.aws-sam -Recurse
