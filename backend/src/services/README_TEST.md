# How to Test Bedrock Virtual Try-On

## Quick Start

1. **Get test images** (person + garment photos)
2. **Run test.py**
3. **See the result!**

---

## Step 1: Add Test Images

You need two images in this directory (`backend/src/services/`):

### Option A: Use Your Own Photos

- Add a person photo: `person.jpg` or `person.png`
- Add a garment photo: `hoodie.jpg` or `garment.jpg`

### Option B: Download Test Images

```bash
cd /Users/renpeicai/Downloads/dubhacks-fitcheck/backend/src/services

# Download test person image
curl -o person.jpg https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400

# Download test hoodie image
curl -o hoodie.jpg https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400
```

---

## Step 2: Run the Test

```bash
cd /Users/renpeicai/Downloads/dubhacks-fitcheck/backend/src/services
python3 test.py
```

**What it does:**
1. Loads your person and garment images
2. Converts them to base64
3. Calls Bedrock Nova Canvas
4. Saves the result to `bedrock_output_0.png`

---

## Step 3: Check the Result

The output will be saved to:
```
/Users/renpeicai/Downloads/dubhacks-fitcheck/bedrock_output_0.png
```

Open it - you should see the person wearing the garment!

---

## Expected Output

```
🔍 Testing Bedrock Nova Canvas Virtual Try-On...
------------------------------------------------------------
✅ Person image: person.jpg
✅ Garment image: hoodie.jpg

📷 Loading images...
✅ Person image loaded (534234 chars)
✅ Garment image loaded (423122 chars)

🔧 Preparing Bedrock request...
✅ Request prepared
   - Task: VIRTUAL_TRY_ON
   - Garment Class: UPPER_BODY

🔌 Connecting to Bedrock (us-east-1)...
✅ Bedrock client created

🚀 Invoking Bedrock Nova Canvas...
   (This may take 10-30 seconds...)

✅ Bedrock responded!

📦 Parsing response...
✅ Received 1 image(s)

💾 Saving output images...
✅ Saved: /Users/renpeicai/Downloads/dubhacks-fitcheck/bedrock_output_0.png
   Size: (1024, 1024)

============================================================
🎉 SUCCESS! Bedrock virtual try-on completed!
============================================================

Check the output images in:
  /Users/renpeicai/Downloads/dubhacks-fitcheck/bedrock_output_0.png

You should see the person wearing the garment!
```

---

## Troubleshooting

### Error: "Person image not found"

**Solution:** Add a person photo with one of these names:
- `person.png`
- `person.jpg`
- `body.png`

### Error: "Garment image not found"

**Solution:** Add a garment photo with one of these names:
- `hoodie.jpg`
- `garment.jpg`
- `shirt.jpg`

### Error: "AccessDeniedException"

**Solution:** Enable Bedrock access:
1. Go to AWS Console → Bedrock (us-east-1)
2. Click "Model access"
3. Request access to "Amazon Nova Canvas"
4. Wait for approval (usually instant)

### Error: "NoCredentialsError"

**Solution:** Configure AWS credentials:
```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`

---

## File Structure

```
backend/src/services/
├── test.py           ← Run this!
├── person.jpg        ← Add this (your test person photo)
├── hoodie.jpg        ← Add this (your test garment photo)
└── compositor.py     ← The actual implementation
```

---

## Tips

**Use clear photos:**
- Person: Full body, standing straight, plain background
- Garment: Product photo on white background, no model

**Adjust garment class:**
Edit test.py line 96 to change garment type:
```python
"garmentClass": "UPPER_BODY"  # or LOWER_BODY, FULL_BODY
```

**Try multiple garments:**
Run the test multiple times with different garment images!

---

**Ready to test? Add your images and run `python3 test.py`!** 🚀
