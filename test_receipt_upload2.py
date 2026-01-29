#!/usr/bin/env python3
"""
QuickBooks Receipt Upload Test Script (Using Python SDK)
Self-contained script to test receipt upload using the official intuitlib-python SDK.
Can be used for troubleshooting and sharing with Intuit support.

Prerequisites:
    pip install intuit-oauth python-quickbooks
"""

import json
from pathlib import Path
from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from quickbooks.objects.attachable import Attachable, AttachableRef
from quickbooks.objects.base import Ref

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# QuickBooks API Configuration
REALM_ID = "9341455122564664"  # Company ID from QuickBooks
ACCESS_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwieC5vcmciOiJIMCJ9..ybwq9ev_5J77fYR_R1ukqQ.ib-c7mbUBGRwa5Vktjf8c0QfEIuTF5fh1C8tcF4XvRlHZXIu9likBEs7Q02ewpMgGPc5l1IHZtTYVp_hDwNHV2nNvPdHMV05ShFUvbDDwSWrTsZ2dnVM1c9ACN0EiYiLqsZVL06YcNhgGII6TL_Z34fKGtjCuxHAmFkbKuVwxvlI0QBxsuIsnqAznZbjBuJy2gy8KeCqmxJCYhx5_xGMibppLW9KcF-ICV0K8Hh-xGjo4gnbg30-PHnXJzpYB8IKnwiPWhkjQNBXZ5L9rYZhM3YZAB1sOjUd5UcUzco9ySiMRG4Oa8T-nahmcusVwR3W2IUNzhpn983-TuKzudVPJdDug6rrN2aqFxI9h5YZwcfmOktw1IXQL4GvrkrJ_B6EX6Dcmyyckp2pFYm31PDcCIbIdT0aqtb6xXsGTfWtLh7N7psDaFkjeQuSm75fwpRCur1tl8wcpnSQ7rMHG3KY54MdnhGGKbnv2o37KlgmcMo.XxhX5n9lMPF6Zpuo5KVXBw"  # OAuth 2.0 Access Token
REFRESH_TOKEN = ""  # Optional: Refresh token if you have one
CLIENT_ID = ""  # Optional: Your app's client ID (for token refresh)
CLIENT_SECRET = ""  # Optional: Your app's client secret (for token refresh)

# Environment
ENVIRONMENT = "sandbox"  # "sandbox" or "production"

# Transaction to link the receipt to
ENTITY_TYPE = "Purchase"  # Can be: Purchase, Bill, Expense, Vendor, etc.
ENTITY_ID = "131"  # The ID of the transaction to attach to

# File to upload
FILE_PATH = "docs/Test 1.pdf"  # Path to the PDF file
USE_FILE_PATH = True  # True = upload from path, False = upload from bytes

# ============================================================================
# SCRIPT LOGIC - DO NOT MODIFY UNLESS NEEDED
# ============================================================================

def upload_receipt_sdk():
    """
    Upload a receipt to QuickBooks using the Python SDK.
    """
    
    print("=" * 80)
    print("QuickBooks Receipt Upload Test (Python SDK)")
    print("=" * 80)
    print()
    
    # Validate configuration
    print("1. Validating configuration...")
    if REALM_ID == "YOUR_REALM_ID_HERE" or ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("   ❌ ERROR: Please update REALM_ID and ACCESS_TOKEN in the script")
        return False
    print("   ✓ Configuration valid")
    print()
    
    # Check if file exists
    print("2. Checking file...")
    file_path = Path(FILE_PATH)
    if not file_path.exists():
        print(f"   ❌ ERROR: File not found: {FILE_PATH}")
        return False
    
    file_size = file_path.stat().st_size
    print(f"   ✓ File found: {FILE_PATH}")
    print(f"   ✓ File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    if file_size > 100 * 1024 * 1024:  # 100 MB limit
        print("   ⚠ WARNING: File is larger than 100 MB (QuickBooks limit)")
    print()
    
    # Initialize QuickBooks client
    print("3. Initializing QuickBooks SDK client...")
    try:
        # The SDK tries to refresh tokens during initialization, which we don't want
        # So we'll create a minimal client manually
        from quickbooks.client import QuickBooks as QBClient
        from intuitlib.enums import Scopes
        
        # Create a basic auth client structure
        if not CLIENT_ID or not CLIENT_SECRET:
            print("   ℹ️  No CLIENT_ID/SECRET provided - creating minimal client")
            print("   ℹ️  (Only access token will be used for authentication)")
            client_id_to_use = 'dummy_client_id'
            client_secret_to_use = 'dummy_client_secret'
        else:
            client_id_to_use = CLIENT_ID
            client_secret_to_use = CLIENT_SECRET
            print("   ✓ Using provided CLIENT_ID/SECRET")
        
        # Create a minimal auth client that won't try to refresh
        from intuitlib.client import AuthClient
        from intuitlib.enums import Scopes
        
        auth_client = AuthClient(
            client_id=client_id_to_use,
            client_secret=client_secret_to_use,
            environment=ENVIRONMENT,
            redirect_uri='http://localhost:8000'
        )
        
        # Manually set the access token on the auth client
        auth_client.access_token = ACCESS_TOKEN
        
        # Create client instance without triggering refresh
        client = object.__new__(QBClient)
        
        # Manually set required attributes
        client.company_id = REALM_ID
        client.minorversion = 65
        client.verbosity = 'none'
        client.auth_client = auth_client
        
        # Set environment/sandbox flag
        if ENVIRONMENT == "sandbox":
            client.sandbox = True
        else:
            client.sandbox = False
        
        # Set the access token directly
        client.access_token = ACCESS_TOKEN
        
        # Use the auth_client as both session_manager and session
        client.session_manager = auth_client
        client.session = auth_client  # This is what process_request checks for!
        
        print(f"   ✓ QuickBooks client initialized (manual mode)")
        print(f"   ✓ Environment: {ENVIRONMENT}")
        print(f"   ✓ Company ID: {REALM_ID}")
        print()
        
    except Exception as e:
        print(f"   ❌ ERROR initializing client: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create the Attachable object
    print("4. Creating Attachable object...")
    try:
        attachment = Attachable()
        
        # Set file name and content type
        attachment.FileName = file_path.name
        attachment.ContentType = "application/pdf"
        
        print(f"   ✓ File name: {attachment.FileName}")
        print(f"   ✓ Content type: {attachment.ContentType}")
        
        # Choose upload method
        if USE_FILE_PATH:
            print(f"   ✓ Upload method: File Path")
            attachment._FilePath = str(file_path.absolute())
            print(f"   ✓ File path: {attachment._FilePath}")
        else:
            print(f"   ✓ Upload method: Bytes in Memory")
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            attachment._FileBytes = file_bytes
            print(f"   ✓ Loaded {len(file_bytes):,} bytes into memory")
        
        print()
        
    except Exception as e:
        print(f"   ❌ ERROR creating Attachable: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Link to entity
    print("5. Linking to entity...")
    try:
        # Create entity reference
        entity_ref = Ref()
        entity_ref.type = ENTITY_TYPE
        entity_ref.value = ENTITY_ID
        
        # Create attachable reference
        attachable_ref = AttachableRef()
        attachable_ref.EntityRef = entity_ref
        
        # Add to attachment
        attachment.AttachableRef = [attachable_ref]
        
        print(f"   ✓ Linking to {ENTITY_TYPE} ID: {ENTITY_ID}")
        print()
        
    except Exception as e:
        print(f"   ❌ ERROR creating entity reference: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Upload the attachment
    print("6. Uploading to QuickBooks...")
    try:
        # Intercept the response to see what we're getting back
        import json as json_lib
        
        # Make the request manually to see the raw response
        from quickbooks.objects.attachable import Attachable as AttachableClass
        
        # Get the upload URL
        url = client.api_url + "/company/{0}/upload".format(client.company_id)
        
        # Prepare the multipart data
        metadata = {
            "FileName": attachment.FileName,
            "AttachableRef": [
                {
                    "EntityRef": {
                        "type": ENTITY_TYPE,
                        "value": ENTITY_ID
                    }
                }
            ]
        }
        
        files = {
            'file_metadata_01': (None, json_lib.dumps(metadata), 'application/json'),
            'file_content_01': (file_path.name, open(file_path, 'rb'), 'application/pdf')
        }
        
        headers = {'Authorization': 'Bearer ' + client.access_token}
        
        print(f"   Sending to: {url}")
        
        response = client.session.post(url, headers=headers, files=files)
        
        print(f"   Response Status: {response.status_code}")
        print()
        
        # Print raw response
        print("   Raw Response:")
        try:
            response_json = response.json()
            print(json_lib.dumps(response_json, indent=6))
        except:
            print(response.text)
        print()
        
        # Check for success
        if response.status_code == 200:
            response_data = response.json()
            
            if "AttachableResponse" in response_data:
                attachable_response = response_data["AttachableResponse"][0]
                
                if "Fault" in attachable_response:
                    fault = attachable_response["Fault"]
                    print("=" * 80)
                    print("❌ UPLOAD FAILED - QuickBooks returned a fault")
                    print("=" * 80)
                    print(f"Fault Type: {fault.get('type')}")
                    for error in fault.get('Error', []):
                        print(f"Error Code: {error.get('code')}")
                        print(f"Message: {error.get('Message')}")
                        print(f"Detail: {error.get('Detail')}")
                    print()
                    return False
                    
                elif "Attachable" in attachable_response:
                    attachable_obj = attachable_response["Attachable"]
                    print("=" * 80)
                    print("✅ UPLOAD SUCCESSFUL!")
                    print("=" * 80)
                    print(f"Attachable ID: {attachable_obj.get('Id')}")
                    print(f"File Name: {attachable_obj.get('FileName')}")
                    print(f"File Size: {attachable_obj.get('Size', 0):,} bytes")
                    print(f"Content Type: {attachable_obj.get('ContentType')}")
                    if 'AttachableRef' in attachable_obj:
                        print(f"Linked to: {len(attachable_obj['AttachableRef'])} transaction(s)")
                        for ref in attachable_obj['AttachableRef']:
                            entity_ref = ref.get('EntityRef', {})
                            print(f"   - {entity_ref.get('type')} ID: {entity_ref.get('value')}")
                    print()
                    return True
        else:
            print("=" * 80)
            print(f"❌ REQUEST FAILED - HTTP {response.status_code}")
            print("=" * 80)
            return False
        
        print("   ✓ Upload request sent")
        print()
        
        # Print result
        print("7. Upload Result:")
        print("=" * 80)
        print("✅ UPLOAD SUCCESSFUL!")
        print("=" * 80)
        
        if hasattr(attachment, 'Id') and attachment.Id:
            print(f"Attachable ID: {attachment.Id}")
        
        if hasattr(attachment, 'FileName'):
            print(f"File Name: {attachment.FileName}")
        
        if hasattr(attachment, 'Size'):
            print(f"File Size: {attachment.Size:,} bytes")
        
        if hasattr(attachment, 'ContentType'):
            print(f"Content Type: {attachment.ContentType}")
        
        if hasattr(attachment, 'AttachableRef') and attachment.AttachableRef:
            print(f"Linked to: {len(attachment.AttachableRef)} transaction(s)")
            for ref in attachment.AttachableRef:
                if hasattr(ref, 'EntityRef') and ref.EntityRef:
                    entity = ref.EntityRef
                    print(f"   - {entity.type} ID: {entity.value}")
        
        # Print raw object data for debugging
        print()
        print("Raw Attachment Object:")
        try:
            # Convert to dict if possible
            if hasattr(attachment, 'to_json'):
                print(attachment.to_json())
            else:
                print(json.dumps(attachment.__dict__, indent=2, default=str))
        except:
            print(str(attachment))
        
        print()
        return True
        
    except Exception as e:
        print("=" * 80)
        print("❌ UPLOAD FAILED")
        print("=" * 80)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print()
        
        # Check if it's a QuickBooks API error with details
        if hasattr(e, 'message'):
            print(f"API Message: {e.message}")
        if hasattr(e, 'detail'):
            print(f"API Detail: {e.detail}")
        if hasattr(e, 'code'):
            print(f"API Code: {e.code}")
        
        # Print full traceback
        print()
        print("Full Traceback:")
        import traceback
        traceback.print_exc()
        print()
        
        return False


def main():
    """Main entry point"""
    try:
        success = upload_receipt_sdk()
        
        if success:
            print("\n🎉 Test completed successfully!")
            return 0
        else:
            print("\n⚠️  Test failed. Review the output above for details.")
            return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ UNEXPECTED ERROR IN MAIN")
        print("=" * 80)
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
