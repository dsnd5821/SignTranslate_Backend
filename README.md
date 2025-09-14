# SignTranslate Backend

## Project Purpose

SignTranslate Backend provides a set of Python-based Firebase Cloud Functions that power the SignTranslate platform. These functions handle video processing with FFmpeg and support features such as:

- Linking library videos and transforming them for playback.
- Composing SLP (Sign Language Phrase) videos.
- Returning basic FFmpeg information for debugging.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd SignTranslate_Backend
   ```
2. **Install Firebase CLI** (requires Node.js)
   ```bash
   npm install -g firebase-tools
   ```
3. **Create a Python virtual environment and install dependencies**
   ```bash
   cd functions
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Environment Variables

The functions require a Firebase service account when run locally or in CI. Set the following environment variable:

- `GOOGLE_APPLICATION_CREDENTIALS` – path to a service-account JSON file with access to the target Firebase project.

When deploying from automation, you may also need:

- `FIREBASE_TOKEN` – authentication token for the Firebase CLI.
- `FIREBASE_PROJECT` – (optional) project ID if different from the default set in `firebase.json`.

## Usage Examples

After deploying, the functions will be available under your Firebase project's region (`asia-southeast1` by default). Examples:

- **Check FFmpeg availability**
  ```bash
  curl https://asia-southeast1-<project-id>.cloudfunctions.net/ffmpeg_info
  ```
- **Invoke library link handler**
  ```bash
  curl -X POST \
       -H "Content-Type: application/json" \
       -d '{"some":"payload"}' \
       https://asia-southeast1-<project-id>.cloudfunctions.net/library_link
  ```

## Firebase Deployment

1. Authenticate the Firebase CLI:
   ```bash
   firebase login
   ```
2. Deploy the functions:
   ```bash
   firebase deploy --only functions
   ```

Deployment uses the configuration in [`firebase.json`](firebase.json) and packages the code in the `functions` directory.

