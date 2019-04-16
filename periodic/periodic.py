# coding=utf-8
import os, re, json, boto3, pystache

from bs4 import BeautifulSoup
from requests import get

bucket = os.environ['bucket']
key = os.environ['key']

s3 = boto3.client('s3')

# Reserve keywords for special cases, including single and 3-letter symbols
reserved_symbols = {
  "Mx"  : "Apache MXNet on AWS", 
  "Tf"  : "TensorFlow on AWS", 
  "Eks" : "Elastic Container Service for Kubernetes", 
  "Ecs" : "Elastic Container Service", 
  "Db"  : "DocumentDB", 
  "53"  : "Route 53", 
  "X"   : "X-Ray", 
  "Ami" : "Deep Learning AMIs", 
  "Phd" : "Personal Health Dashboard", 
  "Cs"  : "CloudSearch", 
  "L"   : "Lambda", 
  "S3"  : "Simple Storage Service", 
  "A"   : "Athena", 
  "Vpc" : "VPC", 
  "Ec2" : "EC2", 
  "C9"  : "Cloud9", 
  "Gt"  : "SageMaker Ground Truth", 
  "Sns" : "Simple Notification Service", 
  "Sqs" : "Simple Queue Service", 
  "Hsm" : "CloudHSM", 
  "Ebs" : "Elastic Block Store", 
  "Cli" : "Command Line Interface", 
  "Cf"  : "CloudFront", 
  "Cm"  : "Cloud Map", 
  "Gl"  : "S3 Glacier", 
  "Sdk" : "Tools and SDKs", 
  "Lx"  : "Lex", 
  "M"   : "Macie", 
  "K"   : "Managed Streaming for Kafka", 
  "Emr" : "EMR", 
  "F"   : "Fargate"
}

# For reverse lookup  
reserved_services = dict(map(reversed, reserved_symbols.items()))

# Some names are just to long to display, shorten them here
preferred_names = {
  "Elastic Container Service for Kubernetes": "ECS for Kubernetes", 
  "Serverless Application Repository":"Serverless App Repo" 
}

# Default colors
colors = ["#834187", "#878541", "#458741", "#874145", 
          "#c92d39", "#3ac92d", "#2d44c9", "#c9762d", 
          "#ef8d22", "#2c22ef", "#ef22e5", "#e5ef22", 
          "#fcc438", "#8d38fc", "#fc38a7", "#a7fc38", 
          "#7ab648", "#b6487a", "#b66548", "#48adb6", 
          "#3aa6dd", "#dd703a", "#ddc23a", "#a73add"]

# Parse prefix and name
def parse_name(name):

    search = re.search( "(AWS|Amazon)*\s*(.*)", name )
    prefix = search.group(1) or 'AWS'
    name = search.group(2)
    name = name.split("(",2)[0].strip()

    return prefix, name

# Create a symbol, roughly:
# 1. Use a pre-defined symbol
# 2. Create a 2 letter symbol using first letters of words in name
# 3. Create a 2 letter symbol using random letters, preferably stating with the first letter of the name
def create_symbol(symbols, name):
  
    symbol = ""
    if name in reserved_services:
      # We have a specific symbol to use for this service
      symbol = reserved_services[name]
      symbols[symbol] = name
    else:
      cleaned = re.sub(r"[&,-/.]",'',name)
      words = cleaned.split(' ')
      words = [ elem for elem in words if not elem.islower() ]

      chars = [ word[0:1] for word in words ]
      chars = "".join(chars + [ word[1:] for word in words ])

      for first in chars:
        first = first.upper()

        for char in chars[1:]:
          candidate = first + char.lower()
          if not candidate in symbols:
            symbols[candidate] = name
            reserved_services[name] = candidate
            symbol = candidate
            break

        if symbol: break

    if not symbol:
      print("Couldn't generate symbol for %s: %s" % (name, chars))

    return symbol
    
title = "Periodic Table of Amazon Web Services"
description = "Periodic Table of Amazon Web Services"

def lambda_handler(event, context):

  periodic = {'categories':[], 'title':title, 'description':description}
  
  # Symbols already used
  symbols = {}
  
  # Services already processed
  names = {}
  

  raw = get('https://aws.amazon.com/products/')
  soup = BeautifulSoup(raw.content, 'html.parser')
  
  ccount = 0
  
  # Scrape the producs page
  for catitem in soup.select("div.lb-item-wrapper"):
    cname = catitem.find("a").find("span", recursive=False).text.strip()
    cclass = re.sub(r"[&, ]",'',cname)
    category = {"name": cname, "services":[], "color": colors[ccount], "class":cclass}
    ccount = ccount + 1
  
    catservices = catitem.findAll("div", { "class" : "lb-content-item" })
    for catservice in catservices:
      name = catservice.find("a").find(text=True, recursive=False).strip()
      # Ignore duplicates on the page
      if name in names:
        continue
      names[name] = 1
      
      desc = catservice.find("a").find("span", recursive=False).text.strip()
      link = "https://aws.amazon.com" + catservice.find('a').attrs['href'].split("?")[0].strip()
      
      prefix, name = parse_name(name)
      symbol = create_symbol(symbols, name)
      
      # Shorter names for some services
      if name in preferred_names: name = preferred_names[name]
      
      category["services"].append({"name": name, "desc": desc, "link": link, "prefix": prefix, "symbol": symbol, "category": cclass, "long":len(name)>11, "reallong":len(name)>20})
  
    periodic['categories'].append(category)
  
    
  # Vertical order for topmost rows
  vlayout = [
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ]
  vlayout  = zip(*vlayout) # transpose for easier handling
  
  # Horizontal layout for bottom 3+ rows
  hlayout = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
  ]
  
  indices = []
  hrow = 1
  for row in range(0,len(vlayout)):
    for col in range(0, len(vlayout[row])):
      if vlayout[row][col]:
        indices.append([hrow+col+1, row+1])
        
  hrow = col + 2
  for row in range(0,len(hlayout)):
    for col in range(0, len(hlayout[row])):
      if hlayout[row][col]:
        indices.append([hrow+row+1, col+1])
  
  count = 0
  for category in periodic['categories']:
    for service in category["services"]:
      service['row'] = indices[count][0]
      service['column'] = indices[count][1]
      count = count + 1
  
  with open('template.mustache', 'r') as f:  
    template = f.read()
    html = pystache.render(template, periodic)
    
    response = s3.put_object(
      ACL='public-read',
      ContentType='text/html',
      Body=html,
      Bucket=bucket,
      Key=key)
