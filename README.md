# aws-periodic-table

TO BUILD:
```
cd periodic
pip install -r requirements.txt -t .

cd ..
./build <region> <lambda-bucket> <stack-name> <bucket> <key>
```  
where:
```
  region - is the AWS region you'll deply this stack to
  lambda-bucket - is use as a staging area for the lambda function
  stack-name - is the name you'd like to use for the cloudformation stack
  bucket - which S3 bucket would you like to copy the resulting HTML file to
  key - the name for the resulting HTML file (the S3 key)
```  
