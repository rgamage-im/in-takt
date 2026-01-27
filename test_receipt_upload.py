#!/usr/bin/env python3
"""
QuickBooks Receipt Upload Test Script
Self-contained script to test receipt upload and linking to a Purchase transaction.
Can be used for troubleshooting and sharing with Intuit support.
"""

import requests
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# QuickBooks API Configuration
REALM_ID = "9341455122564664"  # Company ID from QuickBooks
ACCESS_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwieC5vcmciOiJIMCJ9..IoojxH6j3X0WbRqgsFtJhA.1joSUgn9nm1KmfE_NF3CGJNzzc1T6EFiifDCeHHw8tL5G2L_ZFvb-OrSTiSd4J6ZFOfEUL86axQ7NRT1b5ukXrYWBfjjLfxpBvPHNrn_CdW-hckU2Y3VZTfWtJyPKy9bfsn-Sk4i8NOZ_Ctv_IXx9x2RM4WFPFiEt33hQwhviDgmkwmVj7vMfGjhEXny0n_228rrjfh64OmEtzKlXm-Y_TeZGfRVPvgMx99IWZDTjWrzMKqeigq1cQga7nSjTZULzuvtwDyFT3Ig-OiRJPzIH3qhcP7A-fuW35Ert9-jnMNFUxlKW6VXm6Z2PZjncalPkBcyBgifZD1nLfJC_xWN65Mterxn7NRhCzFzpOspHqE-cdcJ3gOh27x_UijvuWtucyo2FYzq7tLo-UpI6lpjPe_Evj_Jl_-Iaukx5hbWrkLAu0fr_ecL_IjBx5CG0gxkKFl925mpljPdk-KypDunmvr80V224DgH8y2M0afD1Rg.CmSt3Rv7MymKDUiiHFwzIQ"  # OAuth 2.0 Access Token
BASE_URL = "https://sandbox-quickbooks.api.intuit.com"  # Use sandbox or production URL

# Transaction to link the receipt to
ENTITY_TYPE = "Purchase"  # Can be: Purchase, Bill, Expense, Vendor, etc.
ENTITY_ID = "131"  # The ID of the transaction to attach to

# File to upload
FILE_PATH = "docs/Test 1.pdf"  # Path to the PDF file

# ============================================================================
# SCRIPT LOGIC - DO NOT MODIFY UNLESS NEEDED
# ============================================================================

def upload_receipt():
    """
    Upload a receipt to QuickBooks using the all-in-one upload and link method.
    """
    
    print("=" * 80)
    print("QuickBooks Receipt Upload Test")
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
    
    # Prepare the upload
    print("3. Preparing upload request...")
    
    # Construct the upload endpoint
    upload_url = f"{BASE_URL}/v3/company/{REALM_ID}/upload"
    print(f"   URL: {upload_url}")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    print(f"   Headers: {json.dumps({k: v[:50] + '...' if len(v) > 50 else v for k, v in headers.items()}, indent=6)}")
    
    # Prepare metadata
    metadata = {
        "FileName": file_path.name,
        "ContentType": "application/pdf",
        "AttachableRef": [
            {
                "EntityRef": {
                    "type": ENTITY_TYPE,
                    "value": ENTITY_ID
                }
            }
        ]
    }
    metadata_json = json.dumps(metadata)
    print(f"   Metadata: {json.dumps(metadata, indent=6)}")
    print()
    
    # Prepare files for multipart upload
    print("4. Reading file content...")
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        print(f"   ✓ Read {len(file_content):,} bytes")
    except Exception as e:
        print(f"   ❌ ERROR reading file: {e}")
        return False
    print()
    
    # Prepare multipart form data
    files = {
        'file_metadata_01': (None, metadata_json, 'application/json'),
        'file_content_01': (file_path.name, file_content, 'application/pdf')
    }
    
    print("5. Sending request to QuickBooks...")
    print(f"   Uploading to: {upload_url}")
    print()
    
    try:
        # Send the request
        response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            timeout=60
        )
        
        # Print response details
        print("6. Response received:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for key, value in response.headers.items():
            print(f"      {key}: {value}")
        print()
        
        # Print response body
        print("   Response Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=6))
        except:
            print(f"      {response.text}")
        print()
        
        # Check for success
        if response.status_code == 200:
            response_data = response.json()
            
            # Check for faults in the response
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
                    attachable = attachable_response["Attachable"]
                    print("=" * 80)
                    print("✅ UPLOAD SUCCESSFUL!")
                    print("=" * 80)
                    print(f"Attachable ID: {attachable.get('Id')}")
                    print(f"File Name: {attachable.get('FileName')}")
                    print(f"File Size: {attachable.get('Size', 0):,} bytes")
                    print(f"Content Type: {attachable.get('ContentType')}")
                    if 'AttachableRef' in attachable:
                        print(f"Linked to: {len(attachable['AttachableRef'])} transaction(s)")
                        for ref in attachable['AttachableRef']:
                            entity_ref = ref.get('EntityRef', {})
                            print(f"   - {entity_ref.get('type')} ID: {entity_ref.get('value')}")
                    print()
                    return True
        else:
            print("=" * 80)
            print(f"❌ REQUEST FAILED - HTTP {response.status_code}")
            print("=" * 80)
            return False
            
    except requests.exceptions.Timeout:
        print("=" * 80)
        print("❌ REQUEST TIMEOUT")
        print("=" * 80)
        print("The request took too long to complete (>60 seconds)")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print("=" * 80)
        print("❌ CONNECTION ERROR")
        print("=" * 80)
        print(f"Could not connect to QuickBooks API: {e}")
        return False
        
    except Exception as e:
        print("=" * 80)
        print("❌ UNEXPECTED ERROR")
        print("=" * 80)
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = upload_receipt()
    
    if success:
        print("\n🎉 Test completed successfully!")
        return 0
    else:
        print("\n⚠️  Test failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())
