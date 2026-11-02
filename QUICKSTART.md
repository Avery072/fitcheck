# FitCheck - Quick Start Guide

Get your virtual try-on app running in 5 minutes!

## Prerequisites

- Node.js 14+ installed
- A web browser
- An email address (for account creation)

## Installation

1. **Navigate to the frontend directory**:
```bash
cd frontend
```

2. **Install dependencies** (first time only):
```bash
npm install
```

3. **Start the app**:
```bash
npm start
```

4. **Open your browser**:
- The app will automatically open at http://localhost:3000
- If not, manually navigate to http://localhost:3000

## Using the App

### Step 1: Create an Account

1. Click **"Create Account"** on the sign-in screen
2. Enter your email address
3. Create a password with:
   - At least 8 characters
   - 1 uppercase letter
   - 1 lowercase letter
   - 1 number
   - 1 special character
4. Check your email for verification code (if required)

### Step 2: Upload Your Photo

1. After signing in, click **"Choose Photo"**
2. Select a full-body photo from your computer
   - Must be under 5MB
   - PNG, JPG, or GIF format
   - Show your full body for best results
3. Wait for upload confirmation

### Step 3: Try On Clothes

**Option A: Use Example Items** (Fastest!)

1. Browse the example clothing items displayed
2. Click **"Add"** on any items you like
3. Add 1-5 items to your try-on queue

**Option B: Add Your Own Items**

1. Find clothing images online
2. Copy the image URL
3. Fill in the form:
   - **Title**: "Blue Nike Hoodie"
   - **Image URL**: https://static.nike.com/.../image.png
   - **Category**: Select from dropdown (hoodie, pants, etc.)
   - **Retailer**: "Nike" (optional)
4. Click **"Add Custom Item"**

### Step 4: Generate Virtual Try-On

1. Review your selected items
2. Click **"Start Virtual Try-On"**
3. Wait while processing (~10-15 seconds per item)
4. View your results!

## Example Workflow

```
1. Sign up → 2. Upload photo → 3. Add Nike Hoodie → 4. Add Joggers → 5. Start Try-On → 6. View Results!
```

## Tips for Best Results

### Photo Guidelines
- **Lighting**: Good, even lighting (avoid shadows)
- **Background**: Plain, solid color background works best
- **Pose**: Stand straight, arms slightly away from body
- **Clothing**: Wear form-fitting clothes (easier for AI to process)
- **Distance**: Full body visible, head to toe
- **Quality**: High resolution (but under 5MB)

### Clothing Image Guidelines
- Use product photos with transparent or white backgrounds
- Flat lay photos work well
- Avoid photos with models (just the clothing)
- Higher resolution = better results

## Processing Times

| Number of Items | Estimated Time |
|----------------|----------------|
| 1 item | ~12 seconds |
| 2 items | ~24 seconds |
| 3 items | ~36 seconds |
| 5 items | ~60 seconds |

## Troubleshooting

### "Upload failed"
- Check file size (must be < 5MB)
- Try a different image format (PNG works best)
- Ensure stable internet connection

### "Try-on failed"
- Make sure you uploaded your photo first
- Check that clothing image URLs are accessible
- Try with fewer items (start with 1-2)

### Example items not loading
- These use real product URLs that may change
- Use "Add Custom Item" with your own URLs instead

### Can't create account
- Password must meet all requirements
- Use a valid email address
- Check spam folder for verification email

## What's Happening Behind the Scenes?

1. **Upload**: Your photo is securely uploaded to AWS S3
2. **Authentication**: AWS Cognito manages your account
3. **Processing**: AWS Bedrock Nova Canvas AI generates try-on images
4. **Sequential Processing**: Items are processed one at a time
5. **Results**: Each step shows you wearing the previous items + new item

## Getting Image URLs

### Method 1: Right-click on product images
1. Go to any clothing website (Nike, Adidas, etc.)
2. Find a product you like
3. Right-click the product image
4. Select "Copy Image Address" or "Copy Image Link"
5. Paste into the app

### Method 2: Use direct links
Examples:
- Nike: `https://static.nike.com/a/images/...`
- Adidas: `https://assets.adidas.com/images/...`
- Uniqlo: `https://image.uniqlo.com/...`

## AWS Resources Being Used

- **API**: https://0vjz7ay0cc.execute-api.us-west-2.amazonaws.com/dev
- **Authentication**: AWS Cognito (us-west-2_CULDONpiY)
- **Storage**: S3 bucket (fitcheck-user-assets-dev-939111384927)
- **Database**: DynamoDB (fitcheck-data-dev)
- **AI**: AWS Bedrock Nova Canvas

## Need Help?

Check the full documentation:
- Frontend: [frontend/FITCHECK_README.md](frontend/FITCHECK_README.md)
- Backend API: [README.md](README.md)

## Next Steps

After getting familiar with the app:
1. Try different combinations of clothing
2. Upload multiple body photos
3. Experiment with different categories
4. Share your results!

## Example URLs to Test

### Hoodies
```
https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/b1bcbca4-e853-4df7-b329-5be3c61ee057/sportswear-club-fleece-pullover-hoodie-lmhXM7.png
```

### Pants
```
https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/b1bcbca4-e853-4df7-b329-5be3c61ee057/sportswear-tech-fleece-joggers-lmhXM7.png
```

Just copy and paste these into the "Image URL" field!

---

**Ready to get started? Run `npm start` and have fun!**
