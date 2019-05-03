# aws-periodic-table
Generate an HTML "Periodic Table of Amazon Web Services" by scraping service information from https://aws.amazon.com/products/. The build steps below will create a Lambda function the fires daily to regenerate the table and upload to an S3 bucket of your choice.

Uses the SNS topic created by aws-services-scraper


TO BUILD:
```
cd periodic
pip install -r requirements.txt -t .
cd ..

cd shared
pip install -r requirements.txt -t .
cd ..

./build.sh <region> <lambda-bucket> <stack-name> <bucket> <key> <topic>
```  
WHERE:
```
  region - is the AWS region you'll deploy this stack to
  lambda-bucket - is used by cloudformation as a staging area for the lambda function
  stack-name - is the name you'd like to use for the cloudformation stack
  bucket - which S3 bucket would you like to copy the resulting HTML file to
  key - the name for the resulting HTML file (the S3 key)
  topic - the SNS topic to subscribe to for service updates (see awsgeek/aws-services-scraper repo)
```  
