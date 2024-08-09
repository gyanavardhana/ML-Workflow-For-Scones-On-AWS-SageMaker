import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]
    
    # Download the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key, "/tmp/image.png")
    
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


import json
import base64
import boto3

runtime = boto3.client('runtime.sagemaker')
ENDPOINT = 'image-classification-2024-08-09-15-28-15-671'

def lambda_handler(event, context):

    # Parse the body of the event
    body = event["body"]

    # Decode the image data
    image = base64.b64decode(body["image_data"])
    
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,    
        Body=image,               
        ContentType='image/png'   
    )
    
    # Make a prediction:
    inferences = json.loads(response['Body'].read().decode('utf-8'))
    
    # We return the data back to the Step Function    
    body["inferences"] = inferences
    
    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }




import json


THRESHOLD = 0.70


def lambda_handler(event, context):
    
    body = json.loads(event["body"])
    
    # Grab the inferences from the body
    inferences = body.get("inferences")
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
