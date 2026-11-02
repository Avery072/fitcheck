# FitCheck

**See it on you before you buy it.** FitCheck is a virtual try-on web app built at DubHacks. Upload one full-body photo, pick a few clothing items (from the built-in examples or any product image URL), and FitCheck uses **Amazon Bedrock Nova Canvas** to generate images of you wearing each one.

- React 19 frontend with Cognito sign-up / sign-in (AWS Amplify UI)
- Serverless Python backend on AWS Lambda + API Gateway, defined with AWS SAM
- Photos stored privately in S3 and accessed through presigned URLs
- Try-on sessions tracked in DynamoDB, with live progress in the UI

---

## How it works

```
 Browser (React)                                AWS (us-west-2)
 ───────────────                                ─────────────────────────────────────────
 1. Sign in  ─────────────────────────────────▶ Cognito User Pool  (returns JWT)
 2. GET /upload-url ──────────────────────────▶ Lambda ─▶ presigned S3 PUT URL
 3. PUT photo directly ───────────────────────▶ S3  (private, per-user prefix)
 4. POST /multi-fit {items, body_asset_key} ──▶ Lambda (5 min timeout)
                                                  ├─ fetch each garment image from its URL
                                                  ├─ Bedrock Nova Canvas VIRTUAL_TRY_ON (us-east-1)
                                                  ├─ save result image to S3
                                                  └─ update session progress in DynamoDB
 5. GET /multi-fit?session_id=… (every 3 s) ──▶ Lambda ─▶ status + presigned result URLs
```

Each clothing item is tried on against your original photo, producing one result image per item. The garment's category picks the Nova Canvas mask: pants/jeans/shorts → `LOWER_BODY`, dresses/jumpsuits → `FULL_BODY`, everything else → `UPPER_BODY`.

---

## Quick start (run the app locally)

The dev backend is already deployed, and [frontend/src/config.js](frontend/src/config.js) points at it, so you only need to run the frontend.

**Prerequisites:** Node.js 18+ and npm.

```bash
cd frontend
npm install
npm start
```

The app opens at **http://localhost:3000**. Then:

1. **Create an account.** Use your email and a password with at least 8 characters, including an uppercase letter, a lowercase letter, a number and a symbol. Enter the verification code sent to your email.
2. **Upload a photo.** A full-body shot, under 5 MB (PNG/JPG). Plain backgrounds and even lighting work best.
3. **Add items.** Click **Add** on an example item, or paste any clothing image URL with a title and category.
4. **Start Virtual Try-On.** Expect about 10–15 seconds per item. Results appear as each item finishes.

There's a longer walkthrough with photo tips and troubleshooting in [QUICKSTART.md](QUICKSTART.md).

---

## Deploying your own backend

Only needed if you want your own AWS stack instead of the shared dev one.

**Prerequisites**
- An AWS account, with the [AWS CLI](https://aws.amazon.com/cli/) configured (`aws configure`)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Python 3.9
- **Bedrock model access to Amazon Nova Canvas in `us-east-1`**, enabled in the Bedrock console under *Model access*. The stack lives in `us-west-2`, but the try-on code calls Bedrock in `us-east-1`.

**Deploy**

```bash
cd backend
sam build
sam deploy                      # dev stack: fitcheck-dev  (us-west-2)
# or
sam deploy --config-env prod    # prod stack: fitcheck-prod
```

`sam deploy` asks you to confirm the changeset. When it finishes, it prints the stack outputs: `ApiEndpoint`, `UserPoolId`, `UserPoolClientId`, `BucketName` and `TableName`.

**Point the frontend at your stack** by updating [frontend/src/config.js](frontend/src/config.js) with those outputs:

```js
export const awsConfig = {
  Auth: { Cognito: { userPoolId: '<UserPoolId>', userPoolClientId: '<UserPoolClientId>' } }
};

export const apiConfig = {
  endpoint: '<ApiEndpoint>',
  bucket: '<BucketName>',
  region: 'us-west-2'
};
```

**Useful commands**

```bash
sam local start-api                       # run the API locally (needs Docker)
sam logs -n MultiFitFunction --tail       # stream try-on Lambda logs
```

**Testing Bedrock directly:** [backend/src/services/test.py](backend/src/services/test.py) sends a single Nova Canvas try-on request using the sample `person.png` and `hoodie2.png`. Run it from the repo root with `python3 backend/src/services/test.py`. See [backend/src/services/README_TEST.md](backend/src/services/README_TEST.md).

---

## API reference

Base URL (dev): `https://0vjz7ay0cc.execute-api.us-west-2.amazonaws.com/dev`

Every endpoint except `/token` needs a Cognito ID token in the header: `Authorization: Bearer <idToken>`.

| Endpoint | Method | Description |
|---|---|---|
| `/upload-url` | GET | Presigned S3 upload URL. Query: `type` (e.g. `body`), `extension` |
| `/user-assets` | GET | List the user's uploaded photos |
| `/multi-fit` | POST | Start a try-on session. Body: `{ items: [{ title, imageUrl, category, retailer }], body_asset_key, session_id? }` |
| `/multi-fit` | GET | Session status and results. Query: `session_id` |
| `/fit` | POST | Single-item try-on |
| `/fit/{fitId}` | GET | Fetch one single-item try-on result |
| `/fits` | GET | List past try-ons |
| `/profile` | GET / POST | Read or update the user's profile |
| `/cart` | GET / POST / DELETE | Shopping cart operations |
| `/token` | POST | Exchange a Cognito OAuth code for tokens (no auth needed) |

---

## Project structure

```
dubhacks-fitcheck2/
├── QUICKSTART.md              # step-by-step user guide
├── backend/                   # AWS SAM serverless backend (Python 3.9)
│   ├── template.yaml          # Cognito, API Gateway, Lambdas, DynamoDB, S3
│   ├── samconfig.toml         # dev / prod deploy settings
│   └── src/
│       ├── handlers/          # one Lambda handler per endpoint
│       ├── services/          # Nova Canvas try-on logic + Bedrock test script
│       └── utils/             # S3, DynamoDB and HTTP response helpers
└── frontend/                  # React app (Create React App)
    └── src/
        ├── App.js             # Auth → UploadPhoto → VirtualTryOn
        ├── components/        # Auth, UploadPhoto, VirtualTryOn
        ├── data/exampleItems.js
        ├── services/api.js    # Axios client; attaches the Cognito token
        └── config.js          # AWS resource IDs and API endpoint
```

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React 19, AWS Amplify v6, `@aws-amplify/ui-react`, Axios |
| Backend | Python 3.9, AWS Lambda, API Gateway, AWS SAM, boto3, Pillow |
| Auth | Amazon Cognito (email sign-up, JWT authorizer) |
| Data | Amazon S3 (private bucket, presigned URLs), DynamoDB (on-demand, TTL) |
| AI | Amazon Bedrock: Nova Canvas (`amazon.nova-canvas-v1:0`), virtual try-on task |

## Notes and limitations

- Garment images are downloaded by the Lambda from the URL you give it, so they must be publicly reachable. Some retailer CDNs block hotlinking.
- The frontend polls every 3 seconds and gives up after 5 minutes, which matches the try-on Lambda's 5-minute timeout. Keep sessions to about 5 items or fewer.
- Best results come from product shots on plain or transparent backgrounds, not photos of models wearing the item.
- Uploaded photos and results are stored under per-user S3 prefixes and never made public.

## License

MIT
