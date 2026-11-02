import base64, io, json, boto3
from PIL import Image

def load_image_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Prepare request
inference_params = {
    "taskType": "VIRTUAL_TRY_ON",
    "virtualTryOnParams": {
        "sourceImage": load_image_as_base64("backend/src/services/person.png"),   # the person photo
        "referenceImage": load_image_as_base64("backend/src/services/hoodie2.png"),# the garment photo
        "maskType": "GARMENT",                               # focus area
        "garmentBasedMask": {"garmentClass": "UPPER_BODY"}   # or LOWER_BODY / FULL_BODY
    }
}

# Create Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Invoke model
response = bedrock.invoke_model(
    body=json.dumps(inference_params),
    modelId="amazon.nova-canvas-v1:0",
    accept="application/json",
    contentType="application/json"
)

# Parse and save the resulting image
response_json = json.loads(response["body"].read())
for i, image_base64 in enumerate(response_json.get("images", [])):
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes))
    image.save(f"output_{i}.png")
    print(f"Saved: output_{i}.png")
