import boto3
import io
from PIL import Image, ImageDraw, ImageFont

labelSearchNumber = 10

rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_ACCESS_KEY')

with open('./YOUR_IMAGE.jpg', 'rb') as processed_image:
    image_bytes = processed_image.read()
    response = rekognition_client.detect_labels(
        Image={
            'Bytes': image_bytes
        },
        MaxLabels=labelSearchNumber,
        MinConfidence=80)
    image = Image.open(io.BytesIO(image_bytes))
    font = ImageFont.truetype('Keyboard.ttf', 40)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    print(f'Top {labelSearchNumber} labels in the image:')
    for label in response['Labels']:
        name = label['Name']
        confidence = label['Confidence']
        print(f">> '{name}' ({confidence:.2f}% confidence)")
        if(label['Instances']):
            print(f'Specifying location for {label["Name"]}')
        for instance in label['Instances']:
            bounding_box = instance['BoundingBox']
            x0 = int(bounding_box['Left'] * width) 
            y0 = int(bounding_box['Top'] * height)
            x1 = x0 + int(bounding_box['Width'] * width)
            y1 = y0 + int(bounding_box['Height'] * height)
            draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=10)
            draw.text((x1, y0), name, font=font, fill=(255, 0, 0))
    
    image.save('labeled_output.png')