import pyrebase
import requests
from src.constants import FIREBASE_CONFIG
from google_auth_oauthlib.flow import InstalledAppFlow

class FirebaseManager:
    """Handles authentication and cloud session storage via Pyrebase4 & REST."""
    
    def __init__(self):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        self.current_user = None

    def login(self, email, password):
        """Authenticates a user with email and password."""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.current_user = user
            # Pyrebase doesn't always attach the email automatically, so we force it
            if "email" not in self.current_user:
                self.current_user["email"] = email
            return True, "Login successful."
        except Exception as e:
            return False, f"Login failed: {e}"

    def register(self, email, password):
        """Creates a new user with email and password."""
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.current_user = user
            if "email" not in self.current_user:
                self.current_user["email"] = email
            return True, "Registration successful."
        except Exception as e:
            return False, f"Registration failed: {e}"

    def login_with_google(self):
        """Authenticates via Google OAuth and trades the token with Firebase."""
        scopes = [
            'openid', 
            'https://www.googleapis.com/auth/userinfo.email', 
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', scopes)
            credentials = flow.run_local_server(port=0)
            google_id_token = credentials.id_token
            
            if not google_id_token:
                return False, "Failed to retrieve Google ID token."

            api_key = FIREBASE_CONFIG.get("apiKey")
            if not api_key:
                return False, "Missing apiKey in FIREBASE_CONFIG."
            
            endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={api_key}"
            payload = {
                "postBody": f"id_token={google_id_token}&providerId=google.com",
                "requestUri": "http://localhost",
                "returnSecureToken": True 
            }
            
            response = requests.post(endpoint, json=payload)
            
            if not response.ok:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown Firebase Error")
                return False, f"Firebase Auth Error: {error_msg}"
            
            data = response.json()
            self.current_user = {
                "idToken": data.get("idToken"),
                "localId": data.get("localId"),
                "email": data.get("email", ""),
                "refreshToken": data.get("refreshToken")
            }
            
            return True, "Google Login successful."
            
        except FileNotFoundError:
            return False, "Configuration Error: 'client_secrets.json' missing."
        except Exception as e:
            return False, f"Google login failed: {str(e)}"

    # =========================================================================
    # DATABASE METHODS (Syncing history to the cloud)
    # =========================================================================

    def save_chat_history(self, session_id, title, items):
        """Saves a shopping trip to Firebase Realtime Database."""
        if not self.current_user:
            print("⚠️ Cannot save: No user is currently logged in.")
            return

        try:
            # 1. Sanitize the email (CRITICAL: Firebase blocks '.' in keys)
            raw_email = self.current_user.get("email", "guest@smartmart.ai")
            safe_email = raw_email.replace(".", "_")
            
            # 2. Prepare the data payload
            data = {
                "title": title,
                "items": items
            }
            
            # 3. Get the auth token (required by Pyrebase for secure writes)
            token = self.current_user.get("idToken")
            
            # 4. Write to database: /users/email_without_dots/chats/session_id
            self.db.child("users").child(safe_email).child("chats").child(session_id).set(data, token)
            print(f"✅ SUCCESS: Saved session '{title}' to Firebase!")

        except Exception as e:
            print(f"\n❌ FIREBASE SAVE ERROR: {e}\n")

    def get_all_chats(self):
        """Fetches all past shopping trips for the current user."""
        if not self.current_user:
            return {}

        try:
            safe_email = self.current_user.get("email", "guest@smartmart.ai").replace(".", "_")
            token = self.current_user.get("idToken")
            
            # Fetch data from the user's specific node
            chats = self.db.child("users").child(safe_email).child("chats").get(token)
            
            if chats.val():
                print(f"✅ SUCCESS: Loaded {len(chats.val())} past trips from Firebase.")
                return chats.val()
            else:
                print("ℹ️ No past trips found in Firebase for this user.")
                return {}
                
        except Exception as e:
            print(f"\n❌ FIREBASE FETCH ERROR: {e}\n")
            return {}

    def delete_chat_session(self, session_id):
        """Deletes a specific session from the cloud database."""
        if not self.current_user:
            return
            
        try:
            safe_email = self.current_user.get("email", "guest@smartmart.ai").replace(".", "_")
            token = self.current_user.get("idToken")
            
            # Remove the specific session node
            self.db.child("users").child(safe_email).child("chats").child(session_id).remove(token)
            print(f"✅ SUCCESS: Deleted session '{session_id}' from Firebase.")
            
        except Exception as e:
            print(f"\n❌ FIREBASE DELETE ERROR: {e}\n")