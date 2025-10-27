"""
Test Microsoft Graph Permissions
This script checks what permissions your app has
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from msgraph_integration.services import GraphService


def test_permissions():
    """Test what Microsoft Graph permissions are available"""
    print("Testing Microsoft Graph API Permissions...")
    print("-" * 70)
    
    service = GraphService()
    
    # Test 1: Get access token
    print("\n1. Testing authentication...")
    try:
        token = service._get_access_token()
        print("   ✅ Successfully obtained access token")
        print(f"   Token: {token[:30]}...")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return
    
    # Test 2: Try to get organization info (usually works with basic permissions)
    print("\n2. Testing organization access...")
    try:
        org_endpoint = "/organization"
        org_data = service._make_request(org_endpoint)
        print("   ✅ Can access organization info")
        if org_data.get('value'):
            org_name = org_data['value'][0].get('displayName', 'Unknown')
            print(f"   Organization: {org_name}")
    except Exception as e:
        print(f"   ❌ Cannot access organization: {e}")
    
    # Test 3: Try to list users
    print("\n3. Testing user list access (requires User.Read.All)...")
    try:
        users = service.list_users(top=1)
        print("   ✅ Can list users")
        print(f"   Found {len(users.get('value', []))} user(s)")
    except Exception as e:
        error_msg = str(e)
        if '403' in error_msg:
            print("   ❌ Permission denied (403 Forbidden)")
            print("   → App needs 'User.Read.All' application permission")
        else:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Try to get application info
    print("\n4. Testing application info access...")
    try:
        app_endpoint = "/applications"
        app_data = service._make_request(app_endpoint)
        print("   ✅ Can access applications")
    except Exception as e:
        error_msg = str(e)
        if '403' in error_msg:
            print("   ❌ Permission denied (403 Forbidden)")
            print("   → App needs 'Application.Read.All' permission")
        else:
            print(f"   ❌ Error: {e}")
    
    # Test 5: Try to get service principals
    print("\n5. Testing service principal access...")
    try:
        sp_endpoint = "/servicePrincipals"
        sp_data = service._make_request(sp_endpoint)
        print("   ✅ Can access service principals")
    except Exception as e:
        error_msg = str(e)
        if '403' in error_msg:
            print("   ❌ Permission denied (403 Forbidden)")
        else:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nYour app needs the following permissions to use all features:")
    print("\n📋 Required Application Permissions (in Azure Portal):")
    print("   1. User.Read.All - Read all users' profiles")
    print("   2. Directory.Read.All - Read directory data (optional)")
    print("\n🔧 How to add permissions:")
    print("   1. Go to: https://portal.azure.com")
    print("   2. Navigate to: Azure Active Directory → App registrations")
    print("   3. Find your app: 70810155-f32c-46f6-8159-1618ea380966")
    print("   4. Click: API permissions → Add a permission")
    print("   5. Choose: Microsoft Graph → Application permissions")
    print("   6. Search and add: User.Read.All")
    print("   7. IMPORTANT: Click 'Grant admin consent' button!")
    print("\n⚠️  Note: Admin consent is required for application permissions")
    print("=" * 70)


if __name__ == "__main__":
    test_permissions()
